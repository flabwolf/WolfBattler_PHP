import argparse
from websocket_server import WebsocketServer
import types

parser = argparse.ArgumentParser()
parser.add_argument("-p", type=int)
args = parser.parse_args()

# PORT = args.p
PORT = 3000
HOST = "localhost"
# HOST = "http://f-server.ibe.kagoshima-u.ac.jp"

# def new_client(client, server):
#     server.send_message_to_all("Hey all, a new client has joined us")


def send_msg_allclient(client, server, message):
    server.send_message_to_all("{}".format(
        message).encode('iso-8859-1').decode("utf-8"))
    print(message.encode('iso-8859-1').decode("utf-8"))
# print(client)


server = WebsocketServer(PORT, host=HOST)
# server.set_fn_new_client(new_client)
server.set_fn_message_received(send_msg_allclient)
server.run_forever()
