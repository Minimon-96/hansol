from platform import machine
import pyupbit
import time
import math
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


#log settings
#LogFormatter = logging.Formatter('%(asctime)s, %(message)s')
LogFormatter = logging.Formatter('%(message)s')

#handler settings
today_ymd=datetime.today().strftime("%Y%m%d")
LogHandler = handlers.TimedRotatingFileHandler(filename=today_ymd+".log", when='midnight', interval=1, encoding='utf-8')
LogHandler.setFormatter(LogFormatter)
LogHandler.suffix = "%Y%m%d"

#logger set
Logger = logging.getLogger()
Logger.setLevel(logging.INFO)
Logger.addHandler(LogHandler)



upbit =  pyupbit.Upbit(access_key, secret_key)  # Key Reference

# print("Please enter your Coin")
# print("Ex) >> KRW-XRP")
# coin_name = input("Please enter your Coin >> ") 

# 특정 코인의 현재 보유 수량 조회
def DIS_QUAN_COIN(coin_name):
    return  upbit.get_balance(coin_name)        

# 특정 코인의 매수 평균가 조회
def DIS_BUY_AVG(coin_name):
    return  upbit.get_avg_buy_price(coin_name)     

# 특정 코인의 현재 가격 조회
def DIS_CUR_PRICE(coin_name):
    return  pyupbit.get_current_price(coin_name)        

# 보유 현금 조회
def DIS_ACCOUNT_KRW():
    return upbit.get_balance("KRW")        

# return : 15분봉 최근 35개 중 처음봉이 기준봉이 된다
# 바로 전 종가와 비교했을때 -4원 이상 되는 봉을 찾고
# 해당 봉을 기준으로 연속으로 -4원 이상 2번 하락시 구매(반복)
def DIS_CHART_DATA(coin_name):
    url_1 = "https://api.upbit.com/v1/candles/" ## url
    url_time = "minutes/" ## 분봉
    url_num = "15?" ## 15분
    url_coin = "market="+coin_name+"&" ## coin 종류
    url_count = "count=35" ## 과거 차트 개수
    url = url_1+url_time+url_num+url_coin+url_count ## "https://api.upbit.com/v1/candles/minutes/15?market=KRW-XRP&count=40"

    response = requests.request("GET", url)

    json_response = json.loads(response.text)

    ttmp=1.0
    for i in json_response:
        #print(i['candle_date_time_kst']) ## str
        #print(i['trade_price'])  ## float

        if i['trade_price'] > ttmp:
            ttmp = i['trade_price']

    return ttmp


def DIS_AVG_CHART(coin_name,min,cnt):
  if type(min) is not int:
    return "Minute Type is not Integer"
  elif type(cnt) is not int:
    return "Count Type is not Integer"
  elif min not in [1,3,5,10,15,30,60,240]:
    return "Minute is not 1, 3, 5, 10, 15, 30, 60, 240"
  elif cnt > 102:
    return "Enter Count less than 100 plz"
  try:
    url_1 = "https://api.upbit.com/v1/candles/" ## url
    url_time = "minutes/" ## 분봉
    url_num = str(min)+"?" ## 15분
    url_coin = "market="+coin_name+"&" ## coin 종류
    url_count = "count="+str(cnt) ## 과거 차트 개수
    url = url_1+url_time+url_num+url_coin+url_count ## "https://api.upbit.com/v1/candles/minutes/15?market=KRW-XRP&count=40"

    response = requests.request("GET", url)

    json_response = json.loads(response.text)

    ttmp=0
    for i in json_response:
        #print(i['candle_date_time_kst']) ## str
        #print(i['trade_price'])  ## float
        ttmp += i['trade_price']
  except Exception as e:
    return e

  return f"{(ttmp/len(json_response)):.2f}"

# return "side&price&uuid"
def DIS_ORDER_STATE(coin_name):
    try:
        server_url = "https://api.upbit.com" 

        params = {
        'market' : coin_name,
        'states': 'wait'
        }
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
        #query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
        'Authorization': authorization,
        }

        res = requests.get(server_url + '/v1/orders', params=params, headers=headers)
        tjson = json.loads(res.text)
        result = ""
        idx = 0

        for i in tjson:
            print("{}".format(i['side']))
            print("{}".format(i['price']))
            print("{}".format(i['uuid']))
            result = result + str(idx) + "&" # Index 
            result = result + i['side'] + "&" # side : ask(매수) / bid(매도)
            result = result + i['price'] + "&" # 주문 가격
            result = result + i['uuid'] + "&" # 주문 고유ID
            idx+=1
    except Exception as e:
        print(e)

    return result

# 주문 UUID 조회
def DIS_ORDER_UUID(coin_name):
    try:
        ret = upbit.get_order(coin_name)
        if not ret:
            print("No order list.")
            return 0
            
        order_uuid = ret[0]['uuid']
        #print(order_uuid)
        
    except Exception as e:
        print(e)
        return 0
    
    return order_uuid
    

# 시장가 매수
def ORDER_BUY_MARKET(coin_name):
    try:
        Logger.info("[INFO] {}\t |ORDER_BUY({})".format(real_time,coin_name))
        #upbit.create_market_order(coin_name,"buy",5000,1)
        response = 1 # 매수 완료
    except Exception as e:
        Logger.info("[INFO] {}\t |Error : {}".format(real_time,e))
        response = 0 # 매수 실패
    return response

# 시장가 매도
def ORDER_SELL_MARKET(coin_name, sell_quan):
    try:
        Logger.info("[INFO] {}\t |ORDER_SELL({},{})".format(real_time,coin_name,sell_quan))
        #upbit.create_market_order(coin_name,"sell",sell_quan)
        response = 1 # 매도 완료
    except Exception as e:
        Logger.info("[INFO] {}\t |Error : {}".format(real_time,e))
        response = 0 # 매도 실패
    return response
    

#while 1:
    #now = datetime.now()
    #real_time = now.strftime('%Y-%m-%d %H:%M:%S') 
    #Logger.info("[INFO] {}\t |MAIN_FUNCTION_START".format(real_time))
ttval = DIS_ORDER_STATE(coin)
print(ttval)




# while 1:
#     now = datetime.now()
#     real_time = now.strftime('%Y-%m-%d %H:%M:%S') 
#     max_price = DIS_CHART_MAX(coin_name)
#     cur_price = DIS_CUR_PRICE(coin_name)
#     if cur_price<(max_price-25):
#         order_buy_price = ORDER_BUY(cur_price)
#         if order_buy_price!=0:
#             order_sell_price = ORDER_SELL(order_buy_price)
#         else : print("sell error")
#     else : print("buy error")
    

#     #Logger.info("[INFO] {}\t 가격 : {}".format(real_time,DIS_COIN_PRICE(coin_name)))
#     time.sleep(10)



