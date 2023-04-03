import requests
from urllib.parse import urlencode, unquote
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

f=open("key.txt")               # Upbit Accoung Key Open
lines = f.readlines()
access_key = lines[0].strip()          # access key
secret_key = lines[1].strip()          # secret key
f.close()

# 현재가가 이전 종가보다 3틱이상 떨어졌다면 그때부터 count
# count 3이면 매수



def DIS_CHART_DATA(coin_name):
  url_1 = "https://api.upbit.com/v1/candles/" ## url
  url_time = "minutes/" ## 분봉
  url_num = "5?" ## 15분
  url_coin = "market="+coin_name+"&" ## coin 종류
  url_count = "count=2" ## 과거 차트 개수
  url = url_1+url_time+url_num+url_coin+url_count ## "https://api.upbit.com/v1/candles/minutes/15?market=KRW-XRP&count=40"

  response = requests.request("GET", url)

  json_response = json.loads(response.text)
  ttmp=0

  for i in json_response:
    #print(i['candle_date_time_kst']) ## str
    #print(i['trade_price'])  ## float
    ttmp = i['trade_price']
    
      
  return ttmp

#바로 이전 종가
cnt = 0
while 1:
  print("이전 종가 : {}, 현재가격 {}".format(DIS_CHART_DATA(coin), pyupbit.get_current_price(coin)))
  # 최근 5분봉 종가와 현재가랑 비교해서 종가에서 3원 이상 떨어지면
  if (DIS_CHART_DATA(coin)-2) >= pyupbit.get_current_price(coin):
    cnt+=1
    print(str(pyupbit.get_current_price(coin))+" 구매 count = {}".format(cnt))
    
    # count 값이 3이 되면
    if cnt == 3:
        print(str(pyupbit.get_current_price(coin))+"원에 구매 주문완료!")
        break
  time.sleep(0.1)


# if DIS_CHART_DATA(coin) > pyupbit.get_current_price(coin):
#   print("buy")
# elif DIS_CHART_DATA(coin) <= pyupbit.get_current_price(coin):
#   print("no")
# else :
#   print("none")

