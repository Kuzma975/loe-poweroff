import os

basedir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(basedir, "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
CALENDARS_FILE = os.path.join(DATA_DIR, "calendars.json")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "brilliant-forge-176916-0d06b0e3c78e.json")

LOE_URL = "https://api.loe.lviv.ua/api/menus?page=1&type=photo-grafic"
GROUP_ID = "5.1"
INTERESTING_ITEMS = ["Today", "Tomorrow"]
