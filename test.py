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
print(gcal.add_outage_event(service, CAL_ID, start_dt, end_dt))