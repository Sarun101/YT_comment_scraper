import re
import csv
import unicodedata
import pandas as pd

try:
    from wordfreq import zipf_frequency   # pip install wordfreq
except ImportError:
    zipf_frequency = None

# load terms
dfOffensive = pd.read_csv('offensive-terms-in-nepali.csv', encoding='utf-8')
taboo = dfOffensive[dfOffensive['IsTaboo'] == 1]


romTerms, nepTerms = [], []
for col in ['RawRom', 'NormRom']:
    romTerms += taboo[col].dropna().astype(str).tolist()
for col in ['RawNep', 'NormNep']:
    nepTerms += taboo[col].dropna().astype(str).tolist()

print(romTerms)
exit()

# normalizer, used on terms and comments alike
LEET = str.maketrans({'@': 'a', '0': 'o', '1': 'i', '3': 'e', '$': 's', '5': 's'})
TOKEN = re.compile(r'[a-z0-9\u0900-\u097F]+')

def base(s):
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r'[\u200c\u200d]', '', s)    # joiners off for matching only
    return s.translate(LEET).strip()

def squash(s):
    return re.sub(r'([a-z])\1+', r'\1', s)  # fuuuck -> fuck

# english collisions
KEEP = {'fuck', 'fucking', 'fucker', 'mc', 'mg'}   # always match
MANUAL_SKIP = {'made', 'stan', 'virgin'}            # always skip in romanized form
ZIPF_MAX = 3.5                                      # higher = more common english word

def too_common(t):
    if t in KEEP:
        return False
    if t in MANUAL_SKIP:
        return True
    return zipf_frequency is not None and zipf_frequency(t, 'en') >= ZIPF_MAX

# build lookup sets once
romNorm = {base(t) for t in romTerms} - {''}
nepNorm = {base(t) for t in nepTerms} - {''}

romSingle = {t for t in romNorm if ' ' not in t}
skipped = sorted(t for t in romSingle if too_common(t))
romSingle -= set(skipped)
print('skipped as english:', skipped)

single = romSingle | {t for t in nepNorm if ' ' not in t}
phrases = {t for t in romNorm | nepNorm if ' ' in t}
fuzzy = {squash(t) for t in romSingle if len(t) >= 4}   # short words stay exact

print(len(single), 'single terms,', len(phrases), 'phrases')

def contains_offensive(text):
    if not isinstance(text, str):
        return False
    tokens = TOKEN.findall(base(text))

    # token match
    for tok in tokens:
        if tok in single or squash(tok) in fuzzy:
            return True

    # phrase match
    if phrases:
        joined = ' ' + ' '.join(tokens) + ' '
        for p in phrases:
            if ' ' + p + ' ' in joined:
                return True
    return False

# label the full dataset
dfData = pd.read_csv('comments_filtered.csv', encoding='utf-8')
dfData = dfData.drop(columns=['isHate', 'ishate'], errors='ignore')   # no duplicate label columns
dfData['ishate'] = dfData['text'].apply(contains_offensive).astype(int)

print(dfData['ishate'].value_counts())

# write with every field quoted so commas in comments can't split columns
dfData.to_csv('comments_labeled.csv', index=False, encoding='utf-8',
              quoting=csv.QUOTE_ALL)
dfData[dfData['ishate'] == 1].to_csv('isHate.csv', index=False, encoding='utf-8',
                                     quoting=csv.QUOTE_ALL)

# check the file reads back with the same shape
check = pd.read_csv('comments_labeled.csv', encoding='utf-8')
print(check.shape == dfData.shape, check['ishate'].isin([0, 1]).all())