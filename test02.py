from platform import machine
import pybithumb
import sys
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


# print("Please enter your Coin")
# print("Ex) >> KRW-XRP")
# coin = input("Please enter your Coin >> ") 
coin = "KRW-XRP"       # Coin Symbol

f=open("key.txt")               # Upbit Accoung Key Open
lines = f.readlines()
access_key = lines[0].strip()          # access key
secret_key = lines[1].strip()          # secret key
f.close()

upbit = pyupbit.Upbit(access_key, secret_key)  # Key Reference
rep_point_chk = 0   # Buy order signal check
buy_uuid = ""
sell_uuid = ""
stop_loss = 0.0
one_tick = 1.0

# logging (Just care about the path.)
def log(level, func1, *args):
    #LogFormatter = logging.Formatter('%(asctime)s, %(message)s')
    LogFormatter = logging.Formatter('%(message)s')

    #handler settings
    today_ymd=datetime.today().strftime("%Y%m%d")
    #LOGPATH="C:\\Users\\PHM\\Desktop\\git\\hansol\\trace\\trace"+today_ymd+".log" # hansol
    LOGPATH="D:\\mygit\\coin\\coin_study\\trace\\trace"+today_ymd+".log" # home
    #LOGPATH="/D/mygit/coin/coin_study/trace/trace"+today_ymd+".log" # linux
    LogHandler = handlers.TimedRotatingFileHandler(filename=LOGPATH, when='midnight', interval=1, encoding='utf-8')
    LogHandler.setFormatter(LogFormatter)
    LogHandler.suffix = "%Y%m%d"

    #logger set
    Logger = logging.getLogger()
    Logger.setLevel(logging.INFO)
    Logger.addHandler(LogHandler)

    # log time set
    now = datetime.now()
    real_time = now.strftime('%Y-%m-%d %H:%M:%S|')

    #[LOGLEVEL]|[TIME]|[FUNC_NAME]|[Msg]|[Input]|[Output]
    #func1 = sys._getframe(0).f_code.co_name
    if level == "TR":
        logs = "TR| "+real_time+func1 +"()| "
    elif level == "DG":
        logs = "DG| "+real_time

    try:
        #print(len(args))
        for i in args:
            if type(i) != str:
                i=str(i)
            elif type(i) == str:
                pass
            else:
                logs = logs+"|Logging Type Error|"+i+type(i)
                Logger.info(logs)
                return 0
            logs += i+"| "
        Logger.info(logs)
    
    except Exception as e:
        logs += "ER("+e+")"
        Logger.info(logs)
        return 0

    return 1





def ORDER_BUY_MARKET(coin_name, buy_amount):
    try:
        buy_result = upbit.buy_market_order(coin_name,buy_amount) # buy_result type is dict.
        response = buy_result # 매수 주문 완료
        log("TR","ORDER_BUY_MARKET", "Succes Buy order", coin_name, buy_amount, buy_result)
    except Exception as e:
        log("TR","ORDER_BUY_MARKET", "Fail Buy order",coin_name, buy_amount, e)
        response = 0 # 매수 주문 실패
    return response





