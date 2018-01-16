# Devices, from (DeviceId >> 28)
device_names = {
    0x10: 'Wii',
    0x30: 'DSi',
    0x40: 'Old3DS',
    0x48: 'New3DS',
    0x50: 'WiiU',
    0x60: 'WiiU vWii',  # 0x60 is not used by Nintendo, but internally in this project
}

device_codenames = {
    0x10: 'rvl',
    0x30: 'twl',
    0x40: 'ctr',
    0x48: 'ktr',
    0x50: 'wup',
    0x60: 'wupv',  # 0x60 is not used by Nintendo, but internally in this project
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

# --------------------------------------------------------------------------- #
# Default ECommerceSOAP URLs
# wupv is not needed here
default_ecommercesoap_urls = {
    'ContentPrefixURL': {
        'ctr': 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download',
        'ktr': 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download',
        'wup': 'http://ccs.cdn.wup.shop.nintendo.net/ccs/download',
    },
    'UncachedContentPrefixURL': {
        'ctr': 'http://ccs.c.shop.nintendowifi.net/ccs/download',
        'ktr': 'http://ccs.c.shop.nintendowifi.net/ccs/download',
        'wup': 'https://ccs.wup.shop.nintendo.net/ccs/download',
    },
    'EcsURL': {
        'ctr': 'https://ecs.c.shop.nintendowifi.net/ecs/services/ECommerceSOAP',
        'ktr': 'https://ecs.c.shop.nintendowifi.net/ecs/services/ECommerceSOAP',
        'wup': 'https://ecs.wup.shop.nintendo.net/ecs/services/ECommerceSOAP',
    },
    'IasURL': {
        'ctr': 'https://ias.c.shop.nintendowifi.net/ias/services/IdentityAuthenticationSOAP',
        'ktr': 'https://ias.c.shop.nintendowifi.net/ias/services/IdentityAuthenticationSOAP',
        'wup': 'https://ias.wup.shop.nintendo.net/ias/services/IdentityAuthenticationSOAP',
    },
    'CasURL': {
        'ctr': 'https://cas.c.shop.nintendowifi.net/cas/services/CatalogingSOAP',
        'ktr': 'https://cas.c.shop.nintendowifi.net/cas/services/CatalogingSOAP',
        'wup': 'https://cas.wup.shop.nintendo.net/cas/services/CatalogingSOAP',
    },
}
