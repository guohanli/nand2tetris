import sys
import os

# 符号表，存储变量和标签的地址
symbol_table = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SCREEN": 16384,
    "KBD": 24576,
}
next_variable_address = 16  # 下一个可用的变量地址起始值


def add_entry(symbol, address):
    symbol_table[symbol] = address


def translate_a_instruction(instruction):
    symbol = instruction[1:]
    if symbol.isdigit():  # @value
        address = int(symbol)
    else:
        if symbol in symbol_table:  # @symbol
            address = symbol_table[symbol]
        else:  # 新的变量或标签
            global next_variable_address
            address = next_variable_address
            add_entry(symbol, address)
            next_variable_address += 1
    return f"0{address:015b}"


def translate_c_instruction(instruction):
    comp = ""
    dest = ""
    jump = ""
    if "=" in instruction:
        dest, comp = instruction.split("=")
    if ";" in instruction:
        comp, jump = instruction.split(";")

    comp_code = {
        # a=0
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        # a=1
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
    }

    dest_code = {
        "": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
    }

    jump_code = {
        "": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    return f"111{comp_code[comp]}{dest_code[dest]}{jump_code[jump]}"


def translate_instruction(instruction):
    if instruction.startswith("@"):
        return translate_a_instruction(instruction)
    else:
        return translate_c_instruction(instruction)


def assemble(assembly_code):
    binary_code = []
    for line in assembly_code:
        line = line.strip()
        # 忽略标签指令
        if line.startswith("(") and line.endswith(")"):
            continue
        # 忽略注释
        if "//" in line:
            line = line[: line.index("//")].strip()
        if line:
            binary_instruction = translate_instruction(line)
            binary_code.append(binary_instruction)
    return binary_code


def handle_labels(assembly_code):
    instruction_count = 0  # 跳过标签指令的计数
    for line in assembly_code:
        line = line.strip()
        if line.startswith("(") and line.endswith(")"):
            # 处理标签指令，将标签和对应的指令地址添加到符号表中
            symbol = line[1:-1]
            add_entry(symbol, instruction_count)
        else:
            # 忽略注释
            if "//" in line:
                line = line[: line.index("//")].strip()
            if line:
                instruction_count += 1


def assemble_file(file_path):
    # 读取汇编文件
    with open(file_path, "r") as assembly_file:
        assembly_code = assembly_file.readlines()

    # 处理标签
    handle_labels(assembly_code)

    # 调用汇编器进行汇编
    binary_code = assemble(assembly_code)

    # 指定输出文件路径
    output_path = os.path.splitext(file_path)[0] + ".hack"

    # 保存二进制代码到输出文件
    with open(output_path, "w") as output_file:
        for instruction in binary_code:
            output_file.write(instruction + "\n")

    print(f"Assembly successfully written to: {output_path}")


# 获取命令行参数中的汇编文件路径
if len(sys.argv) < 2:
    print("Please provide the assembly file path as a command line argument.")
    sys.exit(1)

file_path = sys.argv[1]

# 检查文件路径是否有效
if not os.path.isfile(file_path):
    print(f"Invalid file path: {file_path}")
    sys.exit(1)

# 调用assemble_file函数来汇编指定的文件
assemble_file(file_path)
