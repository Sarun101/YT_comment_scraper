import os
import csv
import requests

rankedIds = []

with open('ranked_creators.txt','r',encoding='utf-8') as f:
    for line in f:
        if line.strip():
            rankedIds.append(line.strip().split(',')[0])

API_KEY = os.environ.get('YT_API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3'
QUOTA = ('quotaExceeded','dailyLimitExceeded')

def reason_of(d):
    return d.get('error',{}).get('errors',[{}])[0].get('reason','')

# resume: videos already finished
done = set()
if os.path.exists('done_videos.txt'):
    with open('done_videos.txt','r',encoding='utf-8') as f:
        done = {l.strip() for l in f if l.strip()}

new_file = not os.path.exists('comments.csv')
out = open('comments.csv', 'a', encoding='utf-8', newline='')
writer = csv.writer(out)
if new_file:
    writer.writerow(['text'])
donef = open('done_videos.txt', 'a', encoding='utf-8')

try:
    for itemID in rankedIds:

        response = requests.get(f'{BASE_URL}/channels/',params=
                                {
                                    'part':'contentDetails',
                                    'key':API_KEY,
                                    'id': itemID
                                }, timeout=20)

        data = response.json()

        if response.status_code!=200:
            print('Error: ',data['error']['message'])
            if reason_of(data) in QUOTA:
                exit()
            continue
        if not data.get('items'):
            print('No data for', itemID)
            continue
        playlistID = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        playlist_token = None
        while True:
            params = {'part': 'contentDetails', 'playlistId': playlistID, 'maxResults': 50,'key':API_KEY}
            if playlist_token:
                params['pageToken'] = playlist_token
            r = requests.get(f'{BASE_URL}/playlistItems',params=params, timeout=20)
            playlist = r.json()
            if r.status_code!=200:
                print('Playlist error: ',playlist['error']['message'])
                if reason_of(playlist) in QUOTA:
                    exit()
                break

            videos = []
            for entry in playlist['items']:
                contentDetails = entry['contentDetails']
                videoID = contentDetails['videoId']
                videos.append(videoID)

            for video in videos:
                if video in done:
                    continue
                video_token = None
                failed = False

                while True:
                    params = {
                        'part':'snippet,replies',
                        'key':API_KEY,
                        'textFormat':'plainText',
                        'maxResults':100,
                        'videoId': video
                    }
                    if video_token:
                        params['pageToken'] = video_token
                    requestVideo = requests.get(f'{BASE_URL}/commentThreads',params=params, timeout=20)
                    videoDetails = requestVideo.json()

                    if requestVideo.status_code!=200:
                        reason = reason_of(videoDetails)
                        print(video, reason)
                        if reason in QUOTA:
                            exit()
                        if reason not in ('commentsDisabled','videoNotFound'):
                            failed = True   # temporary error, retry next run
                        break

                    for comment in videoDetails.get('items',[]):
                        displayComment = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                        writer.writerow([displayComment])

                        replyCount = comment['snippet']['totalReplyCount']
                        if replyCount>0:
                            replies = comment['replies']['comments']
                            for reply in replies:
                                text = reply['snippet']['textDisplay']
                                writer.writerow([text])

                    video_token = videoDetails.get('nextPageToken')
                    if not video_token:
                        break

                if failed:
                    continue

                # video finished, save progress
                out.flush()
                donef.write(video+'\n')
                donef.flush()
                done.add(video)

            playlist_token = playlist.get('nextPageToken')

            if not playlist_token:
                break

except requests.RequestException as e:
    print('Network error, rerun to resume: ', e)
finally:
    out.close()
    donef.close()