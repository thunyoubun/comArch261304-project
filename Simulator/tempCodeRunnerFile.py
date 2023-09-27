NUMMEMORY = 65536  # maximum number of words in memory
NUMREGS = 8  # number of machine registers
MAXLINELENGTH = 1000

# Util + Error Check Functions
def printState(state):
    print("\n@@@\nstate:")
    print(f"\tpc {state['pc']}")
    print("\tmemory:")
    for i, mem_value in enumerate(state['mem']):
        print(f"\t\tmem[ {i} ] {mem_value}")
    print("\tregisters:")
    for i, reg_value in enumerate(state['reg']):
        print(f"\t\treg[ {i} ] {reg_value}")
    print("end state")

def abortWithError(string):
    print(f"error: {string}")
    exit(1)

def isValidRegister(reg):
    return 0 <= reg < NUMREGS

def convertNum(num):
    if num & (1 << 15):
        num -= (1 << 16)
    return num

# Simulator Functions
def parseInstFromMem(state):
    mem_value = state['mem'][state['pc']]
    opcode = (mem_value >> 22) & 0b111
    arg0 = (mem_value >> 19) & 0b111
    arg1 = (mem_value >> 16) & 0b111
    arg2 = mem_value & 0xFFFF
    return opcode, arg0, arg1, arg2

def executeRTypeInst(state, opcode, arg0, arg1, dest):
    if not isValidRegister(arg0) or not isValidRegister(arg1) or not isValidRegister(dest):
        abortWithError("Register is not valid.")
    
    if opcode == 0:  # add
        state['reg'][dest] = state['reg'][arg0] + state['reg'][arg1]
    elif opcode == 1:  # nor
        state['reg'][dest] = ~(state['reg'][arg0] | state['reg'][arg1])
    else:
        abortWithError("Do not support its opcode.")

def executeITypeInst(state, opcode, arg0, arg1, offset):
    offset = convertNum(offset)
    
    if not isValidRegister(arg0) or not isValidRegister(arg1):
        abortWithError("Register is not valid.")
    
    if offset > 32767 or offset < -32768:
        abortWithError("Offset out of range.")
    
    if opcode == 2:  # lw
        state['reg'][arg1] = state['mem'][state['reg'][arg0] + offset]
    elif opcode == 3:  # sw
        state['mem'][state['reg'][arg0] + offset] = state['reg'][arg1]
    elif opcode == 4:  # beq
        if state['reg'][arg0] == state['reg'][arg1]:
            state['pc'] += offset
    else:
        abortWithError("Do not support its opcode.")

def executeJTypeInst(state, opcode, arg0, arg1):
    if not isValidRegister(arg0) or not isValidRegister(arg1):
        abortWithError("Register is not valid.")
    
    if opcode == 5:  # jalr
        state['reg'][arg1] = state['pc']
        state['pc'] = state['reg'][arg0]
    else:
        abortWithError("Do not support its opcode.")

def main():
    state = {
        'pc': 0,
        'mem': [0] * NUMMEMORY,
        'reg': [0] * NUMREGS,
        'numMemory': 0
    }
    
    executionCount = 0
    
    file_name = input("Enter machine-code file: ")
    
    try:
        with open(file_name, "r") as filePtr:
            lines = filePtr.readlines()
            
            for line in lines:
                state['mem'][state['numMemory']] = int(line)
                print(f"memory[{state['numMemory']}]={state['mem'][state['numMemory']]}")
                state['numMemory'] += 1
    
    except FileNotFoundError:
        abortWithError(f"Can't open file {file_name}")
    
    # Print initial state
    printState(state)
    
    while True:
        isHalt = False
        opcode, arg0, arg1, arg2 = parseInstFromMem(state)
        
        state['pc'] += 1
        executionCount += 1
        
        if state['pc'] < 0 or state['pc'] >= NUMMEMORY:
            abortWithError("PC out of memory.")
        
        # OPCODES
        # 0 - add
        # 1 - nor
        # 2 - lw
        # 3 - sw
        # 4 - beq
        # 5 - jalr
        # 6 - halt
        # 7 - noop
        
        if opcode == 0 or opcode == 1:  # R-Type
            executeRTypeInst(state, opcode, arg0, arg1, arg2)
        elif opcode == 2 or opcode == 3 or opcode == 4:  # I-Type
            executeITypeInst(state, opcode, arg0, arg1, arg2)
        elif opcode == 5:  # J-Type
            executeJTypeInst(state, opcode, arg0, arg1)
        elif opcode == 6:  # O-Type (halt)
            isHalt = True
        elif opcode == 7:  # O-Type (noop)
            pass
        else:
            abortWithError("Do not support its opcode.")
        
        if isHalt:
            break
        
        # Print state
        printState(state)
    
    print("machine halted")
    print(f"total of {executionCount} instructions executed")
    print("final state of machine:")
    printState(state)

if __name__ == "__main__":
    main()
