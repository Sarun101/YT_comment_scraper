import os
import shutil
import pandas as pd

RAW = 'Newcomments.csv'
MASTER = 'comments_filtered.csv'

# load
df = pd.read_csv(RAW, encoding='utf-8', on_bad_lines='skip')
df = df.dropna(subset=['text'])
df['text'] = df['text'].astype(str)
df = df.drop_duplicates(subset='text').reset_index(drop=True)
print('loaded', len(df))

def sub(pattern, repl):
    df['text'] = df['text'].str.replace(pattern, repl, regex=True)

# curly quotes, dashes and ellipsis to plain ascii first
sub(r'[\u2018\u2019\u201a\u201b]', "'")
sub(r'[\u201c\u201d\u201e]', '"')
sub(r'[\u2013\u2014]', '-')
sub(r'\u2026', '...')

# keep only ascii, devanagari, joiners and whitespace
sub(r'[^\x20-\x7E\u0900-\u097F\u200c\u200d\s]', '')

# joiners only stay next to devanagari
sub(r'(?<![\u0900-\u097F])[\u200c\u200d]|[\u200c\u200d](?![\u0900-\u097F])', '')

# whitespace
sub(r'\s+', ' ')
df['text'] = df['text'].str.strip()

# drop rows with no english or devanagari letters
df = df[df['text'].str.contains(r'[A-Za-z\u0900-\u097F]', regex=True)]
df = df.drop_duplicates(subset='text').reset_index(drop=True)
print('cleaned', len(df))

# drop anything already in the master
has_master = os.path.exists(MASTER)
if has_master:
    shutil.copy2(MASTER, MASTER + '.bak')   # backup first
    old = pd.read_csv(MASTER, encoding='utf-8', usecols=['text'],
                      dtype=str, keep_default_na=False, on_bad_lines='skip')
    seen = set(old['text'])
    df = df[~df['text'].isin(seen)]
print('new unique', len(df))

# append, header only if the master doesn't exist yet
df.to_csv(MASTER, mode='a', header=not has_master, index=False, encoding='utf-8')
print('appended to', MASTER)