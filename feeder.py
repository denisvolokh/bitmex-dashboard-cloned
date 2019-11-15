import ssl
import websocket
import yaml
import os
import json
import requests

def on_message(ws, message):
    data = json.loads(message)

    url = "http://django:5000/bitmex/feeder"
    # url = "http://127.0.0.1:8000/bitmex/feeder"

    if "table" in data:

        if data["table"] == "trade":
            print(f"[+] Trade: {message}")
            try:
                r = requests.post(url, json=data)
            except Exception as e:
                print(f"[!!!] Destination server is not responding! {url}")
        
        elif data["table"] == "tradeBin1m" and data["action"] == "insert":
            # print(f"[+] Insert: {message}")
            try:
                r = requests.post(url, json=data)
            except Exception as e:
                print(f"[!!!] Destination server is not responding! {url}")

        elif data["table"] == "tradeBin5m" and data["action"] == "insert":
            # print(f"[+] Insert: {message}")
            try:
                r = requests.post(url, json=data)
            except Exception as e:
                print(f"[!!!] Destination server is not responding! {url}")
        
        elif data["table"] == "tradeBin1h" and data["action"] == "insert":
            # print(f"[+] Insert: {message}")
            try:
                r = requests.post(url, json=data)
            except Exception as e:
                print(f"[!!!] Destination server is not responding! {url}")
        
        elif data["table"] == "tradeBin1d" and data["action"] == "insert":
            # print(f"[+] Insert: {message}")
            try:
                r = requests.post(url, json=data)
            except Exception as e:
                print(f"[!!!] Destination server is not responding! {url}")

        elif data["table"] == "instrument":
            try:
                r = requests.post(url, json=data)
            except Exception as e:
                print(f"[!!!] Destination server is not responding! {url}")
        
        elif data["table"] == "funding":
            try:
                r = requests.post(url, json=data)
            except Exception as e:
                print(f"[!!!] Destination server is not responding! {url}")

        else:
            print(f"[!!!] Skipping data! {data['table']} Action: {data['action']} Data: {data['data']}")     

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("thread terminating...")

if __name__ == "__main__":

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('wss://www.bitmex.com/realtime?subscribe=tradeBin1m:XBTUSD,tradeBin5m:XBTUSD,instrument:XBTUSD',
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    # ws = websocket.WebSocketApp('wss://www.bitmex.com/realtime?subscribe=funding:XBTUSD',
    #                           on_message = on_message,
    #                           on_error = on_error,
    #                           on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()    

    # # turn off SSL certification check for BitMEX websocket
    # ws = websocket.WebSocket(sslopt={'cert_reqs': ssl.CERT_NONE})

    # ws.on('')

    # # connect and subscribe to websocket chanels
    # ws.connect()