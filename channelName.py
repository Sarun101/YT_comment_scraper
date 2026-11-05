import os
import requests
import csv

API_KEY = os.environ.get('YT_API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3'
channelIDs = []
with open('ranked_creators.txt','r',encoding='utf-8') as f:
    for line in f:
        if line.strip():
            channel = line.strip().split(',')[0]
            channelIDs.append(channel)

channelIDs = list(dict.fromkeys(channelIDs))


def Get(endpoint,params):
    params['key'] = API_KEY
    r = requests.get(f'{BASE_URL}/{endpoint}',params=params)
    return r

out = open('final_list.txt','a',encoding='utf-8',newline='')
writer = csv.writer(out)
writer.writerow(['channelName','country','id'])


for i in range(0,len(channelIDs),50):
    
    batch = channelIDs[i:i+50]
    id_page_token = None
    params = {
        'part': 'snippet',
        'id': ','.join(batch),
        'maxResults':50
    }
    
    if id_page_token:
        params['pageToken'] = id_page_token
    
    r1 = Get('channels',params=params)
    data = r1.json()
    
    for channel in data['items']:
        channelTitle = channel['snippet']['title']
        
        country = channel['snippet'].get('country','')
        finalID = channel['id']
        if country=='NP':
            print(channelTitle,country)
            writer.writerow([channelTitle,country,finalID])
        