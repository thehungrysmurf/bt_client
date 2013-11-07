import requests

payload = {'title': 'title_value', 'infohash': 'infohash_value'}
r = requests.get("https://github.com/timeline.json", params=payload)
print r.text
