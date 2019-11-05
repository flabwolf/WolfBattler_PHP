from websocket_server import WebsocketServer
import types
import json
import aiwolfpy

# PORT = 3001
PORT = 3000
HOST = "localhost"
clientlist = {}
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
        if room_name in list(clientlist):
            # clientlist[room_name]["clients"].append(client)
            clientlist[room_name][player_name] = client
        else:
            clientlist[room_name] = {}
            #clientlist[room_name]["clients"] = []
            # clientlist[room_name]["clients"].append(client)
            clientlist[room_name][player_name] = client
    elif mode == "exit":
        send_contents["message"] = player_name + "が退室しました。"
    elif mode == "normal":
        send_contents["message"] = player_name + " ： " + message
    elif mode == "start":
        send_contents["message"] = "ゲームを開始します。"
        send_contents["mode"] = "start"
        infomap_all,request = gm.game_initialize(room_name)
        for k, c in infomap_all.items():
            try:
                server.send_message(clientlist[room_name][k], json.dumps(c))
            except KeyError:
                # NPCはKeyErrorを吐く
                pass
    elif mode == "talk":
        if message[0] == "カミングアウト":
            send_contents["message"] = "{} ： 私は【{}】です。".format(
                player_name, message[1])
        elif message[0] == "推定発言":
            send_contents["message"] = "{} ： 私は【{}】が【{}】だと思います。".format(
                player_name, message[1], message[2])
        elif message[0] == "投票発言":
            send_contents["message"] = "{} ： 私は【{}】に投票します。".format(
                player_name, message[1])
    elif mode == "vote":
        send_contents["message"] = "{} ： 【{}】に投票".format(
            player_name, message)
    elif mode == "divine":
        result = "人間"  # 人狼か人間
        send_contents["message"] = "{} ： 【{}】は【{}】です".format(
            player_name, message, result)
    elif mode == "attack":
        send_contents["message"] = "{} ： 【{}】を襲撃します。".format(
            player_name, message)

    #send_contents["game_setting"] = gamesetting

    # server.send_message_to_all(json.dumps(send_contents))
    for k, c in clientlist[room_name].items():
        server.send_message(c, json.dumps(send_contents))


gm = aiwolfpy.game_master.GameMaster()
gamesetting = gm.game_setting

server = WebsocketServer(PORT, host=HOST)
# server.set_fn_new_client(new_client)
server.set_fn_message_received(send_msg_allclient)
server.run_forever()
