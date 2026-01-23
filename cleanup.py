#!python

from modules import gcal, storage
from config import CALENDARS_FILE, CREDENTIALS_FILE
from datetime import datetime

calendar_service = gcal.get_calendar_service(CREDENTIALS_FILE)

state_files = [
  "data/state.json",
]
calendars_data = storage.load_json(CALENDARS_FILE)
for file in state_files:
  state = storage.load_json(file)
  for date in state:
    print(f"Working for {date}")
    for group in range(1,7):
      for subgroup in range(1,3):
        group_id = str(group) + '.' + str(subgroup)
        print(f"Group id: {group_id}")
        calendar_id = calendars_data.get(group_id).get('calendar_id')
        print(f"Calendar id: {calendar_id}")
        print(gcal.get_calendar_link(calendar_id))
        # events = calendar_service.events().list(calendarId=calendar_id).execute()
        # for event in events['items']:
        #   print(f"{event['summary']} - {event['status']}")
        #   print(f"❌ Видаляю: {event['summary']} ({event['start'].get('dateTime')}) | Status: {event['status']}")
        #   print(gcal.remove_outage_event(calendar_service, calendar_id, event['id']))
        for interval, i_obj in state.get(date).get('groups').get(group_id).get('intervals').items():
          if i_obj:
            event = calendar_service.events().get(calendarId=calendar_id, eventId=i_obj['event_id']).execute()
            # print(event)
            end_dt = datetime.fromisoformat(event['end'].get('dateTime'))
            start_dt = datetime.fromisoformat(event['start'].get('dateTime'))
            # print(f"Duration: {end_dt-start_dt}")
            # gcal.remove_outage_event(calendar_service, calendar_id, state.get(date).get(group_id).get('intervals').get(interval).get('event_id'))
        # events = calendar_service.events().list(calendarId=calendar_id, showDeleted=True).execute()
        # for event in events['items']:
        #   print(f"{event['summary']} - {event['status']}")

remove_calendar_name = "💡 Графік відключень (Група 5.1)"
calendar_id_old = gcal.get_calendar_id(calendar_service, remove_calendar_name)

print(calendar_id_old)
# gcal.remove_calendar(calendar_service, calendar_id)
# gcal.print_available_calendars(calendar_service)