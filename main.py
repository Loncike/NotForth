import operator, sys
from dataclasses import dataclass
from enum import Enum

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
    INDEX = 2
    OP = 3
    LOGICOP = 4
    LABEL = 5
    INITLABEL = 6

@dataclass
class Token:
    type: TokenType
    data: int | None | str

Mem = []

def CheckMem(idx):
    if len(Mem)-1 < int(idx):
        for i in range((int(idx) - len(Mem)) + 1):
            Mem.append(0)

def Add(t1, t2, t3):
    n1 = Mem[t1.data] if t1.type == TokenType.INDEX else t1.data
    n2 = Mem[t2.data] if t2.type == TokenType.INDEX else t2.data
    Mem[t3.data] = n1 + n2

def Sub(t1, t2, t3):
    n1 = Mem[t1.data] if t1.type == TokenType.INDEX else t1.data
    n2 = Mem[t2.data] if t2.type == TokenType.INDEX else t2.data
    Mem[t3.data] = n1 - n2

def Store(t1, t2):
    Mem[t1.data] = Mem[t2.data] if t2.type == TokenType.INDEX else t2.data

def JumpIf(t1, op, t2) -> bool:
    n1 = Mem[t1.data] if t1.type == TokenType.INDEX else t1.data
    n2 = Mem[t2.data] if t2.type == TokenType.INDEX else t2.data
    return logicOps[op.data](n1, n2)

def runProgram(tokens, labels):

    head = 0
    while head < len(tokens):
        if tokens[head].type != TokenType.OP and tokens[head].type != TokenType.INITLABEL: 
            print(tokens)
            print(head, tokens[head])
            exit(1)
        if tokens[head].data == "store":
            CheckMem(tokens[head+1].data)
            if tokens[head+2].type == TokenType.INDEX: CheckMem(tokens[head+2].data)
            Store(tokens[head+1], tokens[head+2])
            head+=2
        elif tokens[head].data == "add":
            if tokens[head+3].type == TokenType.INDEX: CheckMem(tokens[head+3].data)
            Add(tokens[head+1], tokens[head+2], tokens[head+3])
            head+=3
        elif tokens[head].data == "sub":
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
        elif tokens[head].data == "print":
            CheckMem(tokens[head+1].data)
            print(Mem[tokens[head+1].data])
            head+=1
        elif tokens[head].data == "printchr":
            CheckMem(tokens[head+1].data)
            print(chr(Mem[tokens[head+1].data]))
            head+=1
        elif tokens[head].data == "input":
            CheckMem(tokens[head+1].data)
            Mem[tokens[head+1].data] = int(input())
            head+=1
        elif tokens[head].data == "inputchr":
            CheckMem(tokens[head+1].data)
            Mem[tokens[head+1].data] = int(ord(input()))
            head+=1
        elif tokens[head].data == "storepos":
            CheckMem(tokens[head+1].data)
            Store(tokens[head+1], Token(TokenType.NUMBER, head))
            head+=1
        elif tokens[head].data == "jumppos":
            head = Mem[tokens[head+1].data]+3 
        head+=1

def loadProgram(file) -> str:
    with open(file, "r", encoding="utf-8") as f:
        return f.read().split("\n")

def GenerateTokens(program) -> list:
    tokens = []
    for p in program:
        p = p.lower().split(" ")
        if p[0] == "store":
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
            else:
                tokens.append(Token(TokenType.INDEX, int(p[1])))
            if p[2][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[2][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[2])))
            tokens.append(Token(TokenType.INDEX, int(p[3])))

        elif p[0] == "sub":
            tokens.append(Token(TokenType.OP, "sub"))
            if p[1][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[1][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[1])))
            if p[2][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[2][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[2])))
            tokens.append(Token(TokenType.INDEX, int(p[3])))

        elif p[0] == "jumpif":
            tokens.append(Token(TokenType.OP, "jumpif"))
            if p[1][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[1][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[1])))     
            tokens.append(Token(TokenType.LOGICOP, p[2]))
            if p[3][0] == "$": 
                tokens.append(Token(TokenType.NUMBER, int(p[3][1:])))
            else:
                tokens.append(Token(TokenType.INDEX, int(p[3])))
            tokens.append(Token(TokenType.LABEL, p[4]))

        elif p[0] == "jump":
            tokens.append(Token(TokenType.OP, "jump"))
            tokens.append(Token(TokenType.LABEL, p[1]))

        elif p[0] == "label":
            tokens.append(Token(TokenType.INITLABEL, p[1]))

        elif p[0] == "print":
            tokens.append(Token(TokenType.OP, "print"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))

        elif p[0] == "printchr":
            tokens.append(Token(TokenType.OP, "printchr"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))

        elif p[0] == "input":
            tokens.append(Token(TokenType.OP, "input"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))

        elif p[0] == "inputchr":
            tokens.append(Token(TokenType.OP, "inputchr"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))


        elif p[0] == "storepos":
            tokens.append(Token(TokenType.OP, "storepos"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))

        elif p[0] == "jumppos":
            tokens.append(Token(TokenType.OP, "jumppos"))
            tokens.append(Token(TokenType.INDEX, int(p[1])))
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

