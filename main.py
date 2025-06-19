import operator, sys

logicOps = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

Mem = []

def CheckMem(idx):
    if len(Mem)-1 < int(idx):
        for i in range((int(idx) - len(Mem)) + 1):
            Mem.append(0)

def Add(idx1, idx2, idx3):
    Mem[int(idx3)] = Mem[int(idx1)] + Mem[int(idx2)]

def Sub(idx1, idx2, idx3):
    Mem[int(idx3)] = Mem[int(idx1)] - Mem[int(idx2)]

def Store(idx, data):
    Mem[int(idx)] = int(data)

def JumpIf(idx1, op, idx2) -> bool:
    return logicOps[op](Mem[int(idx1)], Mem[int(idx2)])

def runProgram(program, labels):

    head = 0
    while head < len(program):
        p = program[head].lower().split(" ")
        if p[0] == "store":
            CheckMem(p[1])
            Store(p[1], p[2])
        elif p[0] == "add":
            CheckMem(p[1])
            Add(p[1], p[2], p[3])
        elif p[0] == "sub":
            CheckMem(p[1])
            Sub(p[1], p[2], p[3])
        elif p[0] == "jumpif":
            if JumpIf(p[1], p[2], p[3]): 
                head = labels[p[4]]
                continue
        elif p[0] == "print":
            print(Mem[int(p[1])])

        head+=1

def loadProgram(file) -> str:
    with open(file, "r", encoding="utf-8") as f:
        return f.read().split("\n")

def generateLabels(program):
    labels = {}
    for i in range(len(program)):
        p = program[i].lower().split(" ")
        if p[0] == "label":
            labels[p[1]] = i
    return labels

if __name__ == "__main__":
    program = loadProgram(sys.argv[1])
    runProgram(program, generateLabels(program))
