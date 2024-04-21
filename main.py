import requests
import datetime
import subprocess
import time
from tqdm import tqdm
import ping3
import socket

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
session = requests.Session()
retry = Retry(connect=300, backoff_factor=0)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

TIMEOUT=5


class Interface:
    def __init__(self,name:str):
        self.name=name
        self.count=5
        self.last_reco=0
        self.loop()
    def loop(self):
        while True:
            if not self.is_connected():
                self.reconnect()
                time.sleep(10)
            time.sleep(0.3)
    def random_mac(self):
        subprocess.call(["sudo","ip","link","set","dev",self.name,"down"],timeout=5)
        subprocess.call(["sudo","macchanger","-a",self.name],timeout=5)
        subprocess.call(["sudo","ip","link","set","dev",self.name,"up"],timeout=5)
        for _ in tqdm(range(5),desc="Reconnectiong Wifi"):
            try:
                subprocess.call(["nmcli","d","wifi","connect","Valence Briffaut","ifname",self.name],timeout=30)
                return
            except Exception as e:
                time.sleep(1)
    def is_connected(self):
        try:
            for _ in range(3):
                result=socket.getaddrinfo('wireless.wifirst.net',0)
                print(result)
            return False
        except:
            return True
    def reconnect(self):
        if time.time()-self.last_reco<5:
            self.random_mac()
        date=datetime.datetime.now()+datetime.timedelta(days=1)
        timestamp=int(date.timestamp()*1000)
        data = {
            'username': f'PAY/{timestamp}@wifirst.net',
            'password': f'{timestamp}',
            'success_url': 'https://portal-front.wifirst.net/subscription/landing_page/3421047',
            'error_url': 'https://portal-front.wifirst.net/offers/connect-error',
            'update_session': '0',
        }
        try:
            session.post('https://wireless.wifirst.net/goform/HtmlLoginRequest',  data=data)
            print("reconnected")
        except Exception as e:
            print(e)
        self.last_reco=time.time()


interface=Interface("wlp6s0")
