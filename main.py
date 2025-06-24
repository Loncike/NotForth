import operator, sys
from dataclasses import dataclass
from enum import Enum
import ctypes
import ctypes.util

libc = ctypes.CDLL(None)
syscall_fn = libc.syscall

# mem_out writes to Mem
# mem_in reads from Mem
SYSCALLS = {
        0: ["uint", "mem_out", "size_t"],
        1: ["uint", "mem_in", "size_t"],
        60: ["int"]

        }
MAXARGS = 6
Mem = [0] * 1000
def CheckMem(idx):
    if len(Mem)-1 < int(idx):
        for i in range((int(idx) - len(Mem)) + 1):
            Mem.append(0)



def convertArgs(syscall, args):
    retArgs = []
    temp = {}
    for i in range(len(args)):
        if SYSCALLS[syscall][i] == "uint":
            retArgs.append(ctypes.c_uint(args[i]))
        elif SYSCALLS[syscall][i] == "mem_in":
            offset = args[i]
            length = args[i + 1]
            buf = (ctypes.c_ubyte * length)(*Mem[offset:offset + length])
            retArgs.append(ctypes.cast(buf, ctypes.c_void_p))
        elif SYSCALLS[syscall][i] == "mem_out":
            offset = args[i]
            length = args[i + 1]
            buf = ctypes.create_string_buffer(length)
            retArgs.append(ctypes.cast(buf, ctypes.c_void_p))
            temp['buf'] = buf
            temp['offset'] = offset
        elif SYSCALLS[syscall][i] == "size_t":
            retArgs.append(ctypes.c_size_t(args[i]))
    return retArgs, temp


def copy_c_void_p_to_mem(ptr, length, offset):
    byte_ptr = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte * length))
    for i in range(length):
        CheckMem(offset+i)
        Mem[offset + i] = byte_ptr.contents[i]

def doSyscall(syscall, args):
    c_args, extra = convertArgs(syscall, args) 

    while len(c_args) < MAXARGS:
        c_args.append(ctypes.c_int(0))

    res = syscall_fn(syscall, *c_args)

    if 'buf' in extra:
        ptr = ctypes.cast(extra['buf'], ctypes.c_void_p)
        copy_c_void_p_to_mem(ptr, res, extra['offset'])


    return res

logicOps = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

class TokenType(Enum):
    NUMBER = 1
    POINTER= 2
    INDEX = 3
    OP = 4
    LOGICOP = 5
    LABEL = 6
    INITLABEL = 7

@dataclass
class Token:
    type: TokenType
    data: int | None | str | list

@dataclass
class Macro:
    tokens: list

def Add(t1, t2, t3):
    n1, n2 = 0, 0
    if t1.type == TokenType.INDEX:
        n1 = Mem[t1.data] 
    elif t1.type == TokenType.POINTER:
        n1 = Mem[Mem[t1.data]]
    else: 
        n1 = t1.data

    if t2.type == TokenType.INDEX:
        n2 = Mem[t2.data] 
    elif t2.type == TokenType.POINTER:
        n2 = Mem[Mem[t2.data]]
    else: 
        n2 = t2.data
    
    if t3.type == TokenType.INDEX:
        Mem[t3.data] = n1 + n2
    elif t3.type == TokenType.POINTER:
        Mem[Mem[t3.data]] = n1 + n2
 
def Sub(t1, t2, t3):
    n1, n2 = 0, 0
    if t1.type == TokenType.INDEX:
        n1 = Mem[t1.data] 
    elif t1.type == TokenType.POINTER:
        n1 = Mem[Mem[t1.data]]
    else: 
        n1 = t1.data

    if t2.type == TokenType.INDEX:
        n2 = Mem[t2.data] 
    elif t2.type == TokenType.POINTER:
        n2 = Mem[Mem[t2.data]]
    else: 
        n2 = t2.data
    
    if t3.type == TokenType.INDEX:
        Mem[t3.data] = n1 - n2
    elif t3.type == TokenType.POINTER:
        Mem[Mem[t3.data]] = n1 - n2
 
def Store(t1, t2):
    Mem[t1.data] = Mem[t2.data] if t2.type == TokenType.INDEX else t2.data

def JumpIf(t1, op, t2) -> bool:
    n1, n2 = 0, 0
    if t1.type == TokenType.INDEX:
        n1 = Mem[t1.data] 
    elif t1.type == TokenType.POINTER:
        n1 = Mem[Mem[t1.data]]
    else: 
        n1 = t1.data

    if t2.type == TokenType.INDEX:
        n2 = Mem[t2.data] 
    elif t2.type == TokenType.POINTER:
        n2 = Mem[Mem[t2.data]]
    else: 
        n2 = t2.data
    
    return logicOps[op.data](n1, n2)

def runProgram(tokens, labels):
    head = 0
    syscallargsN = 0
    while head < len(tokens):
        #input("...")
        #print(tokens[head], tokens[head+1], tokens[head+2], end=" ")
        if tokens[head].type != TokenType.OP and tokens[head].type != TokenType.INITLABEL: 
            print("ERROR")
            print(tokens)
            print(head, tokens[head])
            exit(1)
        if tokens[head].data == "store":
            CheckMem(tokens[head+1].data)
            if tokens[head+2].type == TokenType.INDEX: CheckMem(tokens[head+2].data)
            Store(tokens[head+1], tokens[head+2])
            head+=2
        elif tokens[head].data == "add":
            if tokens[head+1].type == TokenType.INDEX: CheckMem(tokens[head+1].data)
            if tokens[head+2].type == TokenType.INDEX: CheckMem(tokens[head+2].data)
            if tokens[head+3].type == TokenType.INDEX: CheckMem(tokens[head+3].data)
            Add(tokens[head+1], tokens[head+2], tokens[head+3])
            head+=3
        elif tokens[head].data == "sub":
            if tokens[head+3].type == TokenType.INDEX: CheckMem(tokens[head+3].data)
            if tokens[head+2].type == TokenType.INDEX: CheckMem(tokens[head+2].data)
            if tokens[head+3].type == TokenType.INDEX: CheckMem(tokens[head+3].data)
            Sub(tokens[head+1], tokens[head+2], tokens[head+3])
            head+=3
        elif tokens[head].data == "jumpif":
            if JumpIf(tokens[head+1], tokens[head+2], tokens[head+3]): 
                head = labels[tokens[head+4].data]
                continue
            head+=4
        elif tokens[head].data == "jump":
            head = labels[tokens[head+1].data]
        elif tokens[head].data == "storepos":
            CheckMem(tokens[head+1].data)
            Store(tokens[head+1], Token(TokenType.NUMBER, head))
            head+=1
        elif tokens[head].data == "jumppos":
            head = Mem[tokens[head+1].data]+4 

        elif tokens[head].data == "syscallargs":
            syscallargsN = tokens[head+1].data
            head+=1
        elif tokens[head].data == "syscall":
            syscallNum = tokens[head+1].data
            args = []
            for i in range(1, syscallargsN):
                    args.append(tokens[head+i+1].data)
            ##Mem[head+1].data = TODO implament return 
            doSyscall(syscallNum, args)
            head+=syscallargsN


        #print(Mem[:30], "\n")
        head+=1
    print("Memory dump:", Mem[:30])

def loadProgram(file) -> str:
    with open(file, "r", encoding="utf-8") as f:
        return f.read().split("\n")

def GenerateTokens(program, macros={}) -> list:
    tokens = []
    macros = macros
    syscallargsN = 0
    program = iter(program)
    for p in program:
        p = p.lower().split(" ")

        if p[0] in macros:
            for t in macros[p[0]].tokens:
                tokens.append(t)

        elif p[0] == "store":
            tokens.append(Token(TokenType.OP, "store"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))
            if p[2][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[2][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[2])))
        elif p[0] == "add":
            tokens.append(Token(TokenType.OP, "add"))
            if p[1][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[1][1:])))
            elif p[1][0] == "@": 
                tokens.append(Token(TokenType.POINTER, int(p[1][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[1])))
            if p[2][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[2][1:])))
            elif p[2][0] == "@": 
                tokens.append(Token(TokenType.POINTER, int(p[2][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[2])))
            if p[3][0] == "@": 
                tokens.append(Token(TokenType.POITER, int(p[3][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[3])))

        elif p[0] == "sub":
            tokens.append(Token(TokenType.OP, "sub"))
            if p[1][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[1][1:])))
            elif p[1][0] == "@": 
                tokens.append(Token(TokenType.POINTER, int(p[1][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[1])))
            if p[2][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[2][1:])))
            elif p[2][0] == "@": 
                tokens.append(Token(TokenType.POINTER, int(p[2][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[2])))
            if p[3][0] == "@": 
                tokens.append(Token(TokenType.POINTER, int(p[3][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[3])))


        elif p[0] == "jumpif":
            tokens.append(Token(TokenType.OP, "jumpif"))
            if p[1][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[1][1:])))
            elif p[1][0] == "@": 
                tokens.append(Token(TokenType.POINTER, int(p[1][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[1])))     
            tokens.append(Token(TokenType.LOGICOP, p[2]))
            if p[3][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[3][1:])))
            elif p[3][0] == "@": 
                tokens.append(Token(TokenType.POINTER, int(p[3][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[3])))
            tokens.append(Token(TokenType.LABEL, p[4]))

        elif p[0] == "jump":
            tokens.append(Token(TokenType.OP, "jump"))
            tokens.append(Token(TokenType.LABEL, p[1]))

        elif p[0] == "label":
            tokens.append(Token(TokenType.INITLABEL, p[1]))
        
        elif p[0] == "syscallargs":
            tokens.append(Token(TokenType.OP, "syscallargs"))
            if p[1][0] == "$": tokens.append(Token(TokenType.NUMBER, int(p[1][1:])))
            syscallargsN = int(p[1][1:])
        elif p[0] == "syscall": ## TODO: Pointers
            tokens.append(Token(TokenType.OP, "syscall"))
            for i in range(syscallargsN):
                if p[i+1][0] == "$": 
                    tokens.append(Token(TokenType.NUMBER, int(p[i+1][1:])))
                else:
                    tokens.append(Token(TokenType.INDEX, int(p[i+1])))

        elif p[0] == "storepos":
            tokens.append(Token(TokenType.OP, "storepos"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))
        elif p[0] == "jumppos":
            tokens.append(Token(TokenType.OP, "jumppos"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))

        elif p[0] == "macro":
            m = p[1]
            macros[m] = Macro([])
            s = []
            while p[0] != "end":
                p = next(program, None)
                s.append(p) if p.lower().split(" ")[0] != "end" else ""
                p = p.lower().split(" ")
            macros[m].tokens = GenerateTokens(s, macros)


    return tokens

def generateLabels(tokens):
    labels = {}
    for i in range(len(tokens)):
        t = tokens[i]
        if t.type == TokenType.INITLABEL:
            labels[t.data] = i
    return labels

if __name__ == "__main__":
    program = loadProgram(sys.argv[1])
    tokens = GenerateTokens(program)
    runProgram(tokens, generateLabels(tokens))

