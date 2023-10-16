import os

class Simulator:
    # กำหนดค่าเริ่มต้นของระบบ 
    def __init__(self):
        self.maximumMemory = 65536                  # constant for maximum memory and number of registers
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
    
    # โหลด machine code ที่เป็น hex จากการผ่าน assembler 
    # โหลดเป็น line ใส่ state mem
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

    # print the state of the Simulator
    def printState(self):                                                   
        print("\n@@@\nstate:")
        print(f"\tpc {self.state['pc']}")

        print("\tmemory:")
        for i in range(self.state['numMemory']):
            print(f"\t\tmem[ {i} ] {self.state['mem'][i]}")

        print("\tregisters:")
        for i, registerValue in enumerate(self.state['reg']):
            print(f"\t\treg[ {i} ] {registerValue}")

        print("end state")

    # เก็บ format print state ใส่ list string ไว้ไปใส่ใน output file
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

    # Display an error message
    def exceptionError(self, message):                                      
        print(f"exception {message}")

    # check if register >= 0 or <= 8
    def isValidRegister(self, register):
        return 0 <= register < self.numberRegisters                         # returns 0 if the register is valid
    
    # convert integer
    def convertNumber(self, number):                                        # Convert a signed 16-bit number to a Python integer
        if number & (1 << 15):
            number -= (1 << 16)
        return number

    ## opcodes table ##
    #   ADD  -> 0
    #   NAND -> 1
    #   LW   -> 2
    #   SW   -> 3
    #   BEQ  -> 4
    #   JALR -> 5
    #   HALT -> 6
    #   NOOP -> 7


    def parseInstructionFromMemory(self):                                   # Parse an instruction from memory and extract opcode and arguments
        memoryValue = self.state['mem'][self.state['pc']]

        opcode = (memoryValue >> 22) & 0b111
        rs = (memoryValue >> 19) & 0b111
        rt = (memoryValue >> 16) & 0b111
        rd = memoryValue & 0xFFFF
        
        print(opcode, rs, rt, rd)
        return opcode, rs, rt, rd       # Return decimals arguments
    

    def executeInstructionType_R(self, opcode, rs, rt, dest):                                                       # execute instruction R type
        def nand_operation(a, b):
            # Convert decimal numbers to binary strings
            binary_a = bin(a)[2:]
            binary_b = bin(b)[2:]

            # Ensure the binary strings have the same length by adding leading zeros
            max_len = max(len(binary_a), len(binary_b))
            binary_a = binary_a.zfill(max_len)
            binary_b = binary_b.zfill(max_len)

            # Perform the NAND operation bit by bit
            result = ""
            for bit_a, bit_b in zip(binary_a, binary_b):
                result += '0' if bit_a == '1' and bit_b == '1' else '1'

            # Convert the binary result to decimal
            decimal_result = int(result, 2)
            return decimal_result
        
        if not self.isValidRegister(rs) or not self.isValidRegister(rt) or not self.isValidRegister(dest):          # check if register(rs), (rt), (dest) is invalid 
            self.exceptionError(f"Register must be a valid register rs: {rs}, rt: {rt}, dest: {dest}")                            # throw exception show and value rs, rt, dest

        if opcode == 0:                                                                                         # check if opcode is ADD elif NAND                   
            self.state['reg'][dest] = self.state['reg'][rs] + self.state['reg'][rt]                             # assign ....
        elif opcode == 1:                                                   
            self.state['reg'][dest] = nand_operation(self.state['reg'][rs], self.state['reg'][rt])                             # Perform the NAND operation
            
            #~ (self.state['reg'][rs] & self.state['reg'][rt])
            #print(f"register[{rs}]:{self.state['reg'][rs]} register[{rt}]: {self.state['reg'][rt]}")
            #print(f"result after nand: {self.state['reg'][dest]}")
        else:                                                                                                   # else throw exception
            self.exceptionError("Invalid opcode" + str(opcode))
    
    def executeInstructionType_I(self, opcode, rs, rt, offset):                                                     # execute instruction I type
        offset = self.convertNumber(offset & 0xffff)                                                                             # assign offset to 2's complement

        if not self.isValidRegister(rs) or not self.isValidRegister(rt):                                            # check if register(rs), (rt) is invalid 
            self.exceptionError(f"Register must be a valid register {rs}, {rt}")                                    # throw exception and show value rs, rt
    
        if offset > 32767 or offset < -32768:                                                                           # check if offset is more than maximum positive value or less than minimum negative value 
            self.exceptionError("Out of range offset")                                                                  # throw exception

        if opcode == 2:                                                                                        # check if opcode is LW elif SW elif BEQ     
            self.state['reg'][rt] = self.state['mem'][self.state['reg'][rs] + offset]                      # assign ....
        elif opcode == 3:
            self.state['mem'][self.state['reg'][rs] + offset] = self.state['reg'][rt]

            self.state['numMemory'] += 1

            print(f"{self.state['reg'][rs] + offset}")
        elif opcode == 4:
            if self.state['reg'][rs] == self.state['reg'][rt]:
                self.state['pc'] += offset
        else:                                                                                                  # else throw exception
            self.exceptionError(f"Invalid opcode {opcode}")

    def executeInstructionType_J(self, opcode, rs, rt):                                                             # execute instruction J type
        if not self.isValidRegister(rs) or not self.isValidRegister(rt):                                            # check if register(rs), (rt) is invalid
            self.exceptionError(f"Register must be a valid register {rs}, {rt}")                                    # throw exception and show value rs, rt

        if opcode == 5:                                                                                             # check if opcode is JARL
            print(f"regA: {rs}, regB: {rt}, PC: {self.state['pc']}")

            self.state['reg'][rt] = self.state['reg'][rs]
            self.state['reg'][rs] = self.state['pc']
            
            self.state['reg'][rs], self.state['reg'][rt] = self.state['reg'][rt], self.state['reg'][rs]
            self.state['pc'] = self.state['reg'][rs]

            print(f"JALR instruction executed: rs[{rt}] = {self.state['reg'][rt]}, PC={self.state['pc']}")
        else:                                                                                                       # else throw exception
            self.exceptionError(f"Invalid opcode" + {opcode})

    def executeInstructionType_O(self, opcode):
        if opcode == 6:
            self.halt = True
        elif opcode == 7:
            pass
        else:
            self.exceptionError(f"Invalid opcode" + {opcode})

    def executeTask(self):
        # append header string
        self.tempString.append("Example Run of Simulator")                                   
        print("Example Run of Simulator")                                                    

        # print machine code form memory indexes   
        for i in range(self.state['numMemory']):
            print((f"memory[{i}] = {self.state['mem'][i]}"))
            self.tempString.append(f"memory[{i}] = {self.state['mem'][i]}")

        self.printState()                                                                    # print first state, registers indexes is zero                                  
        self.tempString.append(self.formatOutputString())                                    # append first state follow format output print state

        while not self.halt:                                                            # loop until halt equals true
            if self.executionCount >= self.maximumMemory:
                break

            opcode, rs, rt, rd = self.parseInstructionFromMemory()                # parse instruction from memory
            print(f"\nopcode = {opcode}, rs = {rs}, rt = {rt}, rd = {rd}")

            self.state['pc'] += 1                                                       # increment pc + 1                                 
            self.executionCount += 1                                                    # increment execution count + 1

            if self.state['pc'] < 0 or self.state['pc'] >= self.maximumMemory:          # check if pc less than 0 or greater than maximum memory
                self.exceptionError("PC out of memory!!!")                              # throw exception                           

            if opcode == 0 or opcode == 1:                                              # case 0: ADD or case 1: NOR
                self.executeInstructionType_R(opcode, rs, rt, rd)                 # execute instruction type R
            elif opcode == 2 or opcode == 3 or opcode == 4:                             # case 2: LW or case 3: SW or case 4: BEQ
                self.executeInstructionType_I(opcode, rs, rt, rd)                 # execute instruction type I
            elif opcode == 5:                                                           # case 5: JALR
                self.executeInstructionType_J(opcode, rs, rt)                       # execute instruction type J
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
