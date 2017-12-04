#!/usr/bin/env python3

import csv
import glob
import os
import requests
import sys

regions = {
    'USA': 'E',
    'EUR': 'P',
    'JPN': 'J',
    'CHN': 'C',
    'KOR': 'K',
    'TWN': 'T',
    'AUS': 'A',
}

if len(sys.argv) < 3:
    sys.exit('{} <ninupdates-url> <region>'.format(sys.argv[0]))

tidlist = []
req = requests.get(sys.argv[1].replace('reports', 'titlelist') + '&reg=' + regions[sys.argv[2].upper()] + '&soap=1&csv=1')
for row in csv.reader(req.text.split('\n')):
    if len(row):
        if row[0] != 'TitleID':
            if row[1] == sys.argv[2].upper():
                tidlist.append((row[0], row[2].rsplit(' ')[-1][1:]))

tidlist.sort(key=lambda x: int(x[0], 16))
for t in tidlist:
    print(','.join(str(x) for x in t))
