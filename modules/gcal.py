#!python

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service(creds_file):
  creds = service_account.Credentials.from_service_account_file(
    creds_file, scopes=SCOPES
  )
  return build('calendar', 'v3', credentials=creds)

def print_available_calendars(service):
    print("📋 Шукаю доступні календарі...")
    
    # Отримуємо список
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        
        for calendar_entry in calendar_list['items']:
            cal_name = calendar_entry.get('summary', 'Без назви')
            cal_id = calendar_entry.get('id')
            access_role = calendar_entry.get('accessRole')
            
            print(f"---")
            print(f"📅 Назва: {cal_name}")
            print(f"🆔 ID: {cal_id}")
            print(f"🔑 Права доступу: {access_role}")
            
            if access_role == 'reader':
                print("⚠️ УВАГА: Бот має лише права на читання! Треба дати права 'Make changes'.")
        
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

# --- Виклик (десь у main.py) ---
# service = get_calendar_service()
# print_available_calendars(service)

def get_or_create_public_calendar(service, calendar_name="💡 Графік відключень (Група 5.1)"):
    # 1. Спершу перевіряємо, чи ми вже створили такий календар раніше
    # (Найкраще зберігати ID створеного календаря в config.py або state.json)
    
    # Але для прикладу пройдемось по списку існуючих:
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_entry in calendar_list['items']:
            if calendar_entry.get('summary') == calendar_name:
                print(f"✅ Календар знайдено: {calendar_entry['id']}")
                return calendar_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # 2. Якщо не знайшли — створюємо новий
    print("🆕 Створюю новий календар...")
    calendar_body = {
        'summary': calendar_name,
        'timeZone': 'Europe/Kiev',
        'description': 'Автоматичний графік відключень світла'
    }
    
    created_calendar = service.calendars().insert(body=calendar_body).execute()
    new_cal_id = created_calendar['id']
    print(f"🆔 ID нового календаря: {new_cal_id}")

    # 3. РОБИМО ЙОГО ПУБЛІЧНИМ (Тільки читання)
    # Це дозволяє будь-кому з ID підписатися на нього
    rule = {
        'scope': {'type': 'default'}, # default = public
        'role': 'reader'              # тільки читання
    }
    
    try:
        service.acl().insert(calendarId=new_cal_id, body=rule).execute()
        print("🌍 Календар став публічним (доступним за посиланням/ID)")
    except Exception as e:
        print(f"⚠️ Помилка налаштування доступу: {e}")

    return new_cal_id

def add_outage_event(service, calendar_id, start_dt, end_dt):
    event = {
        'summary': '💡 Відключення світла',
        'description': 'За графіком львівобленерго (автоматично)',
        'start': {
            'dateTime': start_dt.isoformat(), # формат datetime об'єкта
            'timeZone': 'Europe/Kiev',
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Europe/Kiev',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 15}, # Сповіщення за 15 хв
                {'method': 'popup', 'minutes': 60}, # Сповіщення за годину
            ],
        },
        'colorId': '11', # Червоний колір (можна підібрати інший)
    }

    event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Подію створено: {event_result.get('htmlLink')}")
    
    # ПОВЕРТАЄМО ID, щоб зберегти його в базу!
    return event_result['id']