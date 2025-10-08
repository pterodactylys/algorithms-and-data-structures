import time
import os
import json

from src import dataset_creator as creator

def show_main_menu():
    """Показывает главное меню и возвращает выбор пользователя"""
    print('\n' + '='*60)
    print('    Генератор синтетического датасета "Платная поликлиника"')
    print('='*60)
    print("1. Сгенерировать датасет с текущими настройками")
    print("2. Сгенерировать датасет с изменением настроек")
    print("3. Редактировать конфигурацию")
    print("4. Показать текущую конфигурацию")
    print("5. Выйти")
    
    while True:
        choice = input("\nВыберите действие (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 5.")

# Удалена функция show_configuration_menu() - логика упрощена

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

def show_current_config():
    """Показывает текущую конфигурацию без создания файлов"""
    try:
        config_data = creator.load_config_from_json('src/config.json')
        
        print(json.dumps(config_data, ensure_ascii=False, indent=2))
        
        # Показываем краткую сводку
        print(f"\nКраткая сводка:")
        print(f"• Вероятности гражданства: {len(config_data.get('citizenship_probabilities', {}))} стран")
        print(f"• Банки: {len(config_data.get('banks_weights', {}))} банков")
        print(f"• Платежные системы: {len(config_data.get('payment_system_probabilities', {}))} систем")
        
    except FileNotFoundError:
        print("Файл конфигурации не найден. Будут использованы настройки по умолчанию.")
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")


def main():
    names_w_patronymics_file = 'lists/male_names_with_patronymics.txt'
    female_names_file = 'lists/female_names.txt'
    surnames_file = 'lists/surnames.txt'
    
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            # Генерация с текущими настройками
            num_records = get_number_of_records()
            print(f"\nЗапуск генерации {num_records} записей с текущими настройками...")
            start = time.time()
            creator.create_dataset(num_records, names_w_patronymics_file, female_names_file, 
                                  surnames_file, 'dataset.xlsx', edit_config=False)
            end = time.time()
            length = round(end - start, 3)
            print(f"\nДатасет сгенерирован и сохранён в dataset.xlsx")
            print(f"Время генерации: {length} секунд")
                
        elif choice == '2':
            # Генерация с изменением настроек
            num_records = get_number_of_records()
            print(f"\nЗапуск генерации {num_records} записей с редактированием конфигурации...")
            start = time.time()
            creator.create_dataset(num_records, names_w_patronymics_file, female_names_file, 
                                  surnames_file, 'dataset.xlsx', edit_config=True)
            end = time.time()
            length = round(end - start, 3)
            print(f"\nДатасет сгенерирован и сохранён в dataset.xlsx")
            print(f"Время генерации: {length} секунд")
                
        elif choice == '3':
            # Редактирование конфигурации без генерации
            print("\nПереход в редактор конфигурации...")
            creator.edit_config_interactively()
            print("Возврат в главное меню...")
            
        elif choice == '4':
            # Показ текущей конфигурации
            print("\nТекущая конфигурация:")
            show_current_config()
                
        elif choice == '5':
            # Выход
            print("Программа завершена.")
            break

def __main__():
    main()

if __name__ == "__main__":
    __main__()