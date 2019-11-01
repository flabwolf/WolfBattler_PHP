import argparse
from websocket_server import WebsocketServer
import types
import time
import servertest

parser = argparse.ArgumentParser()
parser.add_argument("-p", type=int)
args = parser.parse_args()

# PORT = args.p
PORT = 3000
HOST = "localhost"
client_list = []
# HOST = "http://f-server.ibe.kagoshima-u.ac.jp"

def new_client(client, server):
    global client_list
    client_list.append(client)
    server.send_message_to_all("Hey all, a new client has joined us")

def send_msg_allclient(client, server, message):
    server.send_message_to_all("{}".format(
        message).encode('iso-8859-1').decode("utf-8"))
    print(message.encode('iso-8859-1').decode("utf-8"))
    print(client)

def send_msg(client,server,message):
    global client_list
    print(client_list)
    for c in client_list:
        server.send_message(c,"{}".format(
            message).encode('iso-8859-1').decode("utf-8"))
        print(message.encode('iso-8859-1').decode("utf-8"))
        print(client)

server = WebsocketServer(PORT, host=HOST)
server.set_fn_new_client(new_client)
#server.set_fn_message_received(send_msg_allclient)
#server.set_fn_message_received(send_msg)
ts = servertest.testserv()
server.set_fn_message_received(ts.send_msg_2)
server.run_forever()