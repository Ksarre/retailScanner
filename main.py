from typing import List
from threading import Thread, Timer
from requests import get, post, put, patch, delete, options, head
import winsound
import schedule
import time
import webbrowser

timer = 5

# TODO: move to config file
request_data = [
    {
        "site": "bestbuy",
        "headers": {"sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "max-age=0"
                    },
        "url": "https://www.bestbuy.com/site/computer-cards-components/video-graphics-cards/abcat0507002.c?id=abcat0507002&qp=gpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%203070%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%203080%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%203090"
    },
    {
        "site": "newegg",
        "url": "https://www.newegg.com/p/pl?d=rtx+3000&N=100007709%20601357261%20600494828&isdeptsrh=1&PageSize=96",
        "headers": {}
    },
    {
        "site": "amazon",
        "url": "https://www.amazon.com/MSI-GeForce-RTX-3080-10G/dp/B08HR7SV3M",
        "headers": {}
    },
    {
        "site": "amazon",
        "url": "https://www.amazon.com/ASUS-Graphics-DisplayPort-Military-Grade-Certification/dp/B08HH5WF97",
        "headers": {}
    },

    {
        "site": "amazon",
        "url": "https://www.amazon.com/EVGA-10G-P5-3897-KR-GeForce-Technology-Backplate/dp/B08HR3Y5GQ",
        "headers": {}
    },
    {
        "site": "amazon",
        "url": "https://www.amazon.com/EVGA-10G-P5-3881-KR-GeForce-GAMING-Cooling/dp/B08HR6FMF3",
        "headers": {}
    }
]

request_methods = {
    'get': get,
    'post': post,
    'put': put,
    'patch': patch,
    'delete': delete,
    'options': options,
    'head': head,
}


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def async_request(method, *args, callback=None, timeout=10, **kwargs):
    """Makes request on a different thread, and optionally passes response to a
    `callback` function when request returns.
    """
    method = request_methods[method.lower()]
    if callback:
        def callback_with_args(response, *args, **kwargs):
            callback(response)
        kwargs['hooks'] = {'response': callback_with_args}
    kwargs['timeout'] = timeout
    thread = Thread(target=method, args=args, kwargs=kwargs)
    thread.start()


def alarm_trigger(content: str, site=None, url=None):
    # parse html for IN STOCK
    # if true, trigger an alarm

    val = content.find('Add to Cart')

    str = site + ': '

    if val != -1:
        print(str + 'IN STOCK!!!')
        try:
            winsound.PlaySound('./media/alarm.wav')
        except Exception as e:
            print(e)
        webbrowser.open(url)
    else:
        print(str + 'Not in stock.')


def hit_endpoints():
    for data in request_data:
        site = data.get('site')
        url = data.get('url')

        def alarm_lambda(r, s=site, u=url): return alarm_trigger(
            str(r.content), s, u) if r.status_code >= 200 or r.status_code < 300 else print(
            f"Error {r.status_code}: {r.content}")
        async_request("get", data.get('url'),
                      callback=alarm_lambda,
                      headers=data.get('headers'))


if __name__ == '__main__':
    schedule.every(5).seconds.do(hit_endpoints)
    while True:
        schedule.run_pending()
        time.sleep(1)
