import requests
import random
import logging
import string
import datetime
import subprocess
import time
from tqdm import tqdm
import threading
from ping3 import ping
from faker import Faker
import socket
fake = Faker()
TIMEOUT=5

class HTTPAdapterWithSocketOptions(requests.adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.socket_options = kwargs.pop("socket_options", None)
        super(HTTPAdapterWithSocketOptions, self).__init__(*args, **kwargs)
    def init_poolmanager(self, *args, **kwargs):
        if self.socket_options is not None:
            kwargs["socket_options"] = self.socket_options
        kwargs["timeout"]=TIMEOUT
        super(HTTPAdapterWithSocketOptions, self).init_poolmanager(*args, **kwargs)


interface_names=[
    "wlp6s0",
    # "wlp0s20f0u4"
]

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_number(length):
    return ''.join(random.choices(string.digits, k=length))

class Interface:
    def __init__(self,name:str):
        self.name=name
        self.adapter = HTTPAdapterWithSocketOptions(socket_options=[(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, self.name.encode('utf-8'))])
        self.count=5
        self.connected=True
        self.finish=False
        self.thread=None
        self.run()
    def run(self):
        self.finish=False
        if not self.thread:
            self.thread=threading.Thread(target=self.loop)
            self.thread.start()
    def loop(self):
        while not self.finish:
            if not self.is_connected():
                self.reconnect()
                time.sleep(10)
            time.sleep(0.3)
    def random_mac(self):
        self.connected=False
        subprocess.call(["sudo","ip","link","set","dev",self.name,"down"])
        subprocess.call(["sudo","macchanger","-a",self.name])
        subprocess.call(["sudo","ip","link","set","dev",self.name,"up"])
        for _ in tqdm(range(5),desc="Reconnectiong Wifi"):
            try:
                subprocess.call(["nmcli","d","wifi","connect","Valence Briffaut","ifname",self.name])
                return
            except Exception as e:
                time.sleep(1)
    def is_connected(self):
        try:
            for _ in range(3):
                tmp=ping('1.1.1.1',interface=self.name,timeout=0.5)!=None
                if tmp:
                    self.connected=True
                    return self.connected
            self.connected=False
            return self.connected
        except Exception as e:
            # print("2>",e)
            self.connected=False
            return self.connected
    def create_new_session(self):
        self.session=requests.Session()
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)
    def get_token(self):
        return self.session.get("https://wireless.wifirst.net/index.txt").text
    def reconnect(self):
        if self.count<2:
            self.count+=1
        else:
            self.random_mac()
            self.count=0
        self.create_new_session()
        end_user={
            "mail":random_string(10)+'@gmail.com',
            "phone":f'+33 6 04 {random_number(2)} {random_number(2)} {random_number(2)}',
            "first_name":fake.first_name(),
            "last_name":fake.last_name(),
            "password":random_string(10),
            'cgu': True,
        }
        json_data = {
            'fragment_id': 19666,
            'box_token': self.get_token(),
            'end_user': end_user,
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
            **end_user
        }
        self.session.post('https://portal-front.wifirst.net/api/end_users', json=json_data)
        in2days=datetime.datetime.now()#+datetime.timedelta(days=2)
        timestamp=int(in2days.timestamp()*1000)
        data = {
            'username': f'PAY/{timestamp}@wifirst.net',
            'password': f'{timestamp}',
            'success_url': 'https://portal-front.wifirst.net/subscription/landing_page/3421047',
            'error_url': 'https://portal-front.wifirst.net/offers/connect-error',
            'update_session': '0',
        }
        self.session.post('https://wireless.wifirst.net/goform/HtmlLoginRequest',  data=data)
        print("reconnected")
    def __str__(self) -> str:
        return f"Interface(name='{self.name}', connected={self.connected})"
    def __repr__(self) -> str:
        return f"Interface(name='{self.name}', count={self.count}, connected={self.connected})"
    def end(self):
        self.__del__()
    def __del__(self):
        self.finish = True
        if self.thread:
            print("Deleting",self.name,"...")
            self.thread.join()
            self.thread=None

def change_route(_old:str=None,_new:str=None):
    if isinstance(_old,Interface):
        _old=_old.name
    if isinstance(_new,Interface):
        _new=_new.name
    if _old:
        subprocess.call([
            "sudo",
            "ifmetric",
            str(_old),
            str(100)
        ])
    if _new:
        subprocess.call([
            "sudo",
            "ifmetric",
            str(_new),
            str(10)
        ])

interfaces=list(map(Interface,interface_names))
for index,i in enumerate(interfaces):
    change_route(i.name)

time.sleep(1)
last_interface_connected=None
try:
    while True:
        time.sleep(0.1)
        if last_interface_connected and last_interface_connected.connected:
            continue
        #choose random interface that is connected
        interfaces_with_internet=[i for i in interfaces if i.connected]
        if interfaces_with_internet:
            choosen=random.choice(interfaces_with_internet)
            #switch interfaces priority
            change_route(last_interface_connected,choosen)
            last_interface_connected=choosen
            print("Switch to",choosen)
except Exception as e:
    print(e)
    for i in interfaces:
        i.end()

