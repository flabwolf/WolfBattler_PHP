from websocket_server import WebsocketServer
import types

# PORT = 3001
PORT = 3000
HOST = "localhost"
game = False
# HOST = "http://f-server.ibe.kagoshima-u.ac.jp"

# def new_client(client, server):
#     server.send_message_to_all("Hey all, a new client has joined us")


def send_msg_allclient(client, server, message):
    global game
    msg = message.encode('iso-8859-1').decode("utf-8")
    message_list = []
    if game:
        if msg == "ゲームが終了しました。":
            game = False
        message_list = msg.split()
        print(message_list)
        if message_list[0] == "カミングアウト":
            server.send_message_to_all("{}：私は【{}】です。".format(message_list[1],
                                                             message_list[2]))
        elif message_list[0] == "推定発言":
            server.send_message_to_all("{}：【{}】は【{}】だと思います。".format(message_list[1], message_list[2],
                                                                    message_list[3]))
        elif message_list[0] == "投票発言":
            server.send_message_to_all("{}：私は【{}】に投票します。".format(message_list[1],
                                                                 message_list[2]))
    else:
        if msg == "ゲームを開始しました。":
            game = True
        server.send_message_to_all("{}".format(
            msg))
    print(msg)
# print(client)


server = WebsocketServer(PORT, host=HOST)
# server.set_fn_new_client(new_client)
server.set_fn_message_received(send_msg_allclient)
server.run_forever()
