from platform import machine
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


#log settings
#LogFormatter = logging.Formatter('%(asctime)s, %(message)s')
LogFormatter = logging.Formatter('%(message)s')

#handler settings
today_ymd=datetime.today().strftime("%Y%m%d")

LOGPATH="D:\\mygit\\coin\\coin_study\\trace\\scalper_trend" # window
#LOGPATH="/D/mygit/coin/coin_study/trace/scalper_trend" # linux
LogHandler = handlers.TimedRotatingFileHandler(filename=LOGPATH, when='midnight', interval=1, encoding='utf-8')
LogHandler.setFormatter(LogFormatter)
LogHandler.suffix = "%Y%m%d"

#logger set
Logger = logging.getLogger()
Logger.setLevel(logging.INFO)
Logger.addHandler(LogHandler)

# logging (Just care about the path.)
def log(level,func1, *args):
    # log time set
    now = datetime.now()
    real_time = now.strftime('%Y-%m-%d %H:%M:%S|')

    #[LOGLEVEL]|[TIME]|[FUNC_NAME]|[Msg]|[Input]|[Output]
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

# 특정 코인의 현재 보유 수량 조회
def GET_QUAN_COIN(coin_name):
    return  upbit.get_balance(coin_name)        

# 특정 코인의 매수 평균가 조회
def GET_BUY_AVG(coin_name):
    return  upbit.get_avg_buy_price(coin_name)     

# 특정 코인의 현재 가격 조회
def GET_CUR_PRICE(coin_name):
    return  pyupbit.get_current_price(coin_name)        

# 보유 현금 조회
def GET_ACCOUNT_KRW():
    return upbit.get_balance("KRW")        


# 이동 평균 조회
def GET_MARKET_TREND(ticker, days):
    func1 = sys._getframe(0).f_code.co_name
    ticker = ticker.split('-')[1]
    try:
        df = pybithumb.get_ohlcv(ticker)
        ma5 = df['close'].rolling(window=days).mean()
        last_ma5 = round(ma5[-2] + 1,0)
        price = round(pybithumb.get_current_price(ticker),0)

        trend = None
        if price > last_ma5+1:
            trend = "up"
        else:
            trend = "down"
        log("TR",func1, "Cur Price : "+str(price), "Trend price : "+str(last_ma),"Trend : "+trend)
        return trend
    except Exception as e:
        log("TR",e)
        return 0

# return view full order list "side&price&uuid" 
def GET_ORDER_STATE(coin_name):
    func1 = sys._getframe(0).f_code.co_name
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
        for i in tjson:
            #print("{}".format(i['side']))
            #print("{}".format(i['price']))
            #print("{}".format(i['uuid']))
            result = result + i['side'] + "&" # side : ask(매수) / bid(매도)
            result = result + i['price'] + "&" # 주문 가격
            result = result + i['uuid'] # 주문 고유ID
    except Exception as e:
        print(e)

    return result

# return "uuid&side&price&volume"
def GET_ORDER_INFO(coin_name):
    func1 = sys._getframe(0).f_code.co_name
    try:    
        ret = upbit.get_order(coin_name)
        #print(len(ret))
        #print(ret[0])
        if "error" in ret[0]:
            #Logger.info("[TR]|{}|GET_ORDER_INFO({})|{}".format(real_time,coin,ret[0]))
            return 0
        else:
            for i in range(0,len(ret)):
                #print("\n[{}/{}]".format(i,len(ret)))
                #print(" UUID : {}\n TYPE : {}\n PRICE : {}\n VOLUME : {}\n".format(ret[i]['uuid'], ret[i]['side'], ret[i]['price'], ret[i]['volume']))
                if ret[i]['side'] == 'ask' or 'bid':
                    res = ret[i]['uuid'] +"&"+ ret[i]['side'] +"&"+ ret[i]['price'] +"&"+ ret[i]['volume']
                    #Logger.info("[TR]|{}|GET_ORDER_INFO({})|{}".format(real_time,coin,ret[0]))
                    return res
    except Exception as e:
            #print("error : {}",format(e))
            return e

# 시장가 매수
def ORDER_BUY_MARKET(coin_name, buy_amount):
    func1 = sys._getframe(0).f_code.co_name
    try:
        buy_result = upbit.buy_market_order(coin_name,buy_amount) # buy_result type is dict.
        response = buy_result # 매수 주문 결과
        log("TR",func1, "Succes Buy order", coin_name, buy_amount, buy_result)
    except Exception as e:
        log("TR",func1, "Fail Buy order",coin_name, buy_amount, e)
        response = 0 # 매수 주문 실패
    return response

# 지정가 매수
def ORDER_BUY_LIMIT(coin_name,coin_price):
    func1 = sys._getframe(0).f_code.co_name
    if type(coin_price) is not int:
        #print("The price of a coin is an integer.")
        return 0
    try:
        quan = math.floor(10000/coin_price)
        # symbol, price, amount
        e = upbit.buy_limit_order(coin_name,coin_price,quan)
        print(e)
        response = 1 # 매수 완료
    except Exception as e:
        print(e)
        response = 0 # 매수 실패
    return response

# 시장가 매도
def ORDER_SELL_MARKET(coin_name):
    func1 = sys._getframe(0).f_code.co_name
    try:
        sell_amount = GET_QUAN_COIN(coin_name)
        sell_result = upbit.sell_market_order(coin_name,sell_amount) # sell_result type is dict.
        sell_volume = sell_result['volume']
        response = sell_result # 매도 주문 완료
        # Logging Default : [LOGLEVEL]|[TIME]|[FUNC_NAME]
        # Logging Enter : [Msg]|[Input]|[Output]
        log("TR",func1, "Succes Sell order",coin_name,sell_result)
    except Exception as e:
        log("TR",func1, "Fail Sell order",coin_name,e)
        response = 0 # 매도 주문 실패
    return response
    
# 지정가 매도
def ORDER_SELL_LIMIT(coin_name):
    func1 = sys._getframe(0).f_code.co_name
    try:
        vol = math.floor(upbit.get_balance(coin_name))
        buy_avg_price = math.floor(1.02 * upbit.get_avg_buy_price(coin_name))
        # symbol, price, amount(Enter nothing to sell all)
        e = upbit.sell_limit_order(coin_name, buy_avg_price,vol)
        if 'error' in e:
            log("TR",func1, "Error",coin_name,buy_avg_price,e)
            response = 0
            return response
        log("TR",func1, "Sell Order Success",coin_name,buy_avg_price)
        response = 1 # 매도 완료
    except Exception as e:
        log("TR",func1, "Error",coin_name,buy_avg_price,e)
        response = 0 # 매도 실패
    return response


# Set the parameters for the Upbit Scalper
buy_price = GET_CUR_PRICE(coin) - 4
sell_price = 0.0
current_price = 0.0
rep_point_chk = 1.0


# Initialize the trading account(지속적인 매수로 계좌에 X원이 남으면 멈춤)
cur_account = round(GET_ACCOUNT_KRW(),0)
min_account = cur_account*50/100 # 50%
stop_chk = 1

# Start the trading loop 
while stop_chk == 1:
    func1 = sys._getframe(0).f_code.co_name
    if cur_account < min_account:
        stop_chk = 0
        break
    try:
        # Check the current price
        current_price = GET_CUR_PRICE(coin) #현재가격조회

        # Full Wallet Calculate
        cur_account = GET_ACCOUNT_KRW() #보유현금조회
        cur_coin = GET_QUAN_COIN(coin) #현재 코인 보유수량
        wallet = round(cur_account + (cur_coin * current_price))
        log("DG",func1,"WALLET : " + str(wallet) , "ACCOUNT : " + str(round(cur_account)),"COIN_" + str(coin) + " : " + str(cur_coin))


        # Reset the buy and sell prices according to the market moving average.
        if GET_MARKET_TREND(coin,1) == "up":
            log("DG",func1,"Moving Trend. Reset price.")
            rep_point_chk = 0

        # The first loop or Moving average trend change requires 'buy_price/sell_price' set
        if rep_point_chk == 0:
            buy_price = current_price - 3
            #sell_price = GET_BUY_AVG(coin) * 1.02
            rep_point_chk = 1


        # Buy if the current price is lower than the buy price
        log("DG",func1,"CUR_PRICE : " + str(current_price), "BUY_PRICE  : " + str(buy_price))
        if current_price < buy_price: # 현재가격이 매수가격보다 낮아지면 매수
            # Calculate the amount of coins to buy
            buy_amount = round(5000/current_price)+1

            # buy(ticker, amount) 
            res = ORDER_BUY_MARKET(coin, buy_amount)

            # Buy order Fail is exit.
            if res == 0:
                continue

            # Update the buy price
            buy_price = current_price - 3
            sell_price = GET_BUY_AVG(coin) * 1.02
            log("DG",func1, "BUY " + str(coin)+ " : " + str(buy_price), "AMOUNT : " + str(buy_amount))
        
        log("DG",func1,"CUR_PRICE : " + str(current_price), "SELL_PRICE : " + str(sell_price))
        # Sell if the current price is higher than the sell price
        if current_price >= sell_price and GET_QUAN_COIN(coin) >= 11:
            # sell(ticker)
            res = ORDER_SELL_MARKET(coin)

            # sell order Fail is exit.
            if res == 0:
                continue

            sell_amount = res['executed_volume']
            log("DG",func1, "SELL " + str(coin) + " : " + str(sell_price), "AMOUNT : " + str(sell_amount))
    
            # Update the sell price
            sell_price = 0.0
            
            
    except Exception as e:
        print(e)

    time.sleep(5)
        

if stop_chk == 0:
    func1 = sys._getframe(0).f_code.co_name
    last_order_res = 1
    while last_order_res == 1:
        time.sleep(5)
        #If the current cash holdings fall below the desired amount, stop trading and sell the limit at +2.4% of the average purchase price.
        last_order_res = ORDER_SELL_LIMIT(coin)
        if last_order_res == 1:
            order_info = GET_ORDER_INFO(coin).split('&') #주문 정보 조회 return : uuid&side&price&volume
            log("DG",func1, "Last Order Success ")
            log("DG",func1, "UUID   : "+order_info[0])
            log("DG",func1, "PRICE  : "+order_info[2])
            log("DG",func1, "VOLUME : "+order_info[3])
            break
        elif last_order_res == 0:
            time.sleep(5)
            last_order_res = ORDER_SELL_LIMIT(coin)
        else:
            log("DG",func1, "Last Order Fail ",last_order_res)

            

print("exit.")