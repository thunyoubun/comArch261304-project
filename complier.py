import os

def isNumber(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def hasLabel(instruction):
    if instruction[0] in ['add', 'nand', 'lw', 'sw', 'beq', 'jalr', 'halt', 'noop', '.fill']:
       return False
    else:
        return True
    
def getReg(reg):
    if isNumber(reg):
        reg = int(reg)
    
    return reg

def offsetField(name_instruction,reg3,idx):
    if isNumber(reg3): # เป็นเลข
        offset = int(reg3)
    else: # เป็น Symbolic address
        adds = findAddressLabel(reg3)
        if adds == None:
            raise Exception(f"ERROR: label {reg3} not found", exit(0))
        else:
            if name_instruction == 'beq':
                offset = machine_list[adds + 1] - idx - 1
            elif name_instruction == 'lw' or name_instruction == 'sw':
                offset = adds

    return int(offset)
   
def twoComplement(num):
    if num < 0:
        num = bin(num)[3:]
    else:
        num = bin(num)[2:]
    return num

def findAddressLabel(reg):
    for i in range(len(instruction_all)):
        if reg == instruction_all[i][0]:
            return i

def analyze_instruction(instruction): 
    # ตรวจสอบว่าคำสั่งอยู่ในตาราง opcode หรือไม่
    if instruction in opcode_table:
        opcode = opcode_table[instruction]["opcode"]
        inst_type = opcode_table[instruction]["type"]
        return  opcode ,inst_type
    else:
        raise  Exception (f"ERROR: instruction {instruction} not found " , exit(0))
  
# แปลงคำสั่งเป็น machine code
def convert_to_machine_code(instruction,idx):
    
    # ตรวจสอบว่ามี label หรือไม่
    if not  hasLabel(instruction): # ไม่มี label
        # [0] = name_instruction ,[1] = regA, [2] = regB, [3] = destReg
        label_list.append(None)
        if instruction[0] != '.fill': # ไม่ใช่ .fill 
            opcode ,type = analyze_instruction(instruction[0])
            if type == 'R': # (add, nand)
                regA = getReg( instruction[1])
                regB = getReg( instruction[2])
                destReg = getReg( instruction[3])
                machine_code = (opcode << 22) | (regA << 19) | (regB << 16) | (destReg << 0) | 0b0000000000000000
            elif type == 'I': # (lw, sw, beq)
                regA = getReg( instruction[1])
                regB = getReg( instruction[2])
                offset = offsetField(instruction[0],instruction[3],idx)
                machine_code = (opcode << 22) | (regA << 19) | (regB << 16) | (offset ) | 0b0000000000000000
            elif type == 'J': # (jalr)
                regA = getReg( instruction[1])
                regB = getReg( instruction[2])
                machine_code = (opcode<<22) | (regA<<19) | (regB<<16) | 0b0000000000000000
            elif type == 'O': # (halt, noop)
                machine_code = (opcode<<22) | 0b000000000000000000000000
        else: # เป็น .fill
            if isNumber(instruction[1]):
                machine_code = int(instruction[1])
            else:
                machine_code = findAddressLabel(instruction[1])

    else: # มี label    
        #[0] = label, [1] = name_instruction ,[2] = regA, [3] = regB, [4] = destReg
        label_list.append(instruction[0])
        if instruction[1] != '.fill': # ไม่ใช่ .fill
            opcode ,type = analyze_instruction(instruction[1])
            if type == 'R': # (add, nand)
                regA = getReg( instruction[2])
                regB = getReg( instruction[3])
                destReg = getReg( instruction[4])
                machine_code = (opcode << 22) | (regA << 19) | (regB << 16) | (destReg << 0) | 0b0000000000000000
            elif type == 'I': # (lw, sw, beq)
                regA = getReg( instruction[2])
                regB = getReg( instruction[3])
                offset = offsetField(instruction[1],instruction[4],idx)
                machine_code = (opcode << 22) | (regA << 19) | (regB << 16) | (offset << 0 ) | 0b0000000000000000
            elif type == 'J': # (jalr)
                regA = getReg( instruction[2])
                regB = getReg( instruction[3])
                machine_code = (opcode << 22) | (regA << 19) | (regB << 16) | 0b0000000000000000
            elif type == 'O': # (halt, noop)
                machine_code = (opcode<<22) | 0b000000000000000000000000
        else: # เป็น .fill
            if isNumber(instruction[2]):
                machine_code = int(instruction[2])
            else:
                machine_code = findAddressLabel(instruction[2])
           

    return machine_code

 # ตาราง opcode และประเภทของคำสั่ง
opcode_table = {
    "add": {"opcode": 0b000, "type": "R"},
    "nand": {"opcode": 0b001, "type": "R"},
    "lw": {"opcode": 0b010, "type": "I"},
    "sw": {"opcode": 0b011, "type": "I"},
    "beq": {"opcode": 0b100, "type": "I"},
    "jalr": {"opcode": 0b101, "type": "J"},
    "halt": {"opcode": 0b110, "type": "O"},
    "noop": {"opcode": 0b111, "type": "O"},
    
}

instruction_all = []
instruction_current = []
label_list = []
machine_list = []
folder_path = "assembly_code"
file_names = os.listdir(folder_path)
for page in range(file_names):
    if file_names[page].endswith(".txt"):
        file_path = os.path.join(folder_path, file_names[page])
        with open(file_path, 'r') as file:
            # อ่านไฟล์และแยกคำสั่ง
            for line in file:
                line = line.replace("\n","")
                instruction_all.append(line.split())
            
            for i in range(len(instruction_all)):
                instruction_current = instruction_all[i]
               
                machine_code = convert_to_machine_code(instruction_current,i)
                machine_list.append(machine_code)
                print(f"(address {i}): {machine_code} ({hex(machine_code)})")
            

            save_file = open(f"machine_code/machine{page}.txt", "w")
            for i in range(len(machine_list)):
                save_file.writelines(f"{machine_list[i]}")
                save_file.writelines("\n")
                
            save_file.close()
            print("Save file success")
            


