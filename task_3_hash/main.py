import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext



def parse_excel(file_path):
    df = pd.read_excel(file_path)
    hashes = df["Номер телефона"].tolist()
    known_phone_numbers = list(map(int, df["Unnamed: 2"].tolist()[:5]))
    return hashes, known_phone_numbers

def write_to_txt(file_path, data):
    with open(file_path, 'w') as f:
        for item in data:
            f.write(f"{item}\n")

def read_output(file_path):
    with open(file_path, 'r') as f:
        file = f.readlines()
        file = [line.split(":") for line in file]
        hashes = [line[0] for line in file]
        salt_phones = [line[1][:11] for line in file]
        return hashes, salt_phones

def compute_salt(salt_phones, known_numbers):
    for phone in salt_phones:
        salt = int(phone) - int(known_numbers[0])
        if salt < 0:
            continue
        valid_count = 1
        while (str(int(known_numbers[valid_count]) + salt)) in salt_phones:
            valid_count += 1
            if valid_count == 5:
                return salt
    return 0


def run_hashcat(hashes_file):
    if os.path.exists("hashcat.potfile"):
        os.remove("hashcat.potfile")
    if os.path.exists("output.txt"):
        os.remove("output.txt")
    os.system(f"hashcat -a 3 -m 0 -o output.txt {hashes_file} ?d?d?d?d?d?d?d?d?d?d?d --potfile-disable")


def calculate_raw_numbers(salt, hashcat_output):
    with open(hashcat_output, 'r') as f:
        hashcat_output = f.readlines()
    hashcat_output = [line.strip().split(":") for line in hashcat_output]
    raw_numbers = []
    for i in range(len(hashcat_output)):
        raw_numbers.append(int(hashcat_output[i][1]) - salt)
    with open("raw_numbers.txt", 'w') as f:
        for number in raw_numbers:
            f.write(f"{number}\n")


def main():
    excel_file = 'datass.xlsx'
    hashes_file = 'hashes.txt'
    known_numbers_file = 'known_numbers.txt'
    hashes, known_phone_numbers = parse_excel(excel_file)
    write_to_txt(hashes_file, hashes)
    write_to_txt(known_numbers_file, known_phone_numbers)
    run_hashcat(hashes_file)
    hashes, salt_phones = read_output("output.txt")
    salt = compute_salt(salt_phones, known_phone_numbers)
    print(salt)

from main import parse_excel, write_to_txt, read_output, compute_salt, run_hashcat

class HashcatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hashcat GUI")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.excel_file = tk.StringVar()
        self.hashes_file = "hashes.txt"
        self.known_numbers = []

        tk.Label(root, text="Выберите Excel-файл с данными:", font=("Arial", 11)).pack(pady=10)
        tk.Entry(root, textvariable=self.excel_file, width=50).pack()
        tk.Button(root, text="Обзор...", command=self.browse_excel).pack(pady=5)

        tk.Button(root, text="Запустить hashcat", command=self.run_hashcat_process,
                  bg="#4CAF50", fg="white", width=25).pack(pady=5)

        tk.Button(root, text="Вычислить соль", command=self.calculate_salt,
                  bg="#2196F3", fg="white", width=25).pack(pady=5)
        tk.Button(root, text="Вычислить сырые номера", command=self.calculate_raw_numbers,
                  bg="#2196F3", fg="white", width=25).pack(pady=5)

        tk.Label(root, text="Вывод:", font=("Arial", 11, "bold")).pack(pady=(10, 0))
        self.output_box = scrolledtext.ScrolledText(root, width=70, height=15, state='disabled')
        self.output_box.pack(padx=10, pady=5)

        self.status_var = tk.StringVar(value="Готов")
        self.status_bar = tk.Label(root, textvariable=self.status_var,
                                   bd=1, relief=tk.SUNKEN, anchor='w', font=("Arial", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_excel(self):
        file_path = filedialog.askopenfilename(
            title="Выберите Excel-файл",
            filetypes=[("Excel файлы", "*.xlsx *.xls")]
        )
        if file_path:
            self.excel_file.set(file_path)
            self.set_status(f"Файл выбран: {os.path.basename(file_path)}")

    def log(self, message):
        self.output_box.config(state='normal')
        self.output_box.insert(tk.END, message + "\n")
        self.output_box.see(tk.END)
        self.output_box.config(state='disabled')
        self.root.update_idletasks()

    def set_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

    def run_hashcat_process(self):
        if not self.excel_file.get():
            messagebox.showwarning("Ошибка", "Выберите Excel-файл!")
            return

        try:
            self.set_status("Загрузка данных из Excel...")
            self.log("Загрузка данных из Excel...")
            hashes, self.known_numbers = parse_excel(self.excel_file.get())

            self.set_status("Создание файлов для hashcat...")
            self.log("Создание файлов для hashcat...")
            write_to_txt(self.hashes_file, hashes)
            write_to_txt("known_numbers.txt", self.known_numbers)

            self.set_status("Запуск hashcat...")
            self.log("Запуск hashcat (это может занять время)...")
            run_hashcat(self.hashes_file)

            if not os.path.exists("output.txt"):
                self.set_status("Ошибка")
                self.log("Файл output.txt не найден — hashcat, возможно, не завершился.")
                messagebox.showerror("Ошибка", "Файл output.txt не найден.")
                return

            self.set_status("Hashcat завершён")
            self.log("Hashcat завершил работу. Теперь можно вычислить соль.")
            messagebox.showinfo("Готово", "Hashcat завершён. Теперь можно нажать 'Вычислить соль'.")

        except Exception as e:
            self.set_status("Ошибка")
            self.log(f"Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))

    def calculate_salt(self):
        if not os.path.exists("output.txt"):
            messagebox.showwarning("Ошибка", "Файл output.txt не найден. Сначала запустите hashcat.")
            return

        if not self.known_numbers:
            # Если пользователь запустил программу и сразу нажал "Вычислить соль"
            if not self.excel_file.get():
                messagebox.showwarning("Ошибка", "Выберите Excel-файл для загрузки известных номеров.")
                return
            _, self.known_numbers = parse_excel(self.excel_file.get())

        try:
            self.set_status("Чтение результата...")
            self.log("Чтение результата...")
            hashes, salt_phones = read_output("output.txt")

            self.set_status("Вычисление соли...")
            self.log("Вычисление соли...")
            salt = compute_salt(salt_phones, self.known_numbers)

            self.set_status("Готово")
            self.log(f"Рассчитанная соль: {salt}")
            messagebox.showinfo("Готово", f"Соль найдена: {salt}")

        except Exception as e:
            self.set_status("Ошибка")
            self.log(f"Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))

    def calculate_raw_numbers(self):

        if not self.known_numbers:
            messagebox.showwarning("Ошибка", "Сначала вычислите соль.")
            return

        salt = compute_salt(salt_phones, self.known_numbers)
        calculate_raw_numbers(salt, self.hashcat_output)

        self.set_status("Готово")
        self.log(f"Номера расшифрованы и сохранены в файл raw_numbers.txt")
        messagebox.showinfo("Готово", f"Номера расшифрованы и сохранены в файл raw_numbers.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = HashcatGUI(root)
    root.mainloop()

# 9054775687