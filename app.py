import os
import requests
import time
import csv

API_KEY = os.environ["YT_API_KEY"]
VIDEO_ID = "l9VxSMFMlKI"
BASE = "https://www.googleapis.com/youtube/v3"
count = 0
# get the chat id
r = requests.get(f"{BASE}/videos", params={
    "part": "liveStreamingDetails", "id": VIDEO_ID, "key": API_KEY})
data = r.json()


livechat_id = data['items'][0]['liveStreamingDetails']['activeLiveChatId']


page_token = None
f = open('comments.csv','a',newline= None,encoding='utf-8-sig')
writer = csv.writer(f)

while True:
    
    params={
        'liveChatId' : livechat_id,
        'part' : 'snippet',
        'key' : API_KEY
    }
    if page_token:
        params['pageToken'] = page_token
    r2 = requests.get(f'{BASE}/liveChat/messages',params=params)
    

    comments = r2.json()
    
    if r2.status_code != 200:
        print("stopped:", r2.text)
        break

    for message in comments.get('items',[]):
        snippet_details = message.get('snippet',{})
        text_details = snippet_details.get('textMessageDetails',{})
        text = text_details.get('messageText')
        if text:
            count += 1
            writer.writerow([text])
    f.flush()
    
    page_token = comments.get('nextPageToken')
    time.sleep(comments['pollingIntervalMillis']/1000)