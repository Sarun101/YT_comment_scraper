import os
import requests
import time


API_KEY = os.environ.get('YT_API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3'
VIDEO_ID = ''
creatorName = '@BishwoGhising'
count = 0

response_creator = requests.get(f'{BASE_URL}/channels',params = {
    'part' : 'contentDetails',    
    'forHandle': creatorName,
    'key': API_KEY    
})

data = response_creator.json()
playlistID = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

videos = []
page_token = None
while True:
    params = {
        'part': 'contentDetails',
        'playlistId': playlistID,
        'key': API_KEY,
        'maxResults': 100
    }
    
    if page_token:
        params['pageToken']= page_token
        
    response_playlist = requests.get(f'{BASE_URL}/playlistItems',params= params)

    video_details = response_playlist.json()

    for item in video_details.get('items',[]):
        content_details = item['contentDetails']
        video_id = content_details['videoId']
        videos.append(video_id)
        
    
    page_token = video_details.get('nextPageToken')
    
    if page_token == None:
        break
    
for videoID in videos:
    response_video = requests.get(f'{BASE_URL}/commentThreads',params={
            'part': 'snippet,replies',
            'videoId': videoID,
            'key': API_KEY,
            'maxResults': 100,
            'textFormat': 'plainText'
        })
        
    video_comment_details = response_video.json()
    for comment in video_comment_details['items']:
        count+=1
        print(count,comment['snippet']['topLevelComment']['snippet']['textDisplay'])
        
        if(comment['snippet']['totalReplyCount']>0):
            count+=1
            for reply in comment['replies']['comments']:
                print('reply: ',reply['snippet']['textDisplay'])
                
