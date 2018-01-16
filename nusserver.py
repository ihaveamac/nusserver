#!/usr/bin/env python3

import nuscommon
import nusconfig

import base64
import csv
import http.server
import os
import time
from lxml import etree
from math import *


# mostly based on http://stackoverflow.com/questions/24500752/how-can-i-read-exactly-one-response-chunk-with-pythons-http-client
def get_chunk_size(rfile):
    size_str = rfile.read(2)
    while size_str[-2:] != b'\r\n':
        size_str += rfile.read(1)
    return int(size_str[:-2], 16)


def get_chunk_data(rfile, size):
    data = rfile.read(size)
    rfile.read(2)
    return data


def roundup(n, a):
    return ceil(n / a) * a


# "simple element"
def se(name, value, fmt='{1}'):
    return '<{0}>fmt</{0}>'.replace('fmt', fmt).format(name, value)


class UpdateHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<p>nusserver is running!</p>')
        if self.path.startswith('/resethash'):
            device, region = self.path[11:18].lower().split('/', 2)
            titlehash = self.get_titlehash(device, region, True)
            self.wfile.write('<p>Reset titlehash for {} {}<br>New hash: {}</p>'.format(device, region, titlehash).encode('utf-8'))
        self.wfile.write(b'<p>Saved titlehashes (click one to reset if randomly generated)<ul>')
        for d in self._titlehashes.items():
            for r in d[1].items():
                self.wfile.write('<li>{}/{}: '.format(d[0], r[0]).encode('utf-8'))
                if nusconfig.titlehash[d[0]][r[0]] == 'RANDOM':
                    self.wfile.write('<a href="/resethash/{}/{}">'.format(d[0], r[0]).encode('utf-8'))
                self.wfile.write(r[1].encode('utf-8'))
                if nusconfig.titlehash[d[0]][r[0]] == 'RANDOM':
                    self.wfile.write(b'</a>')
        self.wfile.write(b'</ul></p>')
        return

    _titlehashes = {}
    _certs = {}

    def get_titlehash(self, device, region, force_regen=False):
        device = device.lower()
        region = region.lower()
        cfg_titlehash = nusconfig.titlehash[device][region]
        if cfg_titlehash == 'RANDOM':
            if device not in self._titlehashes:
                self._titlehashes[device] = {}
            if force_regen or region not in self._titlehashes[device]:
                self.log_message('Generating random TitleHash for {} {}'.format(device, region.upper()))
                self._titlehashes[device][region] = os.urandom(16).hex().upper()
            return self._titlehashes[device][region]
        else:
            return cfg_titlehash

    def _load_certs(self, device):
        device = device.lower()
        if device not in self._certs:
            self.log_message('Loading certs for ' + device)
            self._certs[device] = []
            with open('certs/{}-ticket1.cert'.format(device), 'rb') as f:
                self._certs[device].append(base64.b64encode(f.read(0x300)).decode('utf-8'))
            with open('certs/{}-ticket2.cert'.format(device), 'rb') as f:
                self._certs[device].append(base64.b64encode(f.read(0x400)).decode('utf-8'))

    def do_POST(self):
        data = b''
        if self.headers['transfer-encoding'] == 'chunked':
            while True:
                chunk_size = get_chunk_size(self.rfile)
                if chunk_size == 0:
                    break
                else:
                    chunk_data = get_chunk_data(self.rfile, chunk_size)
                    data += chunk_data
        else:
            size = int(self.headers['content-length'])
            data = self.rfile.read(size)

        if self.path.startswith('/nus'):
            namespace = 'nus'
        elif self.path.startswith('/ecs'):
            namespace = 'ecs'
        else:
            self.log_message('Unknown path: ' + self.path)
            self.send_response(501)
            self.end_headers()
            return

        xmlroot = etree.fromstring(data)
        xmlaction = xmlroot[0][0]
        # lazy way to get the action
        action_name = xmlaction.tag.rsplit('}', 1)[-1]
        req_version = xmlaction.find(namespace + ':Version', xmlroot.nsmap).text
        req_deviceid = int(xmlaction.find(namespace + ':DeviceId', xmlroot.nsmap).text)
        req_messageid = xmlaction.find(namespace + ':MessageId', xmlroot.nsmap).text
        if namespace == 'nus':
            req_regionid = xmlaction.find(namespace + ':RegionId', xmlroot.nsmap).text

        try:
            device_identifier = (req_deviceid >> 28) & 0xF8
            if device_identifier == 0x50:
                req_virtualdevicetype = xmlaction.find(namespace + ':VirtualDeviceType', xmlroot.nsmap)
                if req_virtualdevicetype is not None:
                    if req_virtualdevicetype.text == '7':
                        device_identifier = 0x60

            device_name = nuscommon.device_names[device_identifier]
            device_codename = nuscommon.device_codenames[device_identifier]
        except KeyError:
            self.log_error('Unknown device with ID {0} (0x{0:x}) requested {1}'.format(req_deviceid, action_name))
            self.send_response(501)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/xml;charset=utf-8')
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()

        self.log_message('Device {} requesting {}'.format(device_name, action_name))

        resp = nuscommon.soap_templates['response']['header']
        # the nus namespace (in the req to the real NetUpdateSOAP) looks
        #   like it needs to be exactly "urn:{namespace}.wsapi.broadon.com".
        # otherwise the error is like:
        #   "org.xml.sax.SAXException: Invalid element in com.broadon.wsapi.{namespace}.GetSystemTitleHashRequestType - Version"
        # in this case I'm responding with the same one provided by the
        #   console. it probably expects this.
        resp += '<{}Response xmlns="{}">'.format(action_name, xmlroot.nsmap[namespace])
        resp += se('Version', req_version)
        resp += se('DeviceId', req_deviceid)
        resp += se('MessageId', req_messageid)
        resp += se('TimeStamp', floor(time.time() * 1000))
        resp += se('ErrorCode', 0)

        # /nus/services/NetUpdateSOAP
        if action_name == 'GetSystemTitleHash':
            try:
                titlehash = self.get_titlehash(device_codename, req_regionid)
            except KeyError:
                self.log_error('Failed to get TitleHash for {} {}'.format(device_name, req_regionid))
                return
            resp += '<TitleHash>{}</TitleHash>'.format(titlehash)
            self.log_message('Returning TitleHash {}'.format(titlehash))

        elif action_name == 'GetSystemCommonETicket':
            self._load_certs(device_codename)
            for tid in xmlaction.findall(namespace + ':TitleId', xmlroot.nsmap):
                with open(os.path.join(nusconfig.cdn_directory[device_codename], tid.text, 'cetk'), 'rb') as f:
                    resp += se('CommonETicket', base64.b64encode(f.read(0x350)).decode('utf-8'))

            for c in self._certs[device_codename]:
                resp += se('Certs', c)

        # /nus/services/NetUpdateSOAP
        elif action_name == 'GetSystemUpdate':
            try:
                titlehash = self.get_titlehash(device_codename, req_regionid)
            except KeyError:
                self.log_error('Failed to get TitleHash for {} {}'.format(device_name, req_regionid))
                return
            resp += se('ContentPrefixURL', nusconfig.content_prefix_url[device_codename])
            resp += se('UncachedContentPrefixURL', nusconfig.content_prefix_url[device_codename])
            with open('tidlist/{}-{}.csv'.format(device_codename, req_regionid)) as c:
                for row in csv.reader(c):
                    resp += '<TitleVersion>'
                    resp += se('TitleId', row[0])
                    resp += se('Version', row[1])
                    # it seems FsSize and TMDSize don't matter here. it may be
                    #   checked, or it may not. either way, the 3DS seems to
                    #   download and install the contents just fine.
                    # resp += se('FsSize', roundup(int(row[2]), 0x4000))
                    resp += se('FsSize', 0)
                    resp += se('TicketSize', 848)
                    # resp += se('TMDSize', int(row[4]) + 0x700)
                    resp += se('TMDSize', 0)
                    resp += '</TitleVersion>'
            resp += se('UploadAuditData', 1)
            resp += se('TitleHash', titlehash)

        # /ecs/services/ECommerceSOAP
        elif action_name == 'GetAccountStatus':
            resp += se('ServiceStandbyMode', 'false')
            resp += se('AccountStatus', 'R')  # wat?
            resp += se('ServiceURLs', se('Name', 'ContentPrefixURL')
                       + se('URI', nuscommon.default_ecommercesoap_urls['ContentPrefixURL'][device_codename]))
            resp += se('ServiceURLs', se('Name', 'UncachedContentPrefixURL')
                       + se('URI', nuscommon.default_ecommercesoap_urls['UncachedContentPrefixURL'][device_codename]))
            resp += se('ServiceURLs', se('Name', 'SystemContentPrefixURL')
                       + se('URI', nusconfig.content_prefix_url[device_codename]))
            resp += se('ServiceURLs', se('Name', 'SystemUncachedContentPrefixURL')
                       + se('URI', nusconfig.uncached_content_prefix_url[device_codename]))
            resp += se('ServiceURLs', se('Name', 'EcsURL')
                       + se('URI', nuscommon.default_ecommercesoap_urls['EcsURL'][device_codename]))
            resp += se('ServiceURLs', se('Name', 'IasURL')
                       + se('URI', nuscommon.default_ecommercesoap_urls['IasURL'][device_codename]))
            resp += se('ServiceURLs', se('Name', 'CasURL')
                       + se('URI', nuscommon.default_ecommercesoap_urls['CasURL'][device_codename]))
            resp += se('ServiceURLs', se('Name', 'NusURL')
                       + se('URI', 'http://{0.address}:{0.port}/nus/services/NetUpdateSOAP'.format(nusconfig)))

        resp += '</{}Response>'.format(action_name)

        resp += nuscommon.soap_templates['response']['footer']

        final_resp = '{:x}\r\n'.format(len(resp)) + resp + '\r\n0\r\n\r\n'

        self.wfile.write(final_resp.encode('utf-8'))
        return


if __name__ == '__main__':
    print('Starting')
    print('Reset random titlehashes at: http://{}:{}/'.format(nusconfig.address, nusconfig.port))
    server = http.server.HTTPServer(('', nusconfig.port), UpdateHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\rEnding')
