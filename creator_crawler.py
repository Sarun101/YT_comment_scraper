import os
import requests
import time

API_KEY = os.environ.get('YT_API_KEY')
BASE_URL = 'https://www.googleapis.com/youtube/v3'
ChannelID = set()
Handles = set()
keywords = [
    # general
    "Nepali YouTube channels",
    "नेपाली च्यानल",
    "Nepali vlog",
    "Nepali vlogger",
    "Nepali creators 2026",
    "Nepal YouTubers",

    # news and current affairs
    "Nepali news live",
    "Nepal news today",
    "आजको समाचार",
    "Kantipur",
    "Setopati",
    "Online Khabar",
    "Ratopati",
    "Nepali political analysis",
    "Nepal explained",

    # entertainment
    "Nepali comedy",
    "Nepali funny videos",
    "Nepali short film",
    "Nepali web series",
    "Nepali movie full",
    "Nepali podcast",
    "Nepali stand-up comedy",

    # music
    "Nepali songs",
    "नेपाली गीत",
    "Nepali lok geet",
    "Nepali pop",
    "Nepali rap",
    "Nepali lo-fi",
    "Nepali band live",

    # education and tech
    "Nepali tech YouTuber",
    "Learn programming in Nepali",
    "Nepali coding tutorial",
    "CSIT tutorial Nepali",
    "Nepali philosophy",
    "दर्शन",
    "Nepali motivation",
    "Nepali self improvement",
    "Nepali book review",

    # lifestyle
    "Nepali food",
    "Nepali cooking",
    "Nepal travel vlog",
    "Nepal trekking",
    "Kathmandu street food",
    "Nepali gym",
    "Nepali fitness",
]
count = 0

# crawl
for keyword in keywords:
    page_token = None
    pages = 0
    while True:
        params = {
            'part': 'snippet',
            'regionCode': 'NP',
            'maxResults': 50,
            'type': 'channel',
            'relevanceLanguage': 'ne',
            'key': API_KEY,
            'q': keyword
        }
        if page_token:
            params['pageToken'] = page_token
        creator = requests.get(f'{BASE_URL}/search', params=params)
        creator_name = creator.json()

        if creator.status_code != 200:
            print(creator_name['error']['message'])
            break

        for item in creator_name.get('items', []):
            count += 1
            channel_id = item['snippet']['channelId']
            name = item['snippet']['title']
            print(name)
            ChannelID.add(channel_id)

        pages += 1
        page_token = creator_name.get('nextPageToken')
        if not page_token or pages >= 2:
            break

# save
print(len(ChannelID))
with open('creators.txt', 'a', encoding='utf-8') as f:
    for channel_id in ChannelID:
        f.write(channel_id + '\n')