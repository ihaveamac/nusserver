#!/usr/bin/env python3

import glob
import os
import sys

if len(sys.argv) < 2:
    sys.exit('{} <dir>'.format(sys.argv[0]))

tidlist = []
for cia in glob.iglob(os.path.join(sys.argv[1], '*.cia')):
    with open(cia, 'rb') as f:
        f.seek(0xC)
        tiksize = int.from_bytes(f.read(4), 'little')
        # tmdsize = int.from_bytes(f.read(4), 'little')
        # f.seek(0x18)
        # size = int.from_bytes(f.read(8), 'little')
        f.seek(0x2F4C)
        tid = f.read(8).hex().upper()
        f.seek(0x2F9C)
        ver = int.from_bytes(f.read(2), 'big')
        # count = int.from_bytes(f.read(2), 'big')
        # f.seek(0x38C4)
        tidlist.append((tid, ver))

tidlist.sort(key=lambda x: int(x[0], 16))
for t in tidlist:
    print(','.join(str(x) for x in t))
