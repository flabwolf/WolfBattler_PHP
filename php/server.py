from websocket_server import WebsocketServer
import types
import json

# PORT = 3001
PORT = 3000
HOST = "localhost"
# HOST = "http://f-server.ibe.kagoshima-u.ac.jp"

# def new_client(client, server):
#     server.send_message_to_all("Hey all, a new client has joined us")


def send_msg_allclient(client, server, receive):
    receive = json.loads(receive.encode('iso-8859-1').decode("utf-8"))
    print(receive)
    player_name = receive["player_name"]
    room_name = receive["room_name"]
    message = receive["message"]
    mode = receive["mode"]
    send_contents = {"player_name": player_name,
                     "room_name": room_name, "message": "", "mode": ""}

    if mode == "init":
        send_contents["message"] = player_name + "が入室しました。"
    elif mode == "exit":
        send_contents["message"] = player_name + "が退室しました。"
    elif mode == "normal":
        send_contents["message"] = player_name + " ： " + message
    elif mode == "start":
        send_contents["message"] = "ゲームを開始します。"
        send_contents["mode"] = "start"
    elif mode == "play":
        if message[0] == "カミングアウト":
            send_contents["message"] = "{} ： 私は【{}】です。".format(
                player_name, message[1])
        elif message[0] == "推定発言":
            send_contents["message"] = "{} ： 私は【{}】が【{}】だと思います。".format(
                player_name, message[1], message[2])
        elif message[0] == "投票発言":
            send_contents["message"] = "{} ： 私は【{}】に投票します。".format(
                player_name, message[1])

    server.send_message_to_all(json.dumps(send_contents))


server = WebsocketServer(PORT, host=HOST)
# server.set_fn_new_client(new_client)
server.set_fn_message_received(send_msg_allclient)
server.run_forever()
