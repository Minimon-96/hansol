from platform import machine
import inspect
import pybithumb
import sys
import pyupbit
import time
import requests
import math
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


coin = "KRW-XRP" 

with open("key.txt") as f:
    access_key, secret_key = [line.strip() for line in f.readlines()]

upbit = pyupbit.Upbit(access_key, secret_key) 

rep_point_chk = 0 
buy_uuid = ""
sell_uuid = ""
stop_loss = 0.0
one_tick = 1.0


LogFormatter = logging.Formatter('%(message)s')

today_ymd=datetime.today().strftime("%Y%m%d")

LOGPATH="D:\\mygit\\coin\\coin_study\\trace\\scalper" # window
#LOGPATH="/D/mygit/coin/coin_study/trace/scalper" # linux
#LOGPATH="/D/mygit/coin/coin_study/tb/trace/scalper" # linux_tb
LogHandler = handlers.TimedRotatingFileHandler(filename=LOGPATH, when='midnight', interval=1, encoding='utf-8')
LogHandler.setFormatter(LogFormatter)
LogHandler.suffix = "%Y%m%d"

Logger = logging.getLogger()
Logger.setLevel(logging.INFO)
Logger.addHandler(LogHandler)

def log(level, *args):
    now = datetime.now()
    real_time = now.strftime('%Y-%m-%d %H:%M:%S')

    if level not in ("TR", "DG"):
        logs = f"TR|{real_time}|Log Level Error|"
        Logger.info(logs)
        return 0

    logs = f"{level}|{real_time}"

    try:
        for i in args:
            i = str(i)
            logs += f"| {i}"
    except Exception as e:
        logs += f"ER({e})"

    Logger.info(logs)
    return 1
    

def log_function_call(func):
    def wrapper(*args, **kwargs):
        frame = inspect.currentframe()
        frame_info = inspect.getframeinfo(frame)
        params = ", ".join([f"{arg}" for arg in args])
        log("TR",func.__name__,params)
        return func(*args, **kwargs)
    return wrapper

@log_function_call
def GET_QUAN_COIN(ticker, *args):
    try:
        res = upbit.get_balance(ticker)
        log("TR", "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return res  

@log_function_call
def GET_BUY_AVG(ticker, *args):
    try:
        res = upbit.get_avg_buy_price(ticker)
        log("TR", "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return res 

@log_function_call
def GET_CUR_PRICE(ticker, *args):
    try:
        res = pyupbit.get_current_price(ticker)
        log("TR",  "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return res 

@log_function_call
def GET_CASH(ticker, *args):
    try:
        res = upbit.get_balance("KRW") 
        log("TR", "Success", res)
    except Exception as e:
        res = 0
        log("TR", "Fail", e)
    return round(res)

@log_function_call
def GET_MARKET_TREND(ticker, days):
    ticker = ticker.split('-')[1]
    try:
        price = round(pybithumb.get_current_price(ticker),0)
        price_gap = price * 0.01
        df = pybithumb.get_ohlcv(ticker)
        ma5 = df['close'].rolling(window=days).mean()
        last_ma5 = round(ma5[-2] + price_gap)
        
        trend = None
        if price > last_ma5:
            trend = "up"
        else:
            trend = "down"
        days_20=20
        ma20 = df['close'].rolling(window=days_20).mean()
        last_ma20 = ma20[-2] + price_gap
        last_ma20 = round(last_ma20 * 1.2)
        if price > last_ma20:
            trend="run-up"
            last_ma5 = last_ma20
        log("TR", "Cur Price:"+str(price), "Trend price:"+str(last_ma5),"Trend:"+trend)
        return trend
    except Exception as e:
        log("TR", "Fail", e)
        return 0

@log_function_call
def GET_ORDER_UUID(ticker, *args):
    try:
        ret = upbit.get_order(ticker)
        if "error" in ret[0]:
            log("TR", "Error", ret[0])
            res = 0
        else:
            for i in range(0,len(ret)):
                if ret[i]['side'] == 'ask' or 'bid':
                    res = ret[i]['uuid'] +"&"+ ret[i]['side'] +"&"+ ret[i]['price'] +"&"+ ret[i]['volume']
                    log("TR", "Success", res)
    except Exception as e:
            res = 0
            log("TR", "Fail", e)
    return res

@log_function_call
def GET_ORDER_INFO(uuid):
    try:
        res = upbit.get_order(uuid)
        if "error" in ret[0]:
            log("TR", "Error", ret[0])
            res = 0
        log("TR", "Success", res)
    except Exception as e:
            res = 0
            log("TR", "Fail", e)
    return res

@log_function_call
def ORDER_CANCLE(ticker, *args):
    ret = GET_ORDER_UUID(ticker)
    try:
        order_uuid = ret.split('&')[0]
        result = upbit.cancel_order(order_uuid)
        res = 1 
        log("TR", "Success", result)
    except Exception as e:
        res = 0 
        log("TR", "Fail", e)
    return res


@log_function_call
def ORDER_BUY_MARKET(ticker, buy_amount):
    if buy_amount < 5000:
        log("TR", "Fail",ticker, buy_amount,"amount is better than 5000")
        return 0
    try:
        res = upbit.buy_market_order(ticker,buy_amount)
        log("TR", "Success", ticker, buy_amount, res)
    except Exception as e:
        res = 0 
        log("TR", "Fail",ticker, buy_amount, e)
    return res


@log_function_call
def ORDER_BUY_LIMIT(ticker,coin_price,buy_quan):
    if type(coin_price) is not int:
        log("TR", "Fail", "The price of a coin is an integer.")
        return 0
    try:
        result = upbit.buy_limit_order(ticker,coin_price,buy_quan)
        log("TR", "Success", ticker, buy_quan, result)
        res = 1 
    except Exception as e:
        log("TR", "Fail",ticker, coin_price, buy_quan, e)
        res = 0 
    return res


@log_function_call
def ORDER_SELL_MARKET(ticker, *args):
    try:
        sell_quan = GET_QUAN_COIN(ticker)
        res = upbit.sell_market_order(ticker,sell_quan) 
        log("TR", "Success", ticker, sell_quan, sell_volume, res)
    except Exception as e:
        res = 0 
        log("TR", "Fail", ticker, sell_quan, e)
    return res
    
    
@log_function_call
def ORDER_SELL_LIMIT(ticker, *args):
    try:
        vol = math.floor(upbit.get_balance(ticker))
        buy_avg_price = math.floor(1.02 * GET_BUY_AVG(ticker))
        result = upbit.sell_limit_order(ticker, buy_avg_price, vol)
        if 'error' in res:
            log("TR","Error", ticker, buy_avg_price, result)
            res = 0
            return res
        log("TR", " Successs", ticker, buy_avg_price)
        res = 1 # 매도 완료
    except Exception as e:
        log("TR", "Fail", ticker, buy_avg_price, e)
        res = 0 # 매도 실패
    return res


cur_coin = GET_QUAN_COIN(coin) 
if cur_coin > 1:
    sell_price = round(GET_BUY_AVG(coin) * 1.02)
elif cur_coin < 1:
    sell_price = 0.0
cur_price = GET_CUR_PRICE(coin)
buy_price = cur_price - 3
rep_point_chk = 1.0
chk_sell_order = 0

"""
 chk_run value
 0 : Current Cash is $0
 1 : Trade Start
 2 : Program Exit
"""
chk_run = 1

cur_cash = GET_CASH(coin)
if cur_cash == 0:
    log("DG","The balance is confirmed as $0.")
    chk_run = 2
min_cash = round((cur_cash + (cur_coin * cur_price)) * 30/100) 


while chk_run == 1:
    
    if cur_cash < 100:
        log("DG","The balance is confirmed as $0.")
        break
    if cur_cash > min_cash:
        try:
            cur_price = GET_CUR_PRICE(coin) 
            if cur_price < 1:
                cur_price = 1
                buy_price = 0
                time.sleep(10)
                continue

            cur_cash = GET_CASH(coin)
            if cur_cash == 0:
                log("DG","The balance is confirmed as $0.")
                break
            elif cur_cash < min_cash:
                log("DG","Cash on hand is too low.")
                chk_run = 0
                break
            cur_coin = GET_QUAN_COIN(coin) 
            if cur_coin < 1:
                sell_price = 0.0
            wallet = round(cur_cash + (cur_coin * cur_price))
            log("DG","WALLET : " + str(wallet) , "ACCOUNT : " + str(round(cur_cash)),"COIN_" + str(coin) + " : " + str(cur_coin))


            trend = GET_MARKET_TREND(coin,3)
            if  trend == "up":
                log("DG","The price is high. Reset Buy price.")
                rep_point_chk = 0
            elif trend == "run-up":
                log("DG","The price is Crazy run-up. Reset Buy price.")
                rep_point_chk = 0

            if rep_point_chk == 0:
                buy_price = cur_price - 3
                rep_point_chk = 1

            log("DG","CUR_PRICE : " + str(cur_price), "BUY_PRICE  : " + str(buy_price))
            if cur_price < buy_price:
                buy_amount = 6000 

                res = ORDER_BUY_MARKET(coin, buy_amount)
                time.sleep(1)

                if res != 0:
                    buy_price = cur_price - 3
                    sell_price = round(GET_BUY_AVG(coin) * 1.02)
                    log("DG", "BUY " + str(coin)+ " : " + str(cur_price), "AMOUNT : " + str(buy_amount))
                
            
            log("DG","CUR_PRICE : " + str(cur_price), "SELL_PRICE : " + str(sell_price))
            if cur_price >= sell_price and GET_QUAN_COIN(coin) >= 11:
                res = ORDER_SELL_MARKET(coin)
                time.sleep(1)

                if res != 0:
                    sell_amount = res['executed_volume']
                    log("DG", "SELL " + str(coin) + " : " + str(sell_price), "AMOUNT : " + str(sell_amount))
                    sell_price = 0.0
                
        except Exception as e:
            log("DG", "Fail",e)
    else:
        try:
            last_order_res = ORDER_SELL_LIMIT(coin)
            if last_order_res == 1:
                order_info = GET_ORDER_UUID(coin).split('&') 
                log("DG", "Last Order Successs ")
                log("DG", "UUID   : "+order_info[0])
                log("DG", "PRICE  : "+order_info[2])
                log("DG", "VOLUME : "+order_info[3])
                chk_sell_order = 1
            else:
                log("DG", "Fail",last_order_res)
            
        except Exception as e:
            log("DG", "Fail ",e)

    while chk_sell_order == 1:
        try:
            tmp = GET_ORDER_UUID(coin)
            if tmp != 0:
                order_info = tmp.split('&')
            else:
                log("DG", "Fail","ORDER_INFO : " + str(tmp))
                time.sleep(5)
                continue
            log("DG", "Sucess",order_info)
            order_uuid = order_info[0]
            order_status = GET_ORDER_INFO(order_uuid)

            if order_status is None or order_status['state'] == 'done':
                log("DG", "Sucess",order_status)
                break
            elif order_status['state'] == 'wait':
                log("DG", "Sucess",order_status)
            else:
                log("DG", "Fail",order_status)
                break

            time.sleep(1)
        except Exception as e:
            log("DG", "Fail",e)

    chk_sell_order = 0
    
    time.sleep(5)
        


"""
test
"""
if chk_run == 2:
    log("DG","Trade Exit.")