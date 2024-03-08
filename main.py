import requests
import random
import logging
import string
import datetime
import subprocess
import schedule
import time
from urllib import request

interface="wlp6s0"
def random_mac():
    subprocess.call(["sudo","ip","link","set","dev",interface,"down"])
    subprocess.call(["sudo","macchanger","-a",interface])
    subprocess.call(["sudo","ip","link","set","dev",interface,"up"])
    subprocess.call(["nmcli","d","wifi","connect","Valence Briffaut"])

TOKEN_PAGE = "https://wireless.wifirst.net/index.txt"
session=requests.Session()
def get_token():
    token = session.get(TOKEN_PAGE).text
    logging.info(f'Fetched token: {token}')
    return token

def randomstring(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

COUNT=5
def reconnect():
    global COUNT
    if COUNT<2:
        COUNT+=1
    else:
        random_mac()
        COUNT=0
    mail=randomstring(10)+'@chibre.bahaha'
    json_data = {
        'fragment_id': 19666,
        'box_token': get_token(),
        'end_user': {
            'email': mail,
            'first_name': 'firstname',
            'last_name': 'lastname',
            'phone_number': '+33 6 04 41 05 51',
            'password': '123Azerty',
            'password_confirmation': '123Azerty',
            'cgu': True,
        },
        'offer': {
            'id': 10434,
            'price': '12.9',
            'is_recurring': True,
            'currency': 'eur',
            'locales': {
            },
            'signature': 'U2FsdGVkX19mButKWY+AOotv0OzszXztP5wJIHP09tRP7LmN6oPabDuDXyPL5v0/\nTNwWY9j/J43qJ5+iQWbreg==',
            'internal_name': 'Liberté 12,90€ x2 devices',
            'available': True,
            'tax_type': {
                'name': 'TVA',
                'rate': '0.2',
                'id': 10005,
            },
            'items': [
                {
                    'quantity': '1.0',
                    'duration_quantity': '1.0',
                    'duration_unit': 'month',
                    'duration_limit_month': None,
                    'initial_period_quantity_algorithm': None,
                    'product_definition_type': 'WebRightsProductDefinition',
                    'product_definition_id': 1797,
                    'max_usage': 2,
                    'id': 10434,
                },
            ],
        },
        'email': mail,
        'first_name': 'firstname',
        'last_name': 'lastname',
        'phone_number': '+33 6 04 41 05 51',
        'password': '123Azerty',
        'password_confirmation': '123Azerty',
        'cgu': True,
    }

    session.post('https://portal-front.wifirst.net/api/end_users', json=json_data)
    in2days=datetime.datetime.now()#+datetime.timedelta(days=2)
    timestamp=int(in2days.timestamp()*1000)
    data = {
        'username': f'PAY/{timestamp}@wifirst.net',
        'password': f'{timestamp}',
        'success_url': 'https://portal-front.wifirst.net/subscription/landing_page/3421047',
        'error_url': 'https://portal-front.wifirst.net/offers/connect-error',
        'update_session': '0',
    }

    session.post('https://wireless.wifirst.net/goform/HtmlLoginRequest',  data=data)
    print("reconnected")

def check_connection():
    # flolep.fr
    try:
        m=request.urlopen('http://8.8.8.8', timeout=5)
        return not "wifirst" in m.url
    except: 
        return False

reconnect()
while True:
    time.sleep(1)
    if not check_connection():
        reconnect()
        time.sleep(2)
