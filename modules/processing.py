#!python
# -*- coding: utf-8 -*-

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

def find_group(data, group_id):
  group_line = f"Група {group_id}"
  group = next((line for line in data if group_line in line), None)
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

def get_time_intervals_from_group(data):
  return [i.replace(' до ', '-').replace(' ', '').replace(',', '').replace('.', '') if ':' in i else None for i in data.split('з')[1:]]

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
