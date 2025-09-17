from openpyxl import Workbook
import pandas as pd
import random

names_w_patronymics_file = 'lists/male_names_with_patronymics.txt'
female_names_file = 'lists/female_names.txt'
surnames_file = 'lists/surnames.txt'

def read_male_names_with_both_patronymics(filename: str) -> tuple[dict, list]:
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

def read_surnames(filename: str) -> list:
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

def read_simple_list(filename: str) -> list[dict]:
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]
    
patronymics, male_names = read_male_names_with_both_patronymics(names_w_patronymics_file)
female_names = read_simple_list(female_names_file)
surnames = read_surnames(surnames_file)



