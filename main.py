import requests
import random
import logging
import string
import datetime
import subprocess
import time
from pythonping import ping


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
                'en': {
                    'description_1': '<ul><li>Unlimited broadband <strong>Internet</strong></li></ul>',
                    'description_2': '<ul><li><strong>Without commitment</strong></li><li>You can connect 2 devices simultaneously.</li><li>Immediate access</li><li>No cancellation fees</li><li>Payment of the first month prorated</li></ul>',
                    'description_3': 'This offer is without obligation, without cancellation fees and can be activated in a few minutes!',
                    'name': 'Liberty Pack',
                },
                'de': {
                    'description_1': '<ul><li><strong>Bretiband-Internet</strong> unbegrenzt</li></ul>',
                    'description_2': '<ul><li><strong>Ohne Engagement</strong></li><li>Sie können 2 Geräte gleichzeitig anschließen.</li><li>Sofortiger Zugriff</li><li>Ohne Terminierungsentgelte</li><li>Die Zahlung der ersten Monate anteilig</li></ul>',
                    'description_3': 'Dieses Angebot ist unverbindlich, kostenlos und in wenigen Minuten aktivierbar!',
                    'name': 'Freiheit Abo',
                },
                'es': {
                    'description_1': '<ul><li><strong>Internet</strong> ilimitado</li></ul>',
                    'description_2': '<ul><li><strong>Sin compromiso</strong></li><li>Puede conectar 2 dispositivos al mismo tiempo.</li><li>Acceso inmediato</li><li>Sin cargos de terminación</li><li>El pago del 1er mes prorrateado</li></ul>',
                    'description_3': 'Esta oferta es sin compromiso, sin gastos de cancelación y puede activarse en unos minutos.',
                    'name': 'Oferta Libertad',
                },
                'fr': {
                    'description_1': '<ul><li><strong>Internet</strong> haut débit illimité</li></ul>',
                    'description_2': '<ul><li><strong>Sans engagement</strong></li><li>Vous pouvez connecter 2 appareils simultanément.</li><li>Accès immédiat</li><li>Sans frais de résiliation</li><li>Paiement du 1er mois au prorata</li></ul>',
                    'description_3': 'Cette offre est sans engagement, sans frais de résiliation et activable en quelques minutes!',
                    'name': 'Abonnement Liberté',
                },
                'it': {
                    'description_1': None,
                    'description_2': None,
                    'description_3': None,
                    'name': None,
                },
                'nl': {
                    'description_1': '<ul><li><strong>Internet</strong> onbeperkt breedband</li></ul>',
                    'description_2': '<ul><li><strong>zonder inzet</strong></li><li>U kunt 2 apparaten tegelijk aansluiten.</li><li>onmiddellijke toegang</li><li>Zonder opzegging kosten</li><li>Betaling van 1e maand naar rato</li></ul>',
                    'description_3': 'Dit aanbod is vrijblijvend, zonder annuleringskosten en kan in enkele minuten worden geactiveerd!',
                    'name': 'Liberty Pack',
                },
                'pt': {
                    'description_1': None,
                    'description_2': None,
                    'description_3': None,
                    'name': None,
                },
                'zh': {
                    'description_1': '<ul><li>无限宽带<strong>网络</strong> </li></ul>',
                    'description_2': '<ul><li><strong>无需签约</strong></li><li>您可以同时连接2个设备</li><li>立即上网</li><li>无撤销费用</li><li>首月按比例支付</li></ul>',
                    'description_3': '这个优惠是没有义务的，没有取消费用，而且可以在几分钟内激活!',
                    'name': '自由订阅',
                },
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
    try:
        return ping('1.1.1.1',timeout=0.3,count=1).success()
    except Exception as e:
        print("2>",e)
        return False

while True:
    if not check_connection():
        try:
            print('reconnecting')
            reconnect()
            time.sleep(5)
        except Exception as e:
            print("1>",e)
            time.sleep(2)
    time.sleep(1)
