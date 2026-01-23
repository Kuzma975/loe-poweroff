#!python

from config import CREDENTIALS_FILE
from modules import gcal
from datetime import datetime, timedelta

CAL_ID = "e692f7c1bc9cb8d41d166e6d12fedb8cda511445bf7b59ad2b8568d3703c9bf0@group.calendar.google.com"
service = gcal.get_calendar_service(CREDENTIALS_FILE)
print(gcal.print_available_calendars(service))
# print(gcal.get_or_create_public_calendar(service))
# print(gcal.print_available_calendars(service))

now = datetime.now()
start_dt = now + timedelta(minutes=16)
end_dt = now + timedelta(minutes=30)
# print(gcal.add_outage_event(service, 'a93c4194134e952daca3e4f007148643c36ef1257107ff368bf59ddcf898ee5a@group.calendar.google.com', start_dt, end_dt))

def compare_schedules(old_list, new_list):
    # 1. Перетворюємо списки на множини (sets)
    old_set = set(old_list)
    new_set = set(new_list)

    # 2. Знаходимо різницю
    # Те, що є в новій, але немає в старій -> ДОДАЛОСЬ
    added = new_set - old_set
    
    # Те, що є в старій, але немає в новій -> ЗНИКЛО
    removed = old_set - new_set

    # Те, що є в обох -> БЕЗ ЗМІН (перетин множин)
    unchanged = new_set & old_set

    return added, removed, unchanged

# --- ТЕСТУВАННЯ ---

# Старий графік (наприклад, з json файлу)
state_old = [
    "09:00-13:00",
    "18:00-22:00" 
]

# Новий графік (щойно розпарсили, змінився час вечірнього відключення)
state_new = [
    "09:00-13:00",
    "18:00-23:00" # Продовжили на годину
]

added_slots, removed_slots, same_slots = compare_schedules(state_old, state_new)

if not added_slots and not removed_slots:
    print("✅ Змін немає")
else:
    print("⚠️ Увага, зміни в графіку!")
    
    if removed_slots:
        for slot in removed_slots:
            print(f"❌ Скасовано відключення: {slot}")
            # Тут код для видалення з календаря (delete event)

    if added_slots:
        for slot in added_slots:
            print(f"➕ Додано нове відключення: {slot}")
            # Тут код для створення події в календарі (create event)


# Функція для перетворення складних об'єктів у прості рядки для порівняння
def serialize_slots(schedule_list):
    return {f"{s['start'].isoformat()}|{s['end'].isoformat()}" for s in schedule_list}

# Використання
old_set = serialize_slots(old_data_from_json)
new_set = serialize_slots(new_parsed_data)

added = new_set - old_set
# ...далі так само...


# modules/gcal.py
from googleapiclient.discovery import build
# імпорти auth...

class CalendarManager:
    def __init__(self, creds_path, token_path):
        self.service = self._auth(creds_path, token_path)

    def _auth(self, creds, token):
        # Логіка авторизації
        return build('calendar', 'v3', credentials=...)

    def create_event(self, start, end):
        # Логіка створення
        return event_id

    def delete_event(self, event_id):
        # Логіка видалення
        pass

# main.py
from config import URL, STATE_FILE, GROUP_ID, CREDENTIALS_FILE, TOKEN_FILE
from modules import scraper, processing, storage
from modules.gcal import CalendarManager

def main():
    print("🚀 Запуск моніторингу...")

    # 1. Отримуємо дані
    raw_data = scraper.fetch_schedule_data(URL)
    new_schedule = processing.parse_intervals(raw_data)

    # 2. Читаємо старий стан
    old_state = storage.load_state(STATE_FILE)
    old_schedule = [item['interval'] for item in old_state] # спрощено

    # 3. Шукаємо зміни
    added, removed = processing.find_schedule_changes(old_schedule, new_schedule)

    if not added and not removed:
        print("✅ Змін немає.")
        return

    # 4. Якщо є зміни - підключаємо календар
    cal = CalendarManager(CREDENTIALS_FILE, TOKEN_FILE)

    # Видаляємо старі події
    for interval in removed:
        # Треба знайти ID події у old_state за інтервалом
        event_id = ... 
        cal.delete_event(event_id)

    # Створюємо нові
    current_state_objects = []
    for interval in new_schedule: # Проходимо по новому повному списку
        # Якщо це новий інтервал - створюємо подію
        if interval in added:
            event_id = cal.create_event(interval['start'], interval['end'])
            current_state_objects.append({'interval': interval, 'event_id': event_id})
        else:
            # Якщо інтервал старий, треба зберегти старий event_id
            # (тут треба трохи логіки пошуку по old_state)
            pass

    # 5. Зберігаємо новий стан
    storage.save_json(STATE_FILE, current_state_objects)
    print("💾 Стан оновлено.")

if __name__ == "__main__":
    main()


from config import logger # Імпортуємо вже налаштований логер

try:
    logger.info("🚀 Запуск перевірки графіку...")
    # ... твій код ...
    if changes_detected:
        logger.warning(f"⚠️ Знайдено зміни! Додано: {added}, Видалено: {removed}")
    else:
        logger.info("✅ Змін немає.")

except Exception as e:
    # `exc_info=True` додасть повний Traceback помилки в лог (дуже корисно!)
    logger.error(f"🔥 Критична помилка: {e}", exc_info=True)