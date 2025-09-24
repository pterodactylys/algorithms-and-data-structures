import time

from src import dataset_creator as creator

def __main__():
    names_w_patronymics_file = 'lists/male_names_with_patronymics.txt'
    female_names_file = 'lists/female_names.txt'
    surnames_file = 'lists/surnames.txt'
    print("Введите количество записей для генерации (например, 1000000):")
    num_records = int(input())
    start = time.time()
    print(f"Генерация датасета на {num_records} строк...")
    creator.create_dataset(num_records, names_w_patronymics_file, female_names_file, surnames_file,
                            'dataset.xlsx')
    end = time.time()
    length = round(end - start, 3)
    print(f"Датасет сгенерирован и сохранён в dataset.xlsx, Это заняло {length} секунд")

if __name__ == "__main__":
    __main__()
