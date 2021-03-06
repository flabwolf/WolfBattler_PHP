from __future__ import print_function
import websocket
from threading import Thread
import time
import sys


def on_message(ws, message):
    print(time.time())
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        #for i in range():
        while(True):
            # send the message, then wait
            # so thread doesn't exit and socket
            # isn't closed
            msg = input()
            #ws.send("Hello %d" % i)
            ws.send(msg)

        time.sleep(1)
        ws.close()
        print("Thread terminating...")

    Thread(target=run).start()
    #ws.send("NAHANAHA vs. Gaccho-n battle")

if __name__ == "__main__":
    websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = "ws://localhost:3000"
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
    """
    websocket.enableTrace(True)
    ws = websocket.create_connection("ws://localhost:3000")
    print("Sending 'Hello, World'...")
    ws.send("Hello, World")
    print("Sent")
    print("Receiving...")
    result = ws.recv()
    print("Received '%s'" % result)
    ws.close()
    """