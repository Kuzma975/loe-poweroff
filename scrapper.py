#!python

import requests

def reed_of_tags(data):
  return data.replace('<p>', '').replace('</p>', '').replace('<div>', '').replace('<b>', '').replace('</b>', '').replace('</div>', '').replace('\.', '')

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
  return find_specific_time(data, 'до')

def print_outage_time(begins, ends):
  for i, t in enumerate(begins):
    print(f"{begins[i]} - {ends[i]}")

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
  print_outage_time(get_time_from(today_group), get_time_till(today_group))
# print(tomorrow_item)
# print(tomorrow_group)
# print(get_time_from(tomorrow_group))
# print(get_time_till(tomorrow_group))
print('\n'.join(tomorrow_item[0:2]))
if tomorrow_group:
  print_outage_time(get_time_from(tomorrow_group), get_time_till(tomorrow_group))
