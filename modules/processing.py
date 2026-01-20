
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
