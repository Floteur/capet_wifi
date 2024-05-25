import requests
import datetime
import subprocess
import time
from tqdm import tqdm
import dns.resolver

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
session = requests.Session()
retry = Retry(connect=300, backoff_factor=0)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

TIMEOUT=2





# interface_names="wlp6s0"

class Interface:
    def __init__(self,name:str):
        self.name=name
        self.count=5
        self.last_reco=0
        self.new_mac=0
        self.loop()
    def loop(self):
        while True:
            if not self.is_connected():
                print("reconnecting")
                self.reconnect()
            time.sleep(1)
    def random_mac(self):
        subprocess.call(["sudo","ip","link","set","dev",self.name,"down"],timeout=5)
        time.sleep(0.5)
        subprocess.call(["sudo","macchanger","-a",self.name],timeout=5)
        self.new_mac=time.time()
        time.sleep(0.5)
        subprocess.call(["sudo","ip","link","set","dev",self.name,"up"],timeout=5)
        for _ in tqdm(range(10),desc="Reconnectiong Wifi"):
            try:
                subprocess.call(["nmcli","d","wifi","connect","Valence Briffaut","ifname",self.name],timeout=30)
                return
            except Exception as e:
                print("exception:",e)
                time.sleep(1)
    def is_connected(self,nb_time=1):
        try:
            for _ in range(nb_time):
                # DNS_resolver = dns.resolver.Resolver()
                # DNS_resolver.timeout = 1
                # DNS_resolver.lifetime = 1
                # DNS_resolver.resolve("wireless.wifirst.net")
                res=subprocess.check_output(["sudo","-u","flo","nping","-c","10","--rate","5","173.88.8.254","-e",self.name],stderr=subprocess.DEVNULL,timeout=3,encoding="utf-8")
                # print(res)
                return not ("Failed: 0" in res or "Lost: 0" in res) and not "Network is unreachable" in res
            return False
        except Exception as e:
            print("EEEEE:",e)
            return False
    def reconnect(self):
        if time.time()-self.last_reco<5 and time.time()-self.new_mac>60:
            self.random_mac()
        date=datetime.datetime.now()
        timestamp=int(date.timestamp()*1000)
        data = {
            'username': f'PAY/{timestamp}@wifirst.net',
            'password': f'{timestamp}',
            'success_url': 'https://portal-front.wifirst.net/subscription/landing_page/3421047',
            'error_url': 'https://portal-front.wifirst.net/offers/connect-error',
            'update_session': '0',
        }
        try:
            session.post('https://wireless.wifirst.net/goform/HtmlLoginRequest',  data=data,timeout=2)
            print("reconnected")
        except Exception as e:
            print(e)
        self.last_reco=time.time()


III="wlp0s20f0u5"
III="wlp6s0"
# III="wlp10s0"
interface=Interface(III)
