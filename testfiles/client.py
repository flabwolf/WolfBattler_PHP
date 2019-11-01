import websocket
import threading
ws = websocket.WebSocket()
ws = websocket.create_connection("ws://localhost:3000/")


def res_msg():
    result = ws.recv()
    print("Received '%s'" % result)


while True:
    thread = threading.Thread(target=res_msg)
    thread.start()
    msg = input()
    ws.send(msg)


ws.close()
