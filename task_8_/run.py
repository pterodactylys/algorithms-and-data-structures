#!/usr/bin/env python3
"""
Скрипт для запуска приложения
"""
import sys
import subprocess
from pathlib import Path

def main():
    # Проверка наличия main.py
    main_file = Path(__file__).parent / "main.py"
    
    if not main_file.exists():
        print("Ошибка: main.py не найден в текущей директории!")
        sys.exit(1)
    
    try:
        # Запуск приложения
        subprocess.run([sys.executable, str(main_file)], check=True)
    except KeyboardInterrupt:
        print("\nПриложение закрыто пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
