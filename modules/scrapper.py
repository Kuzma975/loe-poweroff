# modules//scrapper.py

import requests

headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

def fetch_data(url):
  return requests.get(url, headers=headers).json()['hydra:member'][0]['menuItems']