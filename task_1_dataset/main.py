import time
import os

from src import dataset_creator as creator

def show_main_menu():
    """Показывает главное меню и возвращает выбор пользователя"""
    print('\n' + '='*60)
    print('    Генератор синтетического датасета "Платная поликлиника"')
    print('='*60)
    print("1. Сгенерировать датасет")
    print("2. Редактировать конфигурацию")
    print("3. Показать текущую конфигурацию")
    print("4. Выйти")
    
    while True:
        choice = input("\nВыберите действие (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 4.")

def show_configuration_menu():
    """Показывает меню конфигурации"""
    print('\n' + '='*40)
    print('    РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ')
    print('='*40)
    print("1. Изменить параметры перед генерацией")
    print("2. Генерировать с текущими настройками")
    print("3. Вернуться в главное меню")
    
    while True:
        choice = input("\nВыберите действие (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 3.")

def get_number_of_records():
    """Запрашивает у пользователя количество записей для генерации"""
    while True:
        try:
            num_records = input("\nВведите количество записей для генерации (например, 100000): ").strip()
            num_records = int(num_records)
            if num_records <= 0:
                print("Ошибка: количество записей должно быть положительным числом!")
                continue
            return num_records
        except ValueError:
            print("Ошибка: введите целое число!")


def main():
    names_w_patronymics_file = 'lists/male_names_with_patronymics.txt'
    female_names_file = 'lists/female_names.txt'
    surnames_file = 'lists/surnames.txt'
    
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            config_choice = show_configuration_menu()
            
            if config_choice == '1':
                num_records = get_number_of_records()
                print(f"\nЗапуск генерации {num_records} записей с редактированием конфигурации...")
                start = time.time()
                creator.create_dataset(num_records, names_w_patronymics_file, female_names_file, 
                                      surnames_file, 'dataset.xlsx', edit_config=True)
                end = time.time()
                length = round(end - start, 3)
                print(f"\nДатасет сгенерирован и сохранён в dataset.xlsx")
                print(f"Время генерации: {length} секунд")
                
            elif config_choice == '2':
                num_records = get_number_of_records()
                print(f"\nЗапуск генерации {num_records} записей с текущими настройками...")
                start = time.time()
                creator.create_dataset(num_records, names_w_patronymics_file, female_names_file, 
                                      surnames_file, 'dataset.xlsx', edit_config=False)
                end = time.time()
                length = round(end - start, 3)
                print(f"\nДатасет сгенерирован и сохранён в dataset.xlsx")
                print(f"Время генерации: {length} секунд")
                
            elif config_choice == '3':
                continue
                
        elif choice == '2':
            print("\nПереход в редактор конфигурации...")
            creator.edit_config_interactively()
            print("Возврат в главное меню...")
            
        elif choice == '3':
            print("\nТекущая конфигурация:")
            creator.create_dataset(0, names_w_patronymics_file, female_names_file, 
                                 surnames_file, 'temp.xlsx', edit_config=False, show_only=True)
            if os.path.exists('temp.xlsx'):
                os.remove('temp.xlsx')
                
        elif choice == '4':
            print("Программа завершена.")
            break

def __main__():
    main()

if __name__ == "__main__":
    __main__()