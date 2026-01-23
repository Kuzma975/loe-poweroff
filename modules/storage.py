#!python

import os
import json

def load_json(file_name):
  if not os.path.exists(file_name):
    return {}
  with open(file_name, 'r', encoding='utf-8') as f:
    return json.load(f)

def save_json(file_name, data):
  with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

def check_for_changes(file_name, new_schedule):
  old_state = load_previous_state(file_name)

  # Отримуємо старий розклад для цієї групи (або пустий список)

    # Порівнюємо (Python вміє порівнювати списки словників)
  if new_schedule != old_state:
    print("⚠️ Увага! Графік змінився!")

        # Тут можна знайти різницю (що додалось, що зникло)
        # ... логіка оновлення календаря ...

        # Оновлюємо та зберігаємо
    save_state(file_name, new_schedule)
  else:
    print("✅ Змін немає, календар чіпати не треба.")
