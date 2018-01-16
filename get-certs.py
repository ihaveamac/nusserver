#!/usr/bin/env python3

import hashlib
import sys

import requests

with requests.get('http://nus.cdn.c.shop.nintendowifi.net/ccs/download/0004003000008F02/cetk') as r:
    with open('certs/ctr-ticket1.cert', 'wb') as f:
        cert = r.content[0x350:0x650]
        cert_hash = hashlib.sha256(cert).hexdigest()
        expected = '65a4cf5bee3dcb60c8fe3a9f15e7a240f83764e74d172cbebd4881611621cc75'
        if cert_hash != expected:
            print('Hash for ctr-ticket1 mismatch.')
            print('Expected:', expected)
            print('Result:', cert_hash)
            sys.exit(1)
        f.write(cert)

    with open('certs/ctr-ticket2.cert', 'wb') as f:
        cert = r.content[0x650:0xA50]
        cert_hash = hashlib.sha256(cert).hexdigest()
        expected = '62690ec04c629d0838bbdf65c5a6b09a54942c870e015573cf7d58f259fe36fa'
        if cert_hash != expected:
            print('Hash for ctr-ticket2 mismatch.')
            print('Expected:', expected)
            print('Result:', cert_hash)
            sys.exit(1)
        f.write(cert)

    # WiiU uses the same certs
    with open('certs/wup-ticket1.cert', 'wb') as f:
        cert = r.content[0x350:0x650]
        # no hash check since it's identical from above
        f.write(cert)

    with open('certs/wup-ticket2.cert', 'wb') as f:
        cert = r.content[0x650:0xA50]
        # no hash check since it's identical from above
        f.write(cert)

with requests.get('http://nus.cdn.wup.shop.nintendo.net/ccs/download/0000000700000002/cetk') as r:
    with open('certs/wupv-ticket1.cert', 'wb') as f:
        cert = r.content[0x5A4:0x9A4]
        cert_hash = hashlib.sha256(cert).hexdigest()
        expected = 'f606090f38c11626333a2a9b8bdcd590286683b7154ad8c67c58f5ab7560a3e6'
        if cert_hash != expected:
            print('Hash for wupv-ticket1 mismatch.')
            print('Expected:', expected)
            print('Result:', cert_hash)
            sys.exit(1)
        f.write(cert)

    with open('certs/wupv-ticket2.cert', 'wb') as f:
        cert = r.content[0x2A4:0x5A4]
        cert_hash = hashlib.sha256(cert).hexdigest()
        expected = '6c6c63935f77e6e0ead3eaa6a06ee408cf0e0edcaee94a30e876c632aa01a8ef'
        if cert_hash != expected:
            print('Hash for wupv-ticket2 mismatch.')
            print('Expected:', expected)
            print('Result:', cert_hash)
            sys.exit(1)
        f.write(cert)
