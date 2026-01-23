#!python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from config import LOE_URL, GROUP_ID, STATE_FILE, INTERESTING_ITEMS, CALENDARS_FILE, CREDENTIALS_FILE
from modules import scrapper, processing, storage, gcal

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

def get_interval(start, end):
  return f"{start}-{end}"

now = datetime.now()
today = date.today()
tomorrow = today + timedelta(days=1)
storage_file = STATE_FILE
calendars_file = CALENDARS_FILE
stored_data = storage.load_json(storage_file)
calendars_data = storage.load_json(calendars_file)
calendar_service = gcal.get_calendar_service(CREDENTIALS_FILE)
calendars = {}
if not calendars_data:
  print("Populating calendars")
  for group in range(1,7):
    for subgroup in range(1,3):
      group_id = str(group) + "." + str(subgroup)
      calendar_name = f"LOE power outage (group {group_id})"
      calendar_id = gcal.get_or_create_public_calendar(calendar_service, calendar_name)
      calendars.update({group_id: {"calendar_id": calendar_id, "calendar_name": calendar_name}})
      print(f"{calendar_name}: {gcal.get_calendar_link(calendar_id)}")
  storage.save_json(calendars_file, calendars)
else:
  calendars = calendars_data
group_number = GROUP_ID

data = scrapper.fetch_data(LOE_URL)

items = {}
for day in INTERESTING_ITEMS:
  raw_data = processing.get_specific_item(data, day)
  if raw_data:
    for_day = raw_data[0].split(' ')[-1]
    old_data = stored_data.get(for_day, None)
    items.update({for_day: {"raw": raw_data}})
    updated = raw_data[1]
    items[for_day].update({"updated": updated})
    items[for_day].update({"for_day": raw_data[0]})
    items[for_day].update({"groups": {}})
    calendar_changed = True
    if old_data:
      calendar_changed = old_data.get('updated', None) != updated
    for group in range(1,7):
      for subgroup in range(1,3):
        parsed_schedule = dict()
        raw_schedule = []
        group_id = str(group) + "." + str(subgroup)
        calendar_id = calendars.get(group_id).get('calendar_id')
        group_str = processing.find_group(raw_data, group_id)
        current_group = group_str.split(' ')
        intervals = processing.get_time_intervals_from_group(group_str)
        old_group = old_data.get('groups').get(group_id, None) if old_data else None
        # raw_starts = processing.get_time_from(current_group)
        # raw_ends = processing.get_time_till(current_group)
        # raw_schedule = [{"start": s, "end": raw_ends[i]} for i, s in enumerate(raw_starts)]
        # intervals = {f"{i["start"]}-{i["end"]}" for i in raw_schedule}
        raw_schedule = [{"start": i.split('-')[0], "end": i.split('-')[1]} for i in intervals]
        if calendar_changed:
          print("calendar were changed")
          if old_group:
            old_intervals = old_group['intervals'].keys()
            if old_intervals:
              added_intervals, removed_intervals, unchanged_intervals = processing.compare_schedules(old_intervals, intervals)
              for interval in removed_intervals:
                print(f"Removing {interval} interval from {group_id}")
                gcal.remove_outage_event(calendar_service, calendar_id, old_group.get('intervals').get(interval).get('event_id'))
              for interval in added_intervals:
                current_date = today if day == "Today" else tomorrow
                start_time, end_time = interval.split('-')
                start_dt, end_dt = parse_interval(start_time, end_time, current_date)
                event_id = gcal.add_outage_event(calendar_service, calendar_id, start_dt, end_dt, now.isoformat(timespec="seconds"), updated)
                parsed_schedule.update({
                  interval: {
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat(),
                    "event_id": event_id
                  }
                })
              for interval in unchanged_intervals:
                gcal.update_outage_event(calendar_service, calendar_id, old_group.get('intervals').get(interval).get('event_id'), now.isoformat(timespec="seconds"), updated)
                parsed_schedule.update({interval: old_group.get('intervals').get(interval)})
          else:
            for interval in intervals:
              current_date = today if day == "Today" else tomorrow
              start_time, end_time = interval.split('-')
              start_dt, end_dt = parse_interval(start_time, end_time, current_date)
              event_id = gcal.add_outage_event(calendar_service, calendar_id, start_dt, end_dt, now.isoformat(timespec="seconds"), updated)
              parsed_schedule.update({
                interval: {
                  "start": start_dt.isoformat(),
                  "end": end_dt.isoformat(),
                  "event_id": event_id
                }
              })
        else:
          if old_group:
            for interval, i_obj in old_group.get('intervals').items():
              gcal.update_outage_event(calendar_service, calendar_id, i_obj.get('event_id'), now.isoformat(timespec="seconds"), updated)
              parsed_schedule.update({interval: i_obj})



        # current_date = today if day == "Today" else tomorrow
        # for interval in intervals:
        #   start, end = interal.split('-')
        #   start_dt, end_dt = parse_interval(start, end, current_date)
        #   parsed_schedule.update({
        #     interval: {
        #       "start": start_dt,
        #       "end": end_dt
        #     }
        #   })
          # parsed_schedule.append({
          #   "start": start_dt,
          #   "end": end_dt
          # })

        items[for_day]['groups'].update({
          group_id: {
            "raw_group": current_group,
            "intervals": parsed_schedule
            # "raw_schedule": raw_schedule,

            # "parsed_schedule": parsed_schedule
          }
        })
  else:
    print(f"For {day} schedule not found")
storage.save_json(storage_file, items)
print(items)


after_end = False
for k, i in items.get(today.strftime('%d.%m.%Y')).get('groups').get('5.1').get('intervals').items():
  s = datetime.fromisoformat(i["start"])
  e = datetime.fromisoformat(i["end"])
  if s <= now <= e:
    print('Outage')
    time_left = e - now
    print(f'time left: {time_left}')
    minutes = time_left.total_seconds() / 60
    print(f'time left in minutes: {minutes}')
  print(f"starts: {i['start']} -> {i['end']} ({e-s})")
  if after_end and now <= s:
    time_left_till_outage = s - now
    print(f'time left till next outage {time_left_till_outage}')
  if e <= now:
    after_end = True

# export_data = [
#   {
#     "start": interval['start'].isoformat(),
#     "end": interval['end'].isoformat()
#   }
#   for interval in parsed_schedule
# ]
# check_for_changes(export_data)
