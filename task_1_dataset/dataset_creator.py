from openpyxl import Workbook
import pandas as pd
import random

def read_male_names_with_both_patronymics(filename: str) -> tuple[dict, list]:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = []
            names_only = []
                
            for line in file:
                line = line.strip()
                if line and ':' in line:
                    name_part, patronymics_part = line.split(':', 1)
                    name = name_part.strip()
                    names_only.append(name)
                        
                    patronymics = patronymics_part.split(',')
                    if len(patronymics) >= 2:
                        data.append({
                            'male': patronymics[0].strip(),
                            'female': patronymics[1].strip()
                        })
            return data, names_only
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return [], []

def read_surnames(filename: str) -> list:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            surnames = []
            for line in file:
                line = line.strip()
                if line and ',' in line:
                    male_surname, female_surname = line.split(',', 1)
                    surnames.append({
                        'male': male_surname.strip(),
                        'female': female_surname.strip()
                    })
            return surnames
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return []

def read_simple_list(filename: str) -> list[dict]:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return []
    
def create_full_name(names: list, surnames: dict, patronymics: dict, gender: str) -> dict:
    full_name = {}
    if gender == 'male':
        full_name['surname'] = (random.choice(surnames)['male'])
        full_name['first_name'] = random.choice(names)
        full_name['patronymic'] = (random.choice(patronymics)['male'])
        return full_name
    elif gender == 'female':
        full_name['surname'] = (random.choice(surnames)['female'])
        full_name['first_name'] = random.choice(names)
        full_name['patronymic'] = (random.choice(patronymics)['female'])
        return full_name
    else: 
        raise ValueError
    
def create_passport_number() -> str:
    series = f"{random.randint(10, 99)} {random.randint(10, 99)}"
    number = f"{random.randint(100000, 999999)}"
    return f"{series} {number}"

def create_snils_number() -> str:
    part1 = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100, 999)}"
    part1_digits = part1.replace('-', '')
    checksum = 0
    for i in range(9):
        checksum += int(part1_digits[i]) * (9 - i)
    part2 = checksum % 101
    if part2 == 100 or part2 == 101:
        part2 = '00'
    if len(str(part2)) == 1:
        part2 = f"0{part2}"
    
    return f"{part1} {part2}"

def __main__():
    names_w_patronymics_file = 'lists/male_names_with_patronymics.txt'
    female_names_file = 'lists/female_names.txt'
    surnames_file = 'lists/surnames.txt'

    # patronymics, male_names = read_male_names_with_both_patronymics(names_w_patronymics_file)
    # female_names = read_simple_list(female_names_file)
    # surnames = read_surnames(surnames_file)

    # print(create_full_name(female_names, surnames, patronymics, 'female'))
    num = create_snils_number()
    print(num)

if __name__ == "__main__":
    __main__()


    




