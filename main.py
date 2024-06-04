import requests
import datetime
import subprocess
import time
from tqdm import tqdm
import dns.resolver
import re

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
                time.sleep(3)
            time.sleep(1)
    def random_mac(self):
        # subprocess.call(["sudo","ip","link","set","dev",self.name,"down"],timeout=5)
        # time.sleep(0.5)
        # subprocess.call(["sudo","macchanger","-a",self.name],timeout=5)
        # self.new_mac=time.time()
        # time.sleep(0.5)
        # subprocess.call(["sudo","ip","link","set","dev",self.name,"up"],timeout=5)
        # deconection wifi
        subprocess.call(["nmcli","d","disconnect",self.name],timeout=5)
        for _ in tqdm(range(10),desc="Reconnectiong Wifi"):
            try:
                subprocess.call(["nmcli","d","wifi","connect","Valence Briffaut","ifname",self.name],timeout=30)
                # wait until dns query is possible
                for _ in range(30):
                    try:
                        dns_resolver = dns.resolver.Resolver()
                        dns_resolver.timeout = 1
                        dns_resolver.lifetime = 1
                        dns_resolver.resolve("wireless.wifirst.net")
                        return
                    except Exception as e:
                        print(e)
                    time.sleep(1)
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
                # "173.88.8.254"
                count=30
                res=subprocess.check_output(["sudo","-u","flo","nping","-c",str(count),"--rate","10","173.88.8.254","--debug"],stderr=subprocess.DEVNULL,timeout=(count/10)*1.5,encoding="utf-8")
                print(res)
                failed= re.search(r"(?:Failed|Lost): (\d+)",res).group(1)
                int_res=int(failed)
                if "Network is unreachable" in res:
                    self.random_mac()
                    return False
                return int_res>count/3
            return False
        except Exception as e:
            print("EEEEE:",e)
            return False
    def reconnect(self):
        if time.time()-self.last_reco<10 and time.time()-self.new_mac>60:
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
III="wlan0"
# III="wlp10s0"
interface=Interface(III)





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



# interfaces=list(map(Interface,interface_names))
# for index,i in enumerate(interfaces):
#     change_route(i.name)

# time.sleep(1)
# last_interface_connected=None
# try:
#     while True:
#         time.sleep(0.1)
#         if last_interface_connected and last_interface_connected.connected:
#             continue
#         #choose random interface that is connected
#         interfaces_with_internet=[i for i in interfaces if i.connected]
#         if interfaces_with_internet:
#             choosen=random.choice(interfaces_with_internet)
#             #switch interfaces priority
#             change_route(last_interface_connected,choosen)
#             last_interface_connected=choosen
#             print("Switch to",choosen)
# except Exception as e:
#     print(e)
#     for i in interfaces:
#         i.end()
