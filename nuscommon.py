# Devices, from (DeviceId >> 28)
device_names = {
    0x10: 'Wii',
    0x30: 'DSi',
    0x40: 'Old3DS',
    0x48: 'New3DS',
    0x50: 'WiiU',
}

device_codenames = {
    0x10: 'rvl',
    0x30: 'twl',
    0x40: 'ctr',
    0x48: 'ktr',
    0x50: 'wup',
    # wupv also exists, but is handled separately
}

# --------------------------------------------------------------------------- #
# SOAP Templates
soap_templates = {'request': {}, 'response': {}}

# SOAP Requests
soap_templates['request']['header'] = '''<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                   xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                   xmlns:nus="urn:nus.wsapi.broadon.com">
<SOAP-ENV:Body>
'''

soap_templates['response']['footer'] = '</SOAP-ENV:Body></SOAP-ENV:Envelope>'

# SOAP Responses
soap_templates['response']['header'] = '''<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<soapenv:Body>
'''

soap_templates['response']['footer'] = '</soapenv:Body></soapenv:Envelope>'
