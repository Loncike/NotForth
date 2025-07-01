from string import ascii_letters, digits
import operator, sys, os, subprocess
import ctypes, ctypes.util
from dataclasses import dataclass
from enum import Enum, auto
## stuff for syscall
libc = ctypes.CDLL(None)
syscall_fn = libc.syscall


class TokenType(Enum):
    BUILTINWORD = auto()
    INDEX = auto()
    NUMBER  = auto()
    POINTER = auto()
    WORD = auto()
    STRING = auto()
    LOGICOP = auto()

@dataclass
class Loc:
    line: int
    file: str

@dataclass
class Token:
    type: TokenType
    value: str|int
    loc: Loc

@dataclass
class Macro:
    tokens: list
    argumentsIdx: dict

builtinwords = ["store", "add", "sub", "jumpif", "jump", "syscallargs", "syscall", "macro", "include", "end", "label", "printnum"]

def lexFile(filePath):
    with open(filePath, "r", encoding="utf-8") as f:
        file = f.read()
        i = 0
        line = 1
        tokens = []
        while i < len(file):
            if file[i] == ";": 
                while file[i] != "\n":
                    i+=1
            elif file[i] in ascii_letters:
                s = file[i]
                i+=1
                while file[i] in ascii_letters + "_-":
                    s += file[i]
                    i+=1
                if s in builtinwords: 
                    tokens.append(Token(TokenType.BUILTINWORD, s, Loc(line, filePath)))
                else:
                    tokens.append(Token(TokenType.WORD, s, Loc(line, filePath)))
            elif file[i] in "<>=!":
                s = file[i]
                if file[i+1] in "<>=": 
                    s += file[i+1] 
                    i+=1
                tokens.append(Token(TokenType.LOGICOP, s, Loc(line, filePath)))
            elif file[i] == "$":
                i+=1
                s = ""
                while file[i] in digits:
                    s += file[i] 
                    i+=1
                tokens.append(Token(TokenType.NUMBER, int(s), Loc(line, filePath)))
            elif file[i] == "@":
                i+=1
                s = ""
                while file[i] in digits:
                    s += file[i] 
                    i+=1
                tokens.append(Token(TokenType.POINTER, int(s), Loc(line, filePath)))
            elif file[i] in digits:
                s = ""
                while file[i] in digits:
                    s+= file[i]
                    i+=1
                tokens.append(Token(TokenType.INDEX, int(s), Loc(line, filePath)))
            elif file[i] == '"':
                i+=1
                s = ""
                while file[i] != '"':
                    s+=file[i]
                    i+=1
                tokens.append(Token(TokenType.STRING, s, Loc(line, filePath)))
            if file[i] == "\n": 
                line+=1
            i+=1 
    return list(reversed(tokens))

## TODO: error handling
def preProcess(tokens, macros={}): 
    includedFiles = set()

    program = [] 
    macros = {}
    labels = {}
    while tokens:
        token = tokens.pop()
        if token.type == TokenType.BUILTINWORD and token.value == "macro":
            macroName = tokens.pop().value
            macroArgsIdx = {}

            counter = 0
            while tokens and tokens[-1].type == TokenType.WORD and not (tokens[-1].value in labels and tokens[-1].value in macros):
                arg = tokens.pop().value
                macroArgsIdx[arg] = counter
                counter+=1
            body = []
            while tokens and not (tokens[-1].type == TokenType.BUILTINWORD and tokens[-1].value == "end"):
                body.append(tokens.pop())

            if tokens and tokens[-1].value == "end":
                tokens.pop()
            else: 
                raise Exception(f"Expected 'end' for closing macro: {macroName}")
            
            macros[macroName] = Macro(body, macroArgsIdx)

        elif token.type == TokenType.BUILTINWORD and token.value == "label":
            labelName = tokens.pop()
            if labelName.type == TokenType.WORD:
                labels[labelName.value] = len(program)+1
            else: 
                raise Exception(f"Expected string for the name of the label, got: {labelName.type} with the value of {labelName.value}")
        ##elif token.type == TokenType.WORD and token.value in labels:
        elif token.type == TokenType.WORD and token.value in macros:
            macroName = token.value
            macro = macros[macroName]

            args = []
            for _ in macro.argumentsIdx:
                if not tokens and tokens[-1].type != TokenType.INDEX and tokens[-1].type != TokenType.NUMBER and tokens[-1].type != TokenType.POINTER:
                    raise Exception(f"Not enough arguments for macro: {macroName}")
                args.append(tokens.pop())

            replacedTokens = []
            for t in macro.tokens:
                if t.type == TokenType.WORD and t.value in macro.argumentsIdx:
                    replacedTokens.append(args[macro.argumentsIdx[t.value]])
                else:
                    replacedTokens.append(t)
            tokens.extend(list(reversed(replacedTokens)))
        elif token.type == TokenType.BUILTINWORD and token.value == "include":
            path = tokens.pop()
            if path.type != TokenType.STRING: raise Exception(f"Expected file path as string after include, got: {path.type}")
            if path.value in includedFiles: raise Exception(f"Recursive include")
            includedFiles.add(path.value)
            tokens.extend(lexFile(path.value))
        else: 
            program.append(token)

    
    return program, labels

class Interpreter():
    def __init__(self, p, l):
        self.Program = p
        self.Labels = l
        self.Mem = [0] * 64
        self.SYSCALLS = {
                0: ["uint", "mem_out", "size_t"],
                1: ["uint", "mem_in", "size_t"],
                60: ["int"]

                }
        self.MAXARGS = 6
        self.LogicOps = {
                "==": operator.eq,
                "!=": operator.ne,
                "<": operator.lt,
                "<=": operator.le,
                ">": operator.gt,
                ">=": operator.ge,
                }
    
    def CheckMemory(self, idx):
        if len(self.Mem)-1 < idx:
            self.Mem.extend([0] * (idx - len(self.Mem) + 1))

    def convertArgs(self, syscall, args):
        retArgs = []
        temp = {}
        for i in range(len(args)):
            if self.SYSCALLS[syscall][i] == "uint":
                n = 0
                if args[i].type == TokenType.INDEX:
                    n = self.Mem[args[i].value] 
                elif args[i].type == TokenType.POINTER:
                    n = self.Mem[self.Mem[args[i].value]]
                else: 
                    n = args[i].value

                retArgs.append(ctypes.c_uint(n))
            elif self.SYSCALLS[syscall][i] == "mem_in":
                offset = 0
                if args[i].type == TokenType.NUMBER:
                    print("Expected Index or Pointer, got Number")
                    exit(1)
                elif args[i].type == TokenType.INDEX:
                    offset = args[i].value
                elif args[i].type == TokenType.POINTER:
                    offset = self.Mem[args[i].value]

                length = 0
                if args[i+1].type == TokenType.INDEX:
                    length = self.Mem[args[i+1].value] 
                elif args[i+1].type == TokenType.POINTER:
                    length = self.Mem[self.Mem[args[i+1].value]]
                else: 
                    length = args[i+1].value
                buf = (ctypes.c_ubyte * length)(*self.Mem[offset:offset + length])
                retArgs.append(ctypes.cast(buf, ctypes.c_void_p))
            elif self.SYSCALLS[syscall][i] == "mem_out":
                offset = 0
                if args[i].type == TokenType.NUMBER:
                    print("Expected Index or Pointer, got Number")
                    exit(1)
                elif args[i].type == TokenType.INDEX:
                    offset = args[i].value
                elif args[i].type == TokenType.POINTER:
                    offset = self.Mem[args[i].value]

                length = 0
                if args[i+1].type == TokenType.INDEX:
                    length = self.Mem[args[i+1].value] 
                elif args[i+1].type == TokenType.POINTER:
                    length = self.Mem[self.Mem[args[i+1].value]]
                else: 
                    length = args[i+1].value
                buf = ctypes.create_string_buffer(length)
                retArgs.append(ctypes.cast(buf, ctypes.c_void_p))
                temp['buf'] = buf
                temp['offset'] = offset
            elif self.SYSCALLS[syscall][i] == "size_t":
                n = 0
                if args[i].type == TokenType.INDEX:
                    n = self.Mem[args[i].value] 
                elif args[i].type == TokenType.POINTER:
                    n = self.Mem[self.Mem[args[i].value]]
                else: 
                    n = args[i].value

                retArgs.append(ctypes.c_size_t(n))
        return retArgs, temp


    def copy_c_void_p_to_mem(self, ptr, length, offset):
        byte_ptr = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte * length))
        for i in range(length):
            self.CheckMemory(offset+i)
            self.Mem[offset + i] = byte_ptr.contents[i]

    def doSyscall(self, syscall, args): 
        c_args, extra = self.convertArgs(syscall, args) 

        while len(c_args) < self.MAXARGS:
            c_args.append(ctypes.c_int(0))

        res = syscall_fn(syscall, *c_args)

        if 'buf' in extra:
            ptr = ctypes.cast(extra['buf'], ctypes.c_void_p)
            self.copy_c_void_p_to_mem(ptr, res, extra['offset'])


        return res

    def Store(self, t1, t2):
        self.CheckMemory(t1.value)
        if t2.type == TokenType.INDEX:
            self.Mem[t1.value] = self.Mem[t2.value]
        else:
            self.Mem[t1.value] = t2.value

    def Add(self, t1, t2, t3):
        n1, n2 = 0, 0
        if t1.type == TokenType.INDEX:
            self.CheckMemory(t1.value)
            n1 = self.Mem[t1.value] 
        elif t1.type == TokenType.POINTER:
            n1 = self.Mem[self.Mem[t1.value]]
        else: 
            n1 = t1.value

        if t2.type == TokenType.INDEX:
            self.CheckMemory(t2.value)
            n2 = self.Mem[t2.value] 
        elif t2.type == TokenType.POINTER:
            n2 = self.Mem[self.Mem[t2.value]]
        else: 
            n2 = t2.value

        if t3.type == TokenType.INDEX:
            self.CheckMemory(t3.value)
            self.Mem[t3.value] = n1 + n2
        elif t3.type == TokenType.POINTER:
            self.Mem[self.Mem[t3.value]] = n1 + n2

    def Sub(self, t1, t2, t3):
        n1, n2 = 0, 0
        if t1.type == TokenType.INDEX:
            self.CheckMemory(t1.value)
            n1 = self.Mem[t1.value] 
        elif t1.type == TokenType.POINTER:
            n1 = self.Mem[self.Mem[t1.value]]
        else: 
            n1 = t1.value

        if t2.type == TokenType.INDEX:
            self.CheckMemory(t2.value)
            n2 = self.Mem[t2.value] 
        elif t2.type == TokenType.POINTER:
            n2 = self.Mem[self.Mem[t2.value]]
        else: 
            n2 = t2.value

        if t3.type == TokenType.INDEX:
            self.CheckMemory(t3.value)
            self.Mem[t3.value] = n1 - n2
        elif t3.type == TokenType.POINTER:
            self.Mem[self.Mem[t3.value]] = n1 - n2


    def JumpIf(self, t1, op, t2) -> bool:
        n1, n2 = 0, 0
        if t1.type == TokenType.INDEX:
            n1 = self.Mem[t1.value] 
        elif t1.type == TokenType.POINTER:
            n1 = self.Mem[self.Mem[t1.value]]
        else: 
            n1 = t1.value

        if t2.type == TokenType.INDEX:
            n2 = self.Mem[t2.value] 
        elif t2.type == TokenType.POINTER:
            n2 = self.Mem[self.Mem[t2.value]]
        else: 
            n2 = t2.value
        
        try:
            return self.LogicOps[op.value](n1, n2)
        except:
            print(f"Undefined logic op: {op.value}")

    def Run(self, debug=False):
        ip = 0
        while ip < len(self.Program):

            print(self.Program[ip]) if debug else None
            if self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "store":
                self.Store(self.Program[ip+1], self.Program[ip+2])
                ip+=2
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "add":
                self.Add(self.Program[ip+1], self.Program[ip+2], self.Program[ip+3])
                ip+=3
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "sub":
                self.Sub(self.Program[ip+1], self.Program[ip+2], self.Program[ip+3])
                ip+=3
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "jumpif":
                if self.JumpIf(self.Program[ip+1], self.Program[ip+2], self.Program[ip+3]):
                    ip = self.Labels[self.Program[ip+4].value]
                    continue
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "jump":
                    ip = self.Labels[self.Program[ip+1].value]-1
                    continue
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "syscall":
                    ip+=1
                    syscallNum = self.Program[ip].value
                    ip+=1
                    args = []
                    while ip < len(self.Program) and self.Program[ip].type in [TokenType.INDEX, TokenType.NUMBER, TokenType.POINTER]:
                        args.append(self.Program[ip])
                        ip+=1
                    ip-=1
                    self.doSyscall(syscallNum, args)
            
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "printnum":
                    t1 = self.Program[ip+1]
                    n1 = 0
                    if t1.type == TokenType.INDEX:
                        n1 = self.Mem[t1.value] 
                    elif t1.type == TokenType.POINTER:
                        n1 = self.Mem[self.Mem[t1.value]]
                    else: 
                        n1 = t1.value

                    print(int(self.Mem[n1]))
                    ip+=1

            ip+=1
        print("Memory dump: ", self.Mem) if debug else None


class Compiler():
    def __init__(self, p, l, out):
        self.Program = p
        self.Labels = l
        self.SYSCALLARGUMENTSREGISTERS = ["edi", "esi", "edx", "r10d", "r8d", "r9d"]
        self.SYSCALLS = {
                0: ["uint", "mem_out", "size_t"],
                1: ["uint", "mem_in", "size_t"],
                60: ["int"]

                }
        self.outName = "./bin/"+out

    def Run(self, debug=False):
        ip = 0
        file = open(self.outName+".asm", "w", encoding="utf-8")
        file.write("format ELF64 executable 3\nentry main\nsegment readable writeable\n    mem dd 1024 dup(0)\nsegment readable executable\nprintnum:\n    mov     r9, -3689348814741910323\n    sub     rsp, 40\n    mov     byte [rsp+31], 10\n    lea     rcx, [rsp+30]\n.L2:\n    mov     rax, rdi\n    and     eax, 0xFFFFFFFF           ; mask input to 32 bits\n    lea     r8, [rsp+32]\n    mul     r9\n    mov     rax, rdi\n    and     eax, 0xFFFFFFFF           ; mask input again\n    sub     r8, rcx\n    shr     rdx, 3\n    lea     rsi, [rdx+rdx*4]\n    add     rsi, rsi\n    sub     rax, rsi\n    add     eax, 48\n    mov     byte [rcx], al\n    mov     rax, rdi\n    and     eax, 0xFFFFFFFF\n    mov     rdi, rdx\n    mov     rdx, rcx\n    sub     rcx, 1\n    cmp     rax, 9\n    ja      .L2\n    lea     rax, [rsp+32]\n    mov     edi, 1\n    sub     rdx, rax\n    xor     eax, eax\n    lea     rsi, [rsp+32+rdx]\n    mov     rdx, r8\n    mov     rax, 1\n    syscall\n    add     rsp, 40\n    ret\nmain:\n")
        while ip < len(self.Program):
            for k, v in  self.Labels.items():
                if v-1 == ip:
                    file.write(f"{k}:\n")

            if self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "store":
                t1 = self.Program[ip+1]
                t2 = self.Program[ip+2]
                if t2.type == TokenType.INDEX:
                    file.write(f"    mov eax, dword [mem + {t2.value}*4]\n")
                    file.write(f"    mov dword [mem + {t1.value}*4], eax\n")
                else: 
                    file.write(f"    mov dword [mem + {t1.value}*4], {t2.value}\n")
                ip+=2

            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "add":
                t1 = self.Program[ip+1]
                t2 = self.Program[ip+2]
                t3 = self.Program[ip+3]
                if t1.type == TokenType.INDEX:
                    file.write(f"    mov eax, dword [mem + {t1.value}*4]\n")
                elif t1.type == TokenType.POINTER:
                    file.write(f"    mov eax, dword [mem + {t1.value}*4]\n")
                    file.write(f"    mov eax, dword [mem + eax*4]\n")
                else: 
                    file.write(f"    mov eax, {t1.value}")

                if t2.type == TokenType.INDEX:
                    file.write(f"    mov ebx, dword [mem + {t2.value}*4]\n")
                elif t2.type == TokenType.POINTER:
                    file.write(f"    mov ebx, dword [mem + {t2.value}*4]\n")
                    file.write(f"    mov ebx, dword [mem + ebx*4]\n")
                else: 
                    file.write(f"    mov ebx, {t2.value}\n")

                file.write(f"    add eax, ebx\n")

                
                if t3.type == TokenType.INDEX:
                    file.write(f"    mov dword [mem + {t3.value}*4], eax\n")
                elif t3.type == TokenType.POINTER:
                    file.write(f"    mov ebx, dword [mem + {t3.value}*4]\n")
                    file.write(f"    mov dword [mem + ebx*4], eax\n")
                ip+=3

            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "sub":
                t1 = self.Program[ip+1]
                t2 = self.Program[ip+2]
                t3 = self.Program[ip+3]
                if t1.type == TokenType.INDEX:
                    file.write(f"    mov eax, dword [mem + {t1.value}*4]\n")
                elif t1.type == TokenType.POINTER:
                    file.write(f"    mov eax, dword [mem + {t1.value}*4]\n")
                    file.write(f"    mov eax, dword [mem + eax*4]\n")
                else: 
                    file.write(f"    mov eax, {t1.value}\n")

                if t2.type == TokenType.INDEX:
                    file.write(f"    mov ebx, dword [mem + {t2.value}*4]\n")
                elif t2.type == TokenType.POINTER:
                    file.write(f"    mov ebx, dword [mem + {t2.value}*4]\n")
                    file.write(f"    mov ebx, dword [mem + ebx*4]\n")
                else: 
                    file.write(f"    mov ebx, {t2.value}\n")

                file.write(f"    sub eax, ebx\n")

                
                if t3.type == TokenType.INDEX:
                    file.write(f"    mov dword [mem + {t3.value}*4], eax\n")
                elif t3.type == TokenType.POINTER:
                    file.write(f"    mov ebx, dword [mem + {t3.value}*4]\n")
                    file.write(f"    mov dword [mem + ebx*4], eax\n")

                ip+=3
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "jumpif":
                t1 = self.Program[ip+1]
                op = self.Program[ip+2].value
                t3 = self.Program[ip+3]
                if t1.type == TokenType.INDEX:
                    file.write(f"    mov eax, dword [mem + {t1.value}*4]\n")
                elif t1.type == TokenType.POINTER:
                    file.write(f"    mov eax, dword [mem + {t1.value}*4]\n")
                    file.write(f"    mov eax, dword [mem + eax*4]\n")
                else: 
                    file.write(f"    mov eax, {t1.value}\n")

                if t3.type == TokenType.INDEX:
                    file.write(f"    mov ebx, dword [mem + {t3.value}*4]\n")
                elif t3.type == TokenType.POINTER:
                    file.write(f"    mov ebx, dword [mem + {t3.value}*4]\n")
                    file.write(f"    mov ebx, dword [mem + ebx*4]\n")
                else: 
                    file.write(f"    mov ebx, {t2.value}\n")

                file.write(f"    cmp eax, ebx\n")
                
                if op == "==":
                    file.write(f"    je {self.Program[ip+4].value}\n")
                elif op == "!=":
                    file.write(f"    jne {self.Program[ip+4].value}\n")
                elif op == "<":
                    file.write(f"    jl {self.Program[ip+4].value}\n") ## for no less than (signed)
                elif op == "<=":
                    file.write(f"    jle {self.Program[ip+4].value}\n")
                elif op == ">":
                    file.write(f"    jg {self.Program[ip+4].value}\n")
                elif op == ">=":
                    file.write(f"    jge {self.Program[ip+4].value}\n")
                ip+=4

            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "jump":
                    file.write(f"    jmp {self.Program[ip+1].value}\n")
                    ip+=1
            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "syscall":
                    ip+=1
                    syscallNum = self.Program[ip].value
                    file.write(f"    mov eax, {syscallNum}\n")
                    ip+=1
                    args = []
                    while ip < len(self.Program) and self.Program[ip].type in [TokenType.INDEX, TokenType.NUMBER, TokenType.POINTER]:
                        args.append(self.Program[ip])
                        ip+=1
                    ip-=1
                    for i in range(len(args)):
                        if args[i].type == TokenType.INDEX:
                            file.write(f"    lea {self.SYSCALLARGUMENTSREGISTERS[i]}, [mem + {args[i].value}*4]\n")
                        elif args[i].type == TokenType.POINTER:
                            file.write(f"    mov {self.SYSCALLARGUMENTSREGISTERS[i]}, dword [mem + {args[i].value}*4]\n")
                            file.write(f"    lea {self.SYSCALLARGUMENTSREGISTERS[i]}, dword [mem + {self.SYSCALLARGUMENTSREGISTERS[i]}*4]\n")
                        else: 
                            if self.SYSCALLS[syscallNum][i] in ["uint", "int"]:
                                file.write(f"    mov {self.SYSCALLARGUMENTSREGISTERS[i]}, {args[i].value}\n")
                            elif self.SYSCALLS[syscallNum][i] == "size_t":
                                file.write(f"    mov {self.SYSCALLARGUMENTSREGISTERS[i]}, {args[i].value}*4\n")

                    file.write(f"    syscall\n")

            elif self.Program[ip].type == TokenType.BUILTINWORD and self.Program[ip].value == "printnum":
                t1 = self.Program[ip+1]
                if t1.type == TokenType.INDEX:
                    file.write(f"    mov edi, dword [mem + {t1.value}*4]\n")
                elif t1.type == TokenType.POINTER:
                    file.write(f"    mov eax, dword [mem + {t1.value}*4]\n")
                    file.write(f"    mov edi, dword [mem + eax*4]\n")
                else: 
                    file.write(f"    mov edi, {t1.value}\n")
                
                file.write(f"    call printnum\n")
                ip+=1

            ip+=1
        file.write("    mov rax, 60\n    syscall") 


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "help":
        print("Compile: python main.py com <dest to file> | Compiled elf64 file will be in ./bin")
        print("Interpret: python main.py int <dest to file> <*debug> | Debug is an optionnal flag")
        exit(0)
    program, labels = preProcess(lexFile(sys.argv[2]))
    if mode == "int":
        inter = Interpreter(program, labels)
        if len(sys.argv) > 3 and sys.argv[3] == "debug":
            inter.Run(True)
        else:
            inter.Run(False)
    elif mode == "com":
        if not os.path.exists("./bin"):
            os.makedirs("./bin")
        fileName = sys.argv[2].split("/")[-1][:-3]
        comp = Compiler(program, labels, fileName)
        comp.Run()
        result = subprocess.run(["fasm", "./bin/"+fileName+".asm"], capture_output=True, text=True)
        if result.returncode != 0:
            print("ERROR:", result.stderr)
        os.remove("./bin/"+fileName+".asm")
    
