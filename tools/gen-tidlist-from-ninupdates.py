#!/usr/bin/env python3

import csv
import glob
import os
import sys

if len(sys.argv) < 3:
    sys.exit('{} <ninupdates-csv> <region>'.format(sys.argv[0]))

tidlist = []
with open(sys.argv[1], 'r') as f:
    for row in csv.reader(f):
        if row[0] != 'TitleID':
            if row[1] == sys.argv[2].upper():
                tidlist.append((row[0], row[2].rsplit(' ')[-1][1:]))

tidlist.sort(key=lambda x: int(x[0], 16))
for t in tidlist:
    print(','.join(str(x) for x in t))
