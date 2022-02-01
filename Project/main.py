from flask import Flask
import ccxt
import requests
import pandas_ta as ta
import schedule
import pandas as pd
import json
import time
from Project.Config import *


app = Flask(__name__)
my_coin = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT', 'SOL/USDT']


@app.route('/', methods=['POST','GET'])
def strategy(df):
    df['ema_7'] = ta.ema(df['close'], length=7)
    df['ema_14'] = ta.ema(df['close'], length=14)
    df['rsi'] = ta.rsi(df['close'], length=14) 
    df['signal_ema'] = df['ema_7'] > df['ema_14']
    df['signal_rsi'] = (df['close'] > df['ema_7']) & (df['rsi'] > 50)
    

# Check EMA7 + EMA14
def check_ema(signal, pre_sig, coin):

    if (signal == True) & (pre_sig == False):
        print('buy EMA7+EMA14')              
        mes = '🎉✨ ถึงเวลา 🟢 BUY 🟢 '+coin+' แล้วครับ 😁✅\n[กลยุทธ์: EMA7+EMA14 🏹]\n'
        BroadcastMessage(mes, Channel_access_token)        
    elif (signal == False) & (pre_sig == True):
        print('sell EMA7+EMA14')    
        mes = '🎉✨ ถึงเวลา 🔴 SELL 🔴 '+coin+' แล้วครับ 😊🟥\n[กลยุทธ์: EMA7+EMA14 🏹]\n'
        BroadcastMessage(mes, Channel_access_token)
    

# Check EMA7 + RSI 
def check_momentum(signal, pre_sig, coin):

    if (signal == True) & (pre_sig == False):
        print('buy EMA Momentum')
        mes = '🎉✨ ถึงเวลา 🟢 BUY 🟢 '+coin+' แล้วครับ 😁✅\n[กลยุทธ์: EMA Momentum ⚔]\n'
        BroadcastMessage(mes, Channel_access_token)
    elif (signal == False) & (pre_sig == True):
        print('sell EMA Momentum')   
        mes = '🎉✨ ถึงเวลา 🔴 SELL 🔴 '+coin+' แล้วครับ 😊🟥\n[กลยุทธ์: EMA Momentum ⚔]\n'
        BroadcastMessage(mes, Channel_access_token)

    
# get data for create indicators
def get_realtime_data(coin_list=my_coin, tf='1m', initial_bar=43):
    global bars, df
    
    for coin in coin_list:
        bars = binance.fetch_ohlcv(coin, timeframe=tf, limit=initial_bar)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df[:42]
        strategy(df)
        
        signal = df.iloc[-1,-2]
        pre_sig = df.iloc[-2,-2]
        signal_rsi = df.iloc[-1,-1]
        pre_signal_rsi = df.iloc[-2,-1]
    
        check_ema(signal, pre_sig, coin)
        check_momentum(signal_rsi, pre_signal_rsi, coin)

        # To Monitor
        print(f'{coin}\n{df[-2:]}\n')


def BroadcastMessage(TextMessage, Line_Acees_Token):
    LINE_API = 'https://api.line.me/v2/bot/message/broadcast'

    Authorization = 'Bearer {}'.format(Line_Acees_Token) 
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization':Authorization
    }

    data = {
        "messages":[{
            "type":"text",
            "text":TextMessage
        }]
    }

    data = json.dumps(data) 
    r = requests.post(LINE_API, headers=headers, data=data) 
    return 200
    

binance = ccxt.binance({
        'apiKey': apiKey,
        'secret': secret
}) 
schedule.every(60).seconds.do(get_realtime_data)
while True:    
    schedule.run_pending()
    time.sleep(1)