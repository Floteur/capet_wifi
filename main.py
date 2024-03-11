import requests
import time
from ping3 import ping
import socket
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress

import asciichartpy as acp

TIMEOUT = 2
TIMEOUT_NB = 5
TIMEOUT_PING = 0.5
PING_HISTORY_SIZE=100

class HTTPAdapterWithSocketOptions(requests.adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.socket_options = kwargs.pop("socket_options", None)
        super(HTTPAdapterWithSocketOptions, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.socket_options is not None:
            kwargs["socket_options"] = self.socket_options
        kwargs["timeout"] = TIMEOUT
        super(HTTPAdapterWithSocketOptions, self).init_poolmanager(*args, **kwargs)

interface = "wlp6s0"  # "wlp0s20f0u5"
adapter = HTTPAdapterWithSocketOptions(socket_options=[(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, interface.encode('utf-8'))])
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

def is_connected():
    start = time.time()
    try:
        for _ in range(TIMEOUT_NB):
            ms=ping('1.1.1.1', interface=interface, timeout=TIMEOUT_PING)
            tmp =  ms!= None
            if tmp:
                return True, 0,ms*1000
        return False, start,None
    except Exception as e:
        return False, start,None

def reconnect():
    timestamp = int(time.time() * 1000)
    data = {
        'username': f'PAY/{timestamp}@wifirst.net',
        'password': f'{timestamp}',
        'success_url': 'https://portal-front.wifirst.net/subscription/landing_page/3426973',
        'error_url': 'https://portal-front.wifirst.net/offers/connect-error',
        'update_session': '0',
    }
    session.post('https://wireless.wifirst.net/goform/HtmlLoginRequest', data=data)

console = Console()


ping_history=[0] * PING_HISTORY_SIZE
def generate_panel(status:str, reconnect_time:float=None) -> Panel:
    if status == "connected":
        title = f"[green]Connected[/green]\nPing: {ping_history[-1]:.2f} ms"
    elif status == "disconnected":
        title = "[red]Disconnected[/red]"
    else:  # status == "reconnecting"
        title = "[red]Reconnecting...[/red]"
        if reconnect_time is not None:
            title += f"\nReconnected in {reconnect_time:.2f} seconds"

    return Panel(
        acp.plot(ping_history, {"height": 10, "min": 0}), title=title, expand=False
    )

def add_history(x:float=None):
    global ping_history
    if x is None:
        x=float("nan")
    ping_history=ping_history[-PING_HISTORY_SIZE:]+[x]

with Live() as live:
    connected = True
    while True:
        while connected:
            time.sleep(0.5)
            connected, reconnect_start,ping_ms = is_connected()
            if ping_ms is not None:
                add_history(ping_ms)
                live.update(generate_panel("connected"))
        add_history()
        live.update(generate_panel("disconnected"))
        while not connected:
            try:
                reconnect()
                connected, _,_ = is_connected()
            except:
                time.sleep(0.1)
        reconnect_end = time.time()
        reconnect_time = reconnect_end - reconnect_start
        live.update(generate_panel("reconnecting", reconnect_time))
