import os
import csv
import requests

API_KEY = os.environ.get('YT_API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3'
creators = ['@Jhapalish', '@ratankarki07', '@VTENOfficial', '@SACAROfficial']
count = 0


def get(endpoint, params):
    params['key'] = API_KEY
    r = requests.get(f'{BASE_URL}/{endpoint}', params=params)
    data = r.json()
    if 'error' in data:
        print('API error:', data['error'].get('message'))
        return None
    return data


with open('data_yt.csv', 'a', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    
    for creator in creators:
        data = get('channels', {'part': 'contentDetails', 'forHandle': creator})
        if not data or not data.get('items'):
            print('Channel not found:', creator)
            continue
        playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # collect all video IDs
        videos, page_token = [], None
        while True:
            params = {'part': 'contentDetails', 'playlistId': playlist_id, 'maxResults': 50}
            if page_token:
                params['pageToken'] = page_token
            d = get('playlistItems', params)
            if not d:
                break
            videos += [i['contentDetails']['videoId'] for i in d.get('items', [])]
            page_token = d.get('nextPageToken')
            if not page_token:
                break

        # collect all comments per video
        for vid in videos:
            page_token = None
            while True:
                params = {'part': 'snippet,replies', 'videoId': vid,
                          'maxResults': 100, 'textFormat': 'plainText'}
                if page_token:
                    params['pageToken'] = page_token
                d = get('commentThreads', params)
                if not d:  # comments disabled / error
                    break
                for c in d.get('items', []):
                    top = c['snippet']['topLevelComment']['snippet']['textDisplay']
                    writer.writerow([top])
                    count += 1
                    for r in c.get('replies', {}).get('comments', []):
                        writer.writerow([r['snippet']['textDisplay']])
                        count += 1
                page_token = d.get('nextPageToken')
                if not page_token:
                    break
            print(creator, vid, 'total so far:', count)