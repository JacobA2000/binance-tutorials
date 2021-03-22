import websocket
import json
import pprint 
import talib
import numpy
import requests
import config
import discord
from datetime import datetime
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/dogeusdt@kline_1m"

RSI_PERIOD = 6
RSI_OVERBOUGHT = 80
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'DOGEUSDT'
TRADE_QUANTITY = 250

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='com')

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        discord.send_message(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Sending {side} order of {quantity} X {symbol}!")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
        discord.send_message(f"```json{json.dumps(order)}```")
    except Exception as e:
        print(f"an exception occured - {e}")
        discord.send_message(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Order Failed - an exception occured - {e}!")
        return False

    return True
    
def on_open(ws):
    discord.send_message(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Connection Opened!")
    print('opened connection')

def on_close(ws):
    discord.send_message(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Connection Closed!")
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print(f"candle closed at {close}")
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print(f"the current rsi is {last_rsi}")

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()