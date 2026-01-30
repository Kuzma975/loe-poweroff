# modules//scrapper.py

import requests

headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

def fetch_data(url):
  retry = True
  retry_count = 3
  while retry:
    retry_count -= 1
    plainJson = requests.get(url, headers=headers).json()
    try:
      if type(plainJson) == type(list()):
        response = plainJson[0]['menuItems']
        return response
      else:
        response = plainJson['hydra:member'][0]['menuItems']
        return response
    except Exception as e:
      print(f"Failed to retrieve schedule {plainJson}: {e}")
    retry = False if retry_count < 1 else True
  return {}