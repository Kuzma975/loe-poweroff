#!python
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta, date
import json
import os

def reed_of_tags(data):
  return data.replace('<p>', '').replace('</p>', '').replace('<div>', '').replace('<b>', '').replace('</b>', '').replace('</div>', '')

def reed_of_tail_garbage(data):
  for i, d in enumerate(data):
    data[i] = d.replace('.', '').replace(',', '')
  return data

def get_specific_item(data, item_name):
  item = reed_of_tags(next((item for item in data if item['name'] == item_name), None)['rawHtml'])
  if (item):
    item = item.split('\n')
  return item

def find_group(data, group):
  group = next((line for line in data if group in line), None)
  if group:
    group = group.split(' ')
  return group

def find_specific_time(data, spec):
  times = []
  for index, part in enumerate(data):
    if part == spec:
      times.append(data[index+1])
  return times

def get_time_from(data):
  return find_specific_time(data, 'з')

def get_time_till(data):
  return reed_of_tail_garbage(find_specific_time(data, 'до'))

def print_outage_time(begins, ends):
  for i, t in enumerate(begins):
    print(f"{begins[i]} - {ends[i]}")

def parse_interval(start_str, end_str, target_date):
  time_fmt = '%H:%M'
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
parsed_schedule = []
raw_schedule = []
file_name = "outage.json"

group_number = '5.1'
api_url = "https://api.loe.lviv.ua/api/menus?page=1&type=photo-grafic"
headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

response = requests.get(api_url, headers=headers)
data = response.json()['hydra:member'][0]['menuItems']

today_item = get_specific_item(data, 'Today')
tomorrow_item = get_specific_item(data, 'Tomorrow')


#print(today_item)
today_group = find_group(today_item, "5.1")
tomorrow_group = find_group(tomorrow_item, "5.1")



# print(get_time_from(today_group))
# print(get_time_till(today_group))
print('\n'.join(today_item[0:2]))
if today_group:
  raw_starts = get_time_from(today_group)
  raw_ends = get_time_till(today_group)
  for i, s in enumerate(raw_starts):
    raw_schedule.append({"day": "today", "start": s, "end": raw_ends[i]})
  print_outage_time(raw_starts, raw_ends)
# print(tomorrow_item)
# print(tomorrow_group)
# print(get_time_from(tomorrow_group))
# print(get_time_till(tomorrow_group))
print('\n'.join(tomorrow_item[0:2]))
if tomorrow_group:
  raw_starts = get_time_from(tomorrow_group)
  raw_ends = get_time_till(tomorrow_group)
  for i, s in enumerate(raw_starts):
    raw_schedule.append({"day": "tomorrow", "start": s, "end": raw_ends[i]})
  print_outage_time(raw_starts, raw_ends)
  # print_outage_time(get_time_from(tomorrow_group), get_time_till(tomorrow_group))

for item in raw_schedule:
  current_date = today if item["day"] == "today" else tomorrow
  start_dt, end_dt = parse_interval(item["start"], item["end"], current_date)
  parsed_schedule.append({
    "start": start_dt,
    "end": end_dt
    })

print(len(parsed_schedule))
after_end = False
for i in parsed_schedule:
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

export_data = [
  {
    "start": interval['start'].isoformat(),
    "end": interval['end'].isoformat()
  }
  for interval in parsed_schedule
]
check_for_changes(export_data)
