import sys
import yaml
import argparse
import struct


class Assembler:
    OPCODES = {
        'load_const': 29,
        'read_mem': 23,
        'write_mem': 20,
        'bitreverse': 3
    }

    def parse_yaml(self, yaml_content):
        intermediate = []

        for instruction in yaml_content['program']:
            if not instruction:
                continue

            for op_name, operand in instruction.items():
                if op_name in self.OPCODES:
                    opcode = self.OPCODES[op_name]

                    if op_name == 'load_const':
                        if operand < 0 or operand >= 2 ** 32:
                            raise ValueError(f"Константа {operand} вне диапазона")
                        intermediate.append({
                            'opcode': opcode,
                            'operand': operand,
                            'type': 'load_const'
                        })
                    elif op_name == 'read_mem':
                        if operand < 0 or operand >= 2 ** 16:
                            raise ValueError(f"Адрес {operand} вне диапазона")
                        intermediate.append({
                            'opcode': opcode,
                            'operand': operand,
                            'type': 'read_mem'
                        })
                    elif op_name == 'write_mem':
                        intermediate.append({
                            'opcode': opcode,
                            'type': 'write_mem'
                        })
                    elif op_name == 'bitreverse':
                        if operand < 0 or operand >= 2 ** 16:
                            raise ValueError(f"Адрес {operand} вне диапазона")
                        intermediate.append({
                            'opcode': opcode,
                            'operand': operand,
                            'type': 'bitreverse'
                        })
                    break
                else:
                    raise ValueError(f"Неизвестная команда: {op_name}")

        return intermediate

    @staticmethod
    def assemble_to_binary(intermediate):
        binary_data = bytearray()

        for instr in intermediate:
            opcode = instr['opcode']

            if instr['type'] == 'load_const':
                operand = instr['operand']
                value = (operand << 5) | opcode
                binary_data.extend(struct.pack('<Q', value)[:5])
            elif instr['type'] == 'read_mem':
                operand = instr['operand']
                value = (operand << 5) | opcode
                binary_data.extend(struct.pack('<I', value)[:3])
            elif instr['type'] == 'write_mem':
                binary_data.append(opcode)
            elif instr['type'] == 'bitreverse':
                operand = instr['operand']
                value = (operand << 5) | opcode
                binary_data.extend(struct.pack('<I', value)[:3])

        return bytes(binary_data)

    @staticmethod
    def format_instruction(instr):
        opcode = instr['opcode']

        if instr['type'] == 'load_const':
            operand = instr['operand']
            value = (operand << 5) | opcode
            bytes_hex = ', '.join(f'0x{b:02X}' for b in struct.pack('<Q', value)[:5])
            return f"A: {opcode}, B: {operand} -> {bytes_hex}"
        elif instr['type'] == 'read_mem':
            operand = instr['operand']
            value = (operand << 5) | opcode
            bytes_hex = ', '.join(f'0x{b:02X}' for b in struct.pack('<I', value)[:3])
            return f"A: {opcode}, Адрес: {operand} -> {bytes_hex}"
        elif instr['type'] == 'write_mem':
            bytes_hex = f'0x{opcode:02X}'
            return f"A: {opcode} -> {bytes_hex}"
        elif instr['type'] == 'bitreverse':
            operand = instr['operand']
            value = (operand << 5) | opcode
            bytes_hex = ', '.join(f'0x{b:02X}' for b in struct.pack('<I', value)[:3])
            return f"A: {opcode}, Адрес: {operand} -> {bytes_hex}"
        return str(instr)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', help='Путь к YAML файлу с программой')
    parser.add_argument('output_file', help='Путь для сохранения результата')
    parser.add_argument('--test', action='store_true', help='Режим тестирования')

    args = parser.parse_args()

    try:
        with open(args.input_file, encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)

        assembler = Assembler()
        intermediate = assembler.parse_yaml(yaml_content)

        num_commands = len(intermediate)
        binary_code = assembler.assemble_to_binary(intermediate)

        if args.test:
            print("Промежуточное представление:")
            print("=" * 50)
            for i, instr in enumerate(intermediate):
                print(f"Инструкция {i}: {assembler.format_instruction(instr)}")
            print("=" * 50)
            print(f"Число ассемблированных команд: {num_commands}")
        else:
            with open(args.output_file, 'wb') as f:
                f.write(binary_code)
            print(f"Число ассемблированных команд: {num_commands}")

    except FileNotFoundError:
        print(f"Ошибка: файл {args.input_file} не найден")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Ошибка парсинга YAML: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"Ошибка: отсутствует поле {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()