import os


def isNumber(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def hasLabel(instruction):
    if instruction[0] in opcode_table : #check ว่าเป็นคำสั่งหรือไม่
        return False
    else:
        if isNumber(instruction[1]):
            return False
        else:
            return True


def getReg(reg):
    if isNumber(reg):
        reg = int(reg)
    return reg


def offsetField(name_instruction, reg3, pc):
    if isNumber(reg3):  # เป็น Numeric address
        offset = int(reg3)
    else:  # เป็น Symbolic address
        adds = findAddressLabel(reg3)
        if adds == None:
            print(f"ERROR: label {reg3} not found")
            exit(0)
        else:
            if name_instruction == 'beq':
                # offsetFiled ของ beq คือ ตำแหน่งของคำสั่งถัดไป - ตำแหน่งของคำสั่งปัจจุบัน - 1
                offset = offset_2Complement_16bit(adds - pc - 1)
                
            elif name_instruction == 'lw' or name_instruction == 'sw':
                offset = offset_2Complement_16bit(adds)


    return int(offset)

# -3 = 1111111111111101
# 3 = 0000000000000011
def offset_2Complement_16bit(num):
    if num < 0:
        num = bin(num & 0b1111111111111111)[2:]
        num = num.zfill(16)

    else:
        num = bin(num)[2:]
        num = num.zfill(16)
    return int(num, 2)

def findAddressLabel(reg):
    for i in range(len(instruction_all)):
        if reg == instruction_all[i][0]:
            return i


def analyze_instruction(instruction):
    # ตรวจสอบว่าคำสั่งอยู่ในตาราง opcode หรือไม่
    if instruction in opcode_table:
        opcode = opcode_table[instruction]["opcode"]
        inst_type = opcode_table[instruction]["type"]
        return opcode, inst_type
    else:
        print(f"ERROR: instruction {instruction} not found ")
        exit(0)
    

# แปลงคำสั่งเป็น machine code
def convert_to_machine_code(instruction, idx):
    
    # ตรวจสอบว่ามี label หรือไม่
    if not hasLabel(instruction):  # ไม่มี label
        # [0] = name_instruction ,[1] = regA, [2] = regB, [3] = destReg
        label_list.append(None)
        if instruction[0] != '.fill':  # ไม่ใช่ .fill
            opcode, type = analyze_instruction(instruction[0])
            if type == 'R':  # (add, nand)
                regA = getReg(instruction[1])
                regB = getReg(instruction[2])
                destReg = getReg(instruction[3])
                machine_code = (opcode << 22) | (regA << 19) | (
                    regB << 16) | (destReg << 0) | 0b0000000000000000
            elif type == 'I':  # (lw, sw, beq)
                regA = getReg(instruction[1])
                regB = getReg(instruction[2])
                offset = offsetField(instruction[0], instruction[3], idx)
                machine_code = (opcode << 22) | (regA << 19) | (
                    regB << 16) | (offset) | 0b0000000000000000
            elif type == 'J':  # (jalr)
                regA = getReg(instruction[1])
                regB = getReg(instruction[2])
                machine_code = (opcode << 22) | (regA << 19) | (
                    regB << 16) | 0b0000000000000000
            elif type == 'O':  # (halt, noop)
                machine_code = (opcode << 22) | 0b000000000000000000000000
        else:  # เป็น .fill
            if isNumber(instruction[1]):
                machine_code = int(instruction[1])
            else:
                machine_code = findAddressLabel(instruction[1])

    else:  # มี label
        # [0] = label, [1] = name_instruction ,[2] = regA, [3] = regB, [4] = destReg
        label_list.append(instruction[0])
        if instruction[1] != '.fill':  # ไม่ใช่ .fill
            opcode, type = analyze_instruction(instruction[1])
            if type == 'R':  # (add, nand)
                regA = getReg(instruction[2])
                regB = getReg(instruction[3])
                destReg = getReg(instruction[4])
                machine_code = (opcode << 22) | (regA << 19) | (
                    regB << 16) | (destReg << 0) | 0b0000000000000000
            elif type == 'I':  # (lw, sw, beq)
                regA = getReg(instruction[2])
                regB = getReg(instruction[3])
                offset = offsetField(instruction[1], instruction[4], idx)
                machine_code = (opcode << 22) | (regA << 19) | (
                    regB << 16) | (offset << 0) | 0b0000000000000000
            elif type == 'J':  # (jalr)
                regA = getReg(instruction[2])
                regB = getReg(instruction[3])
                machine_code = (opcode << 22) | (regA << 19) | (
                    regB << 16) | 0b0000000000000000
            elif type == 'O':  # (halt, noop)
                machine_code = (opcode << 22) | 0b000000000000000000000000
        else:  # เป็น .fill
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

## constant
instruction_all = []
instruction_current = []
label_list = []
machine_list = []
folder_path = "assembly_code"


def AllFile():
    try:
        file_names = os.listdir(folder_path)
    except FileNotFoundError:
        print("Folder not found")
        exit(0)
    for page in range(len(file_names)):
        print(f"Page name: {file_names[page]}")
        if file_names[page].endswith(".txt"):
            file_path = os.path.join(folder_path, file_names[page])
            with open(file_path, 'r') as file:
                # อ่านไฟล์และแยกคำสั่ง
                lines = [line.strip() for line in file if line.strip()]
                for line in lines:
                    line = line.lower()
                    line = line.replace("\n", "")
                    instruction_all.append(line.split())

                for i in range(len(instruction_all)):
                    instruction_current = instruction_all[i]
                    # แปลงคำสั่งเป็น machine code
                    machine_code = convert_to_machine_code(instruction_current[0:4], i)
                    machine_list.append(machine_code)
                    print(f"(address {i}): {machine_code} ({hex(machine_code)})")
                file.close()

                # บันทึกไฟล์
                save_file = open(f"machine_code/machine{page+1}.txt", "w")
                for i in range(len(machine_list)):
                    save_file.writelines(f"{machine_list[i]}")
                    save_file.writelines("\n")
                # ล้างค่า
                machine_list.clear()
                instruction_all.clear()
                label_list.clear()

                save_file.close()
                print("Save file success")


    

def OneFile(name_file):
    try:
        file_names = os.listdir(folder_path)
    except FileNotFoundError:
        print("Folder not found")
        exit(0)
    file_path = os.path.join(folder_path,name_file)
    print(f"Page name: {file_path}")
    with open(file_path,'r' , encoding="utf-8") as file:
        # อ่านไฟล์และแยกคำสั่ง
        lines = [line.strip() for line in file if line.strip()]
        for line in lines:
            line = line.lower()
            line = line.replace("\n", "")
            instruction_all.append(line.split())

        for i in range(len(instruction_all)):
            instruction_current = instruction_all[i]
            # แปลงคำสั่งเป็น machine code
            # print(instruction_current)
            machine_code = convert_to_machine_code(instruction_current, i)
            machine_list.append(machine_code)
            print(f"(address {i}): {machine_code} ({hex(machine_code)})")
        file.close()

        # บันทึกไฟล์
        save_file = open(f"machine_code/machine_{name_file}", "w")
        for i in range(len(machine_list)):
            save_file.writelines(f"{machine_list[i]}")
            save_file.writelines("\n")
        # ล้างค่า
        machine_list.clear()
        instruction_all.clear()
        label_list.clear()

        save_file.close()
        print(f"Save file success at machine_code/machine_{name_file}")

def test_code():
    try:
        file_names = os.listdir("test_case")
    except FileNotFoundError:
        print("Folder not found")
        exit(0)
    for page in range(len(file_names)):

        try:
            if file_names[page].endswith(".txt"):
                file_path = os.path.join("test_case", file_names[page])
                with open(file_path, 'r' ,encoding="utf-8") as file:
                    lines = [line.strip() for line in file if line.strip()]
                    # อ่านไฟล์และแยกคำสั่ง
                    
                    for line in lines:       
                        line = line.lower()
                        line = line.replace("\n", "")
                        instruction_all.append(line.split())

                    for i in range(len(instruction_all)):
                        instruction_current = instruction_all[i]
                        # แปลงคำสั่งเป็น machine code
                        try:
                            machine_code = convert_to_machine_code(instruction_current, i)
                        except:
                            # print(f"❌ {file_names[page]} is FAIL")
                            exit(0)
                        machine_list.append(machine_code)
                        # print(f"(address {i}): {machine_code} ({hex(machine_code)})")
                    file.close()

                    # บันทึกไฟล์
                    with open(f"expect_code/case{page+1}.txt", "r") as expect_file:
                        i = 0
                        for line in expect_file:
                            line = int(line)
                            if line == machine_list[i]:
                                pass
                            else:
                                print(f"❌ {file_names[page]} is FAIL")
                                print(f"expect: {line} but got: {machine_list[i]}")
                                exit(0)
                            i += 1
                        print(f"✅ {file_names[page]} is PASS")
                        # ล้างค่า
                        machine_list.clear()
                        instruction_all.clear()
                        label_list.clear()

                        expect_file.close()
        except:
            print(f"❌ {file_names[page]} is FAIL")
            continue
            


#### run assembler ###

OneFile("combination.txt")
# AllFile()


#### test case ###

# test_code()
