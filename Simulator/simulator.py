import os

class Simulator:
    # Initialize the simulator with default values
    def __init__(self):
        # Set initial parameters for the simulation
        self.maximumMemory = 65536                  # default maximum memory 
        self.numberRegisters = 8                    # default number of registers
        self.executionCount = 0                     # default execution count  
        self.halt = False                           # default halt  
        self.tempString = []                        # default temporary string

        self.state = {
            'pc': 0,                                # default program counter
            'mem': [0] * self.maximumMemory,        # default memory
            'reg': [0] * self.numberRegisters,      # default number of registers 
            'numMemory': 0                          # default number of memory
        }
    
    # Load machine code from a file (in hexadecimal) into the simulator's memory
        # Load machine code from a file and store it in memory
        # Each line of the file is a hexadecimal instruction
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
        # Print the program counter, memory contents, and register values
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

    # Format the state of the simulator for output to a file
        # Create a formatted string containing the state information
        # This is used for saving the state to an output file
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
        # Print an exception message with the provided description
    def exceptionError(self, message):                                      
        print(f"exception {message}")

    # Check if a register number is valid (between 0 and 7)
        # Check if a given register number is within a valid range
    def isValidRegister(self, register):
        return 0 <= register < self.numberRegisters                        
    
    # Convert a signed 16-bit number to a Python integer
        # Convert a 16-bit two's complement number to a Python integer
    def convertNumber(self, number):                                        
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

    # Parse an instruction from memory and extract opcode and arguments
        # Extract the opcode and arguments from a machine code instruction
    def parseInstructionFromMemory(self):
        memoryValue = self.state['mem'][self.state['pc']]
        opcode = (memoryValue >> 22) & 0b111
        rs = (memoryValue >> 19) & 0b111
        rt = (memoryValue >> 16) & 0b111
        rd = memoryValue & 0xFFFF
        
        print(opcode, rs, rt, rd)
        return opcode, rs, rt, rd
    
    # Execute an R-type instruction (ADD or NAND)
        # Execute an R-type instruction based on the opcode
    def executeInstructionType_R(self, opcode, rs, rt, dest):
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
        
        # check if register(rs), (rt), (dest) is invalid 
        if not self.isValidRegister(rs) or not self.isValidRegister(rt) or not self.isValidRegister(dest):          
            self.exceptionError(f"Register must be a valid register rs: {rs}, rt: {rt}, dest: {dest}")      

        if opcode == 0:                                                                                                         
            self.state['reg'][dest] = self.state['reg'][rs] + self.state['reg'][rt]                             
        elif opcode == 1:                                                   
            self.state['reg'][dest] = nand_operation(self.state['reg'][rs], self.state['reg'][rt])                 
        else:                                                                                                   
            self.exceptionError("Invalid opcode" + str(opcode))
    
    # Execute an I-type instruction (LW, SW, BEQ)
        # Execute an I-type instruction based on the opcode
    def executeInstructionType_I(self, opcode, rs, rt, offset):                                                  
        offset = self.convertNumber(offset & 0xffff)                                                                     

        # check if register(rs), (rt) is invalid
        if not self.isValidRegister(rs) or not self.isValidRegister(rt):                                             
            self.exceptionError(f"Register must be a valid register {rs}, {rt}")                                  

        # check if offset is more than maximum positive value or less than minimum negative value 
        if offset > 32767 or offset < -32768:                                                              
            self.exceptionError("Out of range offset")                   

        if opcode == 2:                                                                                       
            self.state['reg'][rt] = self.state['mem'][self.state['reg'][rs] + offset]                  
        elif opcode == 3:
            self.state['mem'][self.state['reg'][rs] + offset] = self.state['reg'][rt]
            self.state['numMemory'] += 1
            print(f"{self.state['reg'][rs] + offset}")
        elif opcode == 4:
            if self.state['reg'][rs] == self.state['reg'][rt]:
                self.state['pc'] += offset
        else:                                                                                            
            self.exceptionError(f"Invalid opcode {opcode}")

    # Execute a J-type instruction (JALR)
    def executeInstructionType_J(self, opcode, rs, rt):    
        # check if register(rs), (rt) is invalid                                                        
        if not self.isValidRegister(rs) or not self.isValidRegister(rt):                                            
            self.exceptionError(f"Register must be a valid register {rs}, {rt}")                       

        if opcode == 5:                                                                                     
            print(f"regA: {rs}, regB: {rt}, PC: {self.state['pc']}")
            self.state['reg'][rt] = self.state['reg'][rs]
            self.state['reg'][rs] = self.state['pc']
            self.state['reg'][rs], self.state['reg'][rt] = self.state['reg'][rt], self.state['reg'][rs]
            self.state['pc'] = self.state['reg'][rs]
            print(f"JALR instruction executed: rs[{rt}] = {self.state['reg'][rt]}, PC={self.state['pc']}")
        else:                                                                                                       
            self.exceptionError(f"Invalid opcode" + {opcode})

    # Execute an O-type instruction (HALT or NOOP)
    def executeInstructionType_O(self, opcode):
        if opcode == 6:
            self.halt = True
        elif opcode == 7:
            pass
        else:
            self.exceptionError(f"Invalid opcode" + {opcode})

    # Execute the entire task in the simulator
        # Execute the instructions in the simulator's memory
    def executeTask(self):
        # append header string
        self.tempString.append("Example Run of Simulator")                                   
        print("Example Run of Simulator")                                                    

        # print machine code form memory indexes   
        for i in range(self.state['numMemory']):
            print((f"memory[{i}] = {self.state['mem'][i]}"))
            self.tempString.append(f"memory[{i}] = {self.state['mem'][i]}")

        # print first state, registers indexes is zero  
        self.printState()
        # append first state follow format output print state                                                                                                    
        self.tempString.append(self.formatOutputString())                                    

        # loop until halt equals true
        while not self.halt:                                                            
            if self.executionCount >= self.maximumMemory:
                break
            
            # parse instruction from memory
            opcode, rs, rt, rd = self.parseInstructionFromMemory()                
            print(f"\nopcode = {opcode}, rs = {rs}, rt = {rt}, rd = {rd}")

            # increment pc + 1 
            # increment execution count + 1 
            self.state['pc'] += 1                                                                                       
            self.executionCount += 1                                                  

            # check if pc less than 0 or greater than maximum memory
            if self.state['pc'] < 0 or self.state['pc'] >= self.maximumMemory:          
                self.exceptionError("PC out of memory!!!")                          

            # case 0: ADD or case 1: NOR then execute instruction R type
            if opcode == 0 or opcode == 1:                                              
                self.executeInstructionType_R(opcode, rs, rt, rd)
            # case 2: LW or case 3: SW or case 4: BEQ then execute instruction I type
            elif opcode == 2 or opcode == 3 or opcode == 4:                             
                self.executeInstructionType_I(opcode, rs, rt, rd)
            # case 5: JALR then execute instruction type J
            elif opcode == 5:                                                           
                self.executeInstructionType_J(opcode, rs, rt) 
            # case 6: HALT or NOOP then execute instruction type O                      
            elif opcode == 6 or opcode == 7:                                                                             
                self.executeInstructionType_O(opcode)                                 

            # print every state after execution for each instruction type
            self.printState()
            # append state following before printState()                                                                
            self.tempString.append(self.formatOutputString())                                
            print(f"total of {self.executionCount} instructions executed")

        # append footer after halt is true
        # append total instruction execution
        self.tempString.append("machine halted")                                             
        self.tempString.append(f"total of {self.executionCount} instructions executed") 
        # if halt is true then print
        # then print total execution count     
        print("machine halted")
        print(f"total of {self.executionCount} instructions executed")

        # print lasted state
        # append lasted state
        self.printState()                                                                    
        self.tempString.append(self.formatOutputString())                                   

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
