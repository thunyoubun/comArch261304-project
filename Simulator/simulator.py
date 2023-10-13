import os

class Simulator:
    def __init__(self):
        self.maximumMemory = 65536                    # constant for maximum memory and number of registers
        self.numberRegisters = 8                      
        self.executionCount = 0                       # Initialize execution count
        self.halt = False                             # Initialize halt flag to False
        self.tempString = []

        self.state = {
            'pc': 0,                                  # default program counter
            'mem': [0] * self.maximumMemory,          # default memory and registers should be initialized with zero
            'reg': [0] * self.numberRegisters,        
            'numMemory': 0                            # number of memory world initialized with zero
        }
        
    def loadMachineCode(self, machineCodeFile):
        folder_path = "machineCodeFiles"
        try:
            file_path = os.path.join(folder_path, machineCodeFile)
            try:
                with open(file_path, "r") as filePtr:
                    lines = filePtr.readlines()

                    for line in lines:
                        self.state['mem'][self.state['numMemory']] = int(line)
                        self.state['numMemory'] += 1

            except FileNotFoundError:
                self.exceptionError(f"Machine code file not found {machineCodeFile}")
        except FileNotFoundError:
            self.exceptionError(f"Folder machine code files not found {folder_path}")
    
    def printState(self):                                                   # print the state of the Simulator
        print("\n@@@\nstate:")
        print(f"\tpc {self.state['pc']}")

        print("\tmemory:")
        for i in range(self.state['numMemory']):
            print(f"\t\tmem[ {i} ] {self.state['mem'][i]}")

        print("\tregisters:")
        for i, registerValue in enumerate(self.state['reg']):
            print(f"\t\treg[ {i} ] {registerValue}")

        print("end state")

    def formatOutputString(self):
        state_str = ["@@@", "state:"]
        state_str.append(f"\tpc {self.state['pc']}")

        state_str.append("\tmemory:")
        for i in range(self.state['numMemory']):
            state_str.append(f"\t\tmem[ {i} ] {self.state['mem'][i]}")

        state_str.append("\tregisters:")
        for i, registerValue in enumerate(self.state['reg']):
            state_str.append(f"\t\treg[ {i} ] {registerValue}")

        state_str.append("end state")
    
        return '\n'.join(state_str)

    def exceptionError(self, message):                                      # Display an error message
        print(f"exception {message}")

    def isValidRegister(self, register):
        return 0 <= register < self.numberRegisters                         # returns 0 if the register is valid
    
    def convertNumber(self, number):                                        # Convert a signed 16-bit number to a Python integer
        if number & (1 << 15):
            number -= (1 << 16)
        return number

    ## opcodes table ##
    #   ADD  -> 0
    #   NOR  -> 1
    #   LW   -> 2
    #   SW   -> 3
    #   BEQ  -> 4
    #   JALR -> 5
    #   HALT -> 6
    #   NOOP -> 7

    def parseInstructionFromMemory(self):                                   # Parse an instruction from memory and extract opcode and arguments
        memoryValue = self.state['mem'][self.state['pc']]

        opcode = (memoryValue >> 22) & 0b111
        arg0 = (memoryValue >> 19) & 0b111
        arg1 = (memoryValue >> 16) & 0b111
        arg2 = memoryValue & 0xFFFF
        
        return opcode, arg0, arg1, arg2

    def executeInstructionType_R(self, opcode, arg0, arg1, dest):                                                       # execute instruction R type
        if not self.isValidRegister(arg0) or not self.isValidRegister(arg1) or not self.isValidRegister(dest):          # check if register(rs), (rt), (dest) is invalid 
            self.exceptionError(f"Register must be a valid register {arg0}, {arg1}, {dest}")                            # throw exception show and value rs, rt, dest

        if opcode == 0:                                                                                        # check if opcode is ADD elif NOR                   
            self.state['reg'][dest] = self.state['reg'][arg0] + self.state['reg'][arg1]                        # assign ....
        elif opcode == 1:                                                   
            self.state['reg'][dest] = ~(self.state['reg'][arg0] & self.state['reg'][arg1])
        else:                                                                                                  # else throw exception
            self.exceptionError("Invalid opcode" + str(opcode))
    
    def executeInstructionType_I(self, opcode, arg0, arg1, offset):                                                     # execute instruction I type
        offset = self.convertNumber(offset)                                                                             # assign offset to 2's complement

        if not self.isValidRegister(arg0) or not self.isValidRegister(arg1):                                            # check if register(rs), (rt) is invalid 
            self.exceptionError(f"Register must be a valid register {arg0}, {arg1}")                                    # throw exception and show value rs, rt
        
        if offset > 32767 or offset < -32768:                                                                           # check if offset is more than maximum positive value or less than minimum negative value 
            self.exceptionError("Out of range offset")                                                                  # throw exception

        if opcode == 2:                                                                                        # check if opcode is LW elif SW elif BEQ     
            self.state['reg'][arg1] = self.state['mem'][self.state['reg'][arg0] + offset]                      # assign ....
        elif opcode == 3:
            self.state['mem'][self.state['reg'][arg0] + offset] = self.state['reg'][arg1]
            print(f"{self.state['mem'][self.state['reg'][arg0] + offset]} = {self.state['reg'][arg1]}")
        elif opcode == 4:
            if self.state['reg'][arg0] == self.state['reg'][arg1]:
                self.state['pc'] += offset
        else:                                                                                                  # else throw exception
            self.exceptionError(f"Invalid opcode" + {opcode})

    def executeInstructionType_J(self, opcode, arg0, arg1):                                                             # execute instruction J type
        if not self.isValidRegister(arg0) or not self.isValidRegister(arg1):                                            # check if register(rs), (rt) is invalid
            self.exceptionError(f"Register must be a valid register {arg0}, {arg1}")                                    # throw exception and show value rs, rt

        if opcode == 5:                                                                                        # check if opcode is JARL
            self.state['reg'][arg1] = self.state['pc']                                                         # assign ....
            self.state['pc'] = self.state['reg'][arg0]
        else:                                                                                                  # else throw exception
            self.exceptionError(f"Invalid opcode" + {opcode})

    def executeInstructionType_O(self, opcode):
        if opcode == 6:
            self.halt = True
        elif opcode == 7:
            pass
        else:
            self.exceptionError(f"Invalid opcode" + {opcode})

    def executeTask(self):
        self.tempString.append("Example Run of Simulator")                                   # append header string
        print("Example Run of Simulator")                                                    # print machine code form memory indexes   

        for i in range(self.state['numMemory']):
            print((f"memory[{i}] = {self.state['mem'][i]}"))
            self.tempString.append(f"memory[{i}] = {self.state['mem'][i]}")

        self.printState()                                                                    # print first state, registers indexes is zero                                  
        self.tempString.append(self.formatOutputString())                                    # append first state follow format output print state

        while not self.halt:                                                            # loop until halt equals true
            opcode, arg0, arg1, arg2 = self.parseInstructionFromMemory()                # parse instruction from memory
            print(f"opcode = {opcode}, rs = {arg0}, rt = {arg1}, rd = {arg2}")

            self.state['pc'] += 1                                                       # increment pc + 1                                 
            self.executionCount += 1                                                    # increment execution count + 1

            if self.state['pc'] < 0 or self.state['pc'] >= self.maximumMemory:          # check if pc less than 0 or greater than maximum memory
                self.exceptionError("PC out of memory!!!")                              # throw exception                           

            if opcode == 0 or opcode == 1:                                              # case 0: ADD or case 1: NOR
                self.executeInstructionType_R(opcode, arg0, arg1, arg2)                 # execute instruction type R
            elif opcode == 2 or opcode == 3 or opcode == 4:                             # case 2: LW or case 3: SW or case 4: BEQ
                self.executeInstructionType_I(opcode, arg0, arg1, arg2)                 # execute instruction type I
            elif opcode == 5:                                                           # case 5: JALR
                self.executeInstructionType_J(opcode, arg0, arg1)                       # execute instruction type J
            elif opcode == 6 or opcode == 7:                                            # case 6: HALT or NOOP                                    
                self.executeInstructionType_O(opcode)                                   # execute instruction type O

            self.printState()                                                                # print every state after execution for each instruction type
            self.tempString.append(self.formatOutputString())                                # append state following before printState()
            print(f"total of {self.executionCount} instructions executed")

        self.tempString.append("machine halted")                                             # if halt is true then print
        self.tempString.append(f"total of {self.executionCount} instructions executed")      # then print total execution count
        print("machine halted")
        print(f"total of {self.executionCount} instructions executed")

        self.printState()                                                                    # print lasted state
        self.tempString.append(self.formatOutputString())                                    # append lasted state

    def saveOutputToFile(self):
        print(f"call method saving output to file")
        folder_path = "outputFiles"

        try:
            index = 1
            baseFilename = "simulateFile.txt"
            os.makedirs(folder_path, exist_ok = True)

            while True:
                outputFile = (f"{baseFilename[:-4]}{index}.txt")
                file_path = os.path.join(folder_path, outputFile)

                if not os.path.isfile(file_path):
                    break
                index += 1

            try:
                with open(file_path, 'w') as file:
                    file.write("\n".join(self.tempString))

                print(f"writing {outputFile} successfully")
            except FileExistsError:
                self.exceptionError(f"Output file {outputFile} does not exist")

        except FileNotFoundError:
            self.exceptionError(f"Folder not found {folder_path}")
