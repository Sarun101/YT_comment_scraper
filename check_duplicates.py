videoURLS = []

with open('done_videos.txt','r',encoding='utf-8') as f:
    for line in f:
        if line.strip():
            videoURLS.append(line)
            

def get_duplicate_items(data):
    values = set()
    for item in data:
        if item in values:
            return True
        values.add(item)
    return False
    
    
    

if (get_duplicate_items(videoURLS)):
    print('Duplicate found')
