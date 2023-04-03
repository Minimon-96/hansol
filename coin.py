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

coin = "KRW-XRP"       # Coin Symbol

f=open("Key.txt")               # Upbit Accoung Key Open
lines = f.readlines()
access_key = lines[0].strip()          # access key
secret_key = lines[1].strip()          # secret key
f.close()

upbit =  pyupbit.Upbit(access_key, secret_key)  # Key Reference


now = datetime.now()
real_time = now.strftime('%Y-%m-%d %H:%M:%S') 

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


# 주문 정보 조회
def DIS_ORDER_INFO(coin_name):
    ret = upbit.get_order(coin_name)
    print(len(ret))
    if len(ret) in 0:
        return 0
    else:    
        for i in range(0,len(ret)):
            print("\nUUID : {}\n TYPE : {}\n PRICE : {}\n VOLUME : {}\n".format(ret[i]['uuid'], ret[i]['side'], ret[i]['price'], ret[i]['volume']))
            #if ret[i]['side'] in ask:
            #    res = ret[i]['uuid'] +"&"+ ret[i]['side'] +"&"+ ret[i]['price'] +"&"+ ret[i]['volume']
            #    return res


# 주문 UUID 조회
def DIS_ORDER_UUID(coin_name):
    try :
        ret = upbit.get_order(coin_name)
        if not ret:
            print("No order list.")
        else :
            order_uuid = ret[0]['uuid']
            print(order_uuid)
    except Exception as e:
        print(e)
        #Logger.info("[INFO] {}\t |ORDER_CANCLE({})".format(real_time,coin_name))


# 주문 취소
def ORDER_CANCLE(coin_name):
    try:
        ret = upbit.get_order(coin_name)
        order_uuid = ret[0]['uuid']
        print(order_uuid)
        e = upbit.cancel_order(order_uuid)
        if "None" in e:
            print(e)
            response = 0
            return response
        print(e)
        #Logger.info("[INFO] {}\t |ORDER_CANCLE({})".format(real_time,coin_name))
        response = 1 # 취소 완료
    except Exception as e:
        #Logger.info("[INFO] {}\t |Error : {}".format(real_time,e))
        print(e)
        response = 0 # 취소 실패
    return response


# 시장가 매수
def ORDER_BUY_MARKET(coin_name, buy_price):
    try:
        # symbol, price
        upbit.buy_market_order(coin_name, buy_price)
        #Logger.info("[TR] {}\t |ORDER_BUY_MARKET({},{})".format(real_time,coin_name,buy_price))
        response = 1 # 매수 완료
    except Exception as e:
        #print(e)
        #Logger.info("[ER] {}\t |ORDER_BUY_MARKET({},{})|Error : {}".format(real_time,coin_name,buy_price,e))
        response = 0 # 매수 실패
    return response



# print("Please enter your Coin")
# print("Ex) >> KRW-XRP")
# coin_name = input("Please enter your Coin >> ") 



