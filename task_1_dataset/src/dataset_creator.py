import pandas as pd
import random
from src import medical_information as md

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
        full_name['Фамилия'] = (random.choice(surnames)['male'])
        full_name['Имя'] = random.choice(names)
        full_name['Отчество'] = (random.choice(patronymics)['male'])
        return full_name
    elif gender == 'female':
        full_name['Фамилия'] = (random.choice(surnames)['female'])
        full_name['Имя'] = random.choice(names)
        full_name['Отчество'] = (random.choice(patronymics)['female'])
        return full_name
    else: 
        raise ValueError

def generate_citizenship_simple(ru_prob: float, by_prob: float, kz_prob: float) -> str:
    total = ru_prob + by_prob + kz_prob
    if abs(total - 1.0) > 0.001:
        raise ValueError(f"Сумма вероятностей должна быть равна 1.0, получено {total}")
    
    rand = random.random()
    
    if rand < ru_prob:
        return 'RU'
    elif rand < ru_prob + by_prob:
        return 'BY'
    else:
        return 'KZ'
    
def create_passport_number(country) -> str:
    if country == 'RU':
        series = f"{random.randint(10, 99)} {random.randint(10, 99)}"
        number = f"{random.randint(100000, 999999)}"
        return f"{series} {number}"
    elif country == 'BY':
        series = f"{random.randint(10, 99)}"
        number = f"{random.randint(1000000, 9999999)}"
        return f"{series} {number}"
    elif country == 'KZ':
        series = f"{random.randint(10, 99)}"
        number = f"{random.randint(100000, 999999)}"
        return f"{series} {number}"

def create_snils_number(country: str) -> str:
    if country == 'RU':
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
    
    elif country == 'BY':
        return "Гражданин РБ"
    elif country == "KZ":
        return "Гражданин РК"

def create_bank_card_number(payment_system:str, bank_name: str) -> str:
    payment_systems = {
        'VISA': '4', 
        'MasterCard': '5',
        'Mir': '2'
    }
    if payment_system in payment_systems:
        prefix = payment_systems[payment_system]
        length = 16
    else:
        raise ValueError("Unknown payment system")
    banks = {
        'Sberbank': '04',
        'Tinkoff': '16',
        'VTB': '41',
        'Alfa-Bank': '35',
        'Gazprombank': '22',
        'Raiffeisenbank': '36',
        'Otkritie': '45',
        'Promsvyazbank': '20',
        'Rosbank': '43',
        'UniCredit Bank': '40'
    }
    if bank_name in banks:
        prefix += banks[bank_name]
    else:
        raise ValueError("Unknown bank")
    unique_part_length = length - len(prefix) - 1
    unique_part = ''.join(random.choices('0123456789', k=unique_part_length))
    partial_number = prefix + unique_part

    def luhn_check_digit(number: str) -> str:
        total = 0
        reverse_digits = number[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 0:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        check_digit = (10 - (total % 10)) % 10
        return str(check_digit)
    
    partial_number += luhn_check_digit(partial_number)
    formatted_number = ' '.join(partial_number[i:i + 4] for i in range(0, len(partial_number), 4))
    return formatted_number


def create_client(gender: str, names: list, surnames: dict, patronymics: dict, 
                  bank_name: str, payment_system: str, country: str) -> dict:
    client = {}
    client.update(create_full_name(names, surnames, patronymics, gender))
    client.update({
        'Паспортные данные': create_passport_number(country),
        'СНИЛС': create_snils_number(country),
    })
    medical_information = md.create_random_patient_profile()
    client.update(medical_information)
    client.update({
        'Карта оплаты': create_bank_card_number(payment_system, bank_name)
    })

    return client

def create_dataset(number_of_clients: int, names_w_patronymics_file: str,
                    female_names_file: str, surnames_file: str, output_file: str) -> None:
    patronymics, male_names = read_male_names_with_both_patronymics(names_w_patronymics_file)
    female_names = read_simple_list(female_names_file)
    surnames = read_surnames(surnames_file)
    clients = []
    for _ in range(number_of_clients):
        gender = random.choice(['male', 'female'])
        payment_system = random.choice(['VISA', 'MasterCard', 'Mir'])
        bank = random.choice(['Sberbank', 'Tinkoff', 'VTB', 'Alfa-Bank', 'Gazprombank', 
                              'Raiffeisenbank', 'Otkritie', 'Promsvyazbank', 'Rosbank', 'UniCredit Bank'])
        country = generate_citizenship_simple(0.7, 0.2, 0.1)
        if gender == 'male':
            clients.append(create_client(gender, male_names, surnames, patronymics, bank, payment_system, country))
        else:
            clients.append(create_client(gender, female_names, surnames, patronymics, bank, payment_system, country))

    df = pd.DataFrame(clients)
    #adjust columns width
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = (max_length + 2) * 1.1
            worksheet.column_dimensions[column_letter].width = adjusted_width





