import requests
import os

channelIDs = []
with open('creators.txt','r',encoding='utf-8') as f:
    for line in f:
        channelIDs.append(line.strip())

API_KEY = os.environ.get('YT_API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3'

# batch lookup
ids = list(channelIDs)
subs = {}

for i in range(0, len(ids), 50):
    batch = ids[i:i + 50]
    res = requests.get(f'{BASE_URL}/channels', params={
        'part': 'statistics',
        'id': ','.join(batch),
        'key': API_KEY
    })
    
    data = res.json()
    if res.status_code != 200:
        print('Error: ',data['error']['message'])
        break

    if res.status_code != 200:
        print(data['error']['message'])
        break

    for item in data.get('items', []):
        stats = item['statistics']
        subs[item['id']] = int(stats.get('subscriberCount', 0))  # hidden counts become 0

# sort
ranked = sorted(subs.items(), key=lambda x: x[1], reverse=True)

# save
with open('ranked_creators.txt', 'w', encoding='utf-8') as f:
    for channel_id, count in ranked:
        f.write(f'{channel_id},{count}\n')

print(ranked[:5])
    
