#!python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
import json
import os
from config import LOE_URL, GROUP_ID, STATE_FILE, INTERESTING_ITEMS
from modules import scrapper, processing

def parse_interval(start_str, end_str, target_date):
  time_fmt = '%H:%M'
  if end_str == '24:00':
    end_str = '23:59'
  t_start = datetime.strptime(start_str, time_fmt).time()
  t_end = datetime.strptime(end_str, time_fmt).time()
  dt_start = datetime.combine(target_date, t_start)
  dt_end = datetime.combine(target_date, t_end)

  if dt_end < dt_start:
    dt_end += timedelta(days=1)
  return dt_start, dt_end

def load_previous_state():
  if not os.path.exists(file_name):
    return {}
  with open(file_name, 'r', encoding='utf-8') as f:
    return json.load(f)

def save_state(data):
  with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

def check_for_changes(new_schedule):
  old_state = load_previous_state()

  # Отримуємо старий розклад для цієї групи (або пустий список)

    # Порівнюємо (Python вміє порівнювати списки словників)
  if new_schedule != old_state:
    print("⚠️ Увага! Графік змінився!")

        # Тут можна знайти різницю (що додалось, що зникло)
        # ... логіка оновлення календаря ...

        # Оновлюємо та зберігаємо
    save_state(new_schedule)
  else:
    print("✅ Змін немає, календар чіпати не треба.")

now = datetime.now()
today = date.today()
tomorrow = today + timedelta(days=1)
file_name = STATE_FILE

group_number = GROUP_ID

data = scrapper.fetch_data(LOE_URL)

items = {}
for day in INTERESTING_ITEMS:
  rawData = processing.get_specific_item(data, day)
  if rawData:
    items.update({day: {"raw": rawData}})
    items[day].update({"updated": rawData[1]})
    items[day].update({"forDay": rawData[0]})
    for group in range(1,7):
      for subgroup in range(1,3):
        parsed_schedule = []
        raw_schedule = []
        groupId = str(group) + "." + str(subgroup)
        current_group = processing.find_group(rawData, groupId)
        raw_starts = processing.get_time_from(current_group)
        raw_ends = processing.get_time_till(current_group)
        raw_schedule = [{"start": s, "end": raw_ends[i]} for i, s in enumerate(raw_starts)]
        current_date = today if day == "Today" else tomorrow
        for interval in raw_schedule:
          start_dt, end_dt = parse_interval(interval["start"], interval["end"], current_date)
          parsed_schedule.append({
            "start": start_dt,
            "end": end_dt
          })

        items[day].update({
          groupId: {
            "rawGroup": current_group,
            "rawSchedule": raw_schedule,
            "parsedSchedule": parsed_schedule
          }
        })
  else:
    print(f"For {day} schedule not found")
print(items)


after_end = False
for i in items.get('Today').get('5.1').get('parsedSchedule'):
  if i["start"] <= now <= i["end"]:
    print('Outage')
    time_left = i['end'] - now
    print(f'time left: {time_left}')
    minutes = time_left.total_seconds() / 60
    print(f'time left in minutes: {minutes}')
  print(f"starts: {i['start']} -> {i['end']} ({i['end']-i['start']})")
  if after_end and now <= i['start']:
    time_left_till_outage = i['start'] - now
    print(f'time left till next outage {time_left_till_outage}')
  if i['end'] <= now:
    after_end = True

# export_data = [
#   {
#     "start": interval['start'].isoformat(),
#     "end": interval['end'].isoformat()
#   }
#   for interval in parsed_schedule
# ]
# check_for_changes(export_data)
