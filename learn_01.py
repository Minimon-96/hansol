from platform import machine
import pyupbit
import time
import requests
import json
import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote
from datetime import datetime
from logging import handlers
import logging
today_ymd=datetime.today().strftime("%Y%m%d")

now = datetime.now()
real_time = now.strftime('%Y-%m-%d %H:%M:%S') 

coin = "KRW-XRP"       # Coin Symbol


url_1 = "https://api.upbit.com/v1/candles/" ## url
url_time = "minutes/" ## 분봉
url_num = "15?" ## 15분
url_coin = "market="+coin+"&" ## coin 종류
url_count = "count=100" ## 과거 차트 개수
url = url_1+url_time+url_num+url_coin+url_count ## "https://api.upbit.com/v1/candles/minutes/15?market=KRW-XRP&count=40"

response = requests.request("GET", url)

json_response = json.loads(response.text)

ttmp=1.0
for json in json_response:
    print("{} / {}".format(json['candle_date_time_kst'],json['trade_price'] ))
    #print(json['candle_date_time_kst']) ## str
    #print(json['trade_price'])  ## float

    #if json['trade_price'] > ttmp:
        #   ttmp = json['trade_price']

