import os
import csv
import requests

rankedIds = []

with open('final_list.txt','r',encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if row:
            rankedIds.append(row[2])

# api keys
API_KEYS = [k.strip() for k in os.environ.get('YT_API_KEYS','').split(',') if k.strip()]
if not API_KEYS:
    print('No keys found in YT_API_KEYS')
    exit()
key_index = 0

BASE_URL = 'https://www.googleapis.com/youtube/v3'
QUOTA = ('quotaExceeded','dailyLimitExceeded')

def reason_of(d):
    return d.get('error',{}).get('errors',[{}])[0].get('reason','')

def api_get(url, params):
    global key_index
    while True:
        params['key'] = API_KEYS[key_index]
        r = requests.get(url, params=params, timeout=20)
        if r.status_code != 200 and reason_of(r.json()) in QUOTA:
            print(f'Key {key_index + 1} out of quota')
            key_index += 1
            if key_index >= len(API_KEYS):
                print('All keys used up, rerun after quota resets')
                exit()
            continue
        return r

# resume: videos already finished
done = set()
if os.path.exists('done_videos.txt'):
    with open('done_videos.txt','r',encoding='utf-8') as f:
        done = {l.strip() for l in f if l.strip()}

# resume: channels already finished
done_channels = set()
if os.path.exists('done_channels.txt'):
    with open('done_channels.txt','r',encoding='utf-8') as f:
        for l in f:
            if l.strip():
                done_channels.add(l.strip().split(',', 1)[0])

new_file = not os.path.exists('Newcomments.csv')
out = open('Newcomments.csv', 'a', encoding='utf-8', newline='')
writer = csv.writer(out)
if new_file:
    writer.writerow(['text'])
donef = open('done_videos.txt', 'a', encoding='utf-8')
donec = open('done_channels.txt', 'a', encoding='utf-8')

try:
    for itemID in rankedIds:

        if itemID in done_channels:
            continue

        response = api_get(f'{BASE_URL}/channels', {
            'part':'contentDetails,snippet',
            'id': itemID
        })

        data = response.json()

        if response.status_code!=200:
            print('Error: ',data['error']['message'])
            continue
        if not data.get('items'):
            print('No data for', itemID)
            continue

        title = data['items'][0]['snippet']['title'].replace('\n', ' ')
        playlistID = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        channel_ok = True
        playlist_token = None
        while True:
            params = {'part': 'contentDetails', 'playlistId': playlistID, 'maxResults': 50}
            if playlist_token:
                params['pageToken'] = playlist_token
            r = api_get(f'{BASE_URL}/playlistItems', params)
            playlist = r.json()
            if r.status_code!=200:
                print('Playlist error: ',playlist['error']['message'])
                channel_ok = False
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
                        'textFormat':'plainText',
                        'maxResults':100,
                        'videoId': video
                    }
                    if video_token:
                        params['pageToken'] = video_token
                    requestVideo = api_get(f'{BASE_URL}/commentThreads', params)
                    videoDetails = requestVideo.json()

                    if requestVideo.status_code!=200:
                        reason = reason_of(videoDetails)
                        print(video, reason)
                        if reason not in ('commentsDisabled','videoNotFound'):
                            failed = True   # temporary error, retry next run
                        break

                    for comment in videoDetails.get('items',[]):
                        displayComment = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                        writer.writerow([displayComment])

                        replyCount = comment['snippet']['totalReplyCount']
                        if replyCount>0:
                            replies = comment.get('replies', {}).get('comments', [])
                            for reply in replies:
                                text = reply['snippet']['textDisplay']
                                writer.writerow([text])

                    video_token = videoDetails.get('nextPageToken')
                    if not video_token:
                        break

                if failed:
                    channel_ok = False
                    continue

                # video finished, save progress
                out.flush()
                donef.write(video+'\n')
                donef.flush()
                done.add(video)

            playlist_token = playlist.get('nextPageToken')

            if not playlist_token:
                break

        # channel finished, save progress
        if channel_ok:
            donec.write(f'{itemID},{title}\n')
            donec.flush()
            done_channels.add(itemID)

except requests.RequestException as e:
    print('Network error, rerun to resume: ', e)
finally:
    out.close()
    donef.close()
    donec.close()