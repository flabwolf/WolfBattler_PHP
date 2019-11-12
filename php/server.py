from websocket_server import WebsocketServer
import types
import json
import aiwolfpy
from threading import Thread

#PORT = 3000
#HOST = "localhost"
# HOST はサーバー側にするPCのipアドレスを入力する
HOST = "10.200.11.23"
PORT = 443

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
            gm[room_name] = aiwolfpy.game_master.GameMaster()
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
        for k, c in clientlist[room_name].items():
            server.send_message(c, json.dumps(send_contents))
        # gm[room_name].GameMain(room_name,server,clientlist,send_contents)
        thread = Thread(target=gm[room_name].GameMain, args = (room_name,server,clientlist,send_contents), daemon=True)
        thread.start()
        infomap_all = gm[room_name].infomap_all
        return 0
        """
        for k, c in infomap_all.items():
            try:
                server.send_message(clientlist[room_name][k], json.dumps(c))
            except KeyError:
                # NPCはKeyErrorを吐く
                pass
        """
    
    elif mode == "talk":
        if message[0] == "カミングアウト":
            send_contents["message"] = "{} ： 私は【{}】です。".format(
                player_name, message[1])
            if message[1] == "占い師":
                role = "SEER"
            elif message[1] == "狂人":
                role = "POSSESSED"
            elif message[1] == "人狼":
                role = "WEREWOLF"
            else:
                role = "VILLAGER"
            gm[room_name].player_talk(player_name,"COMINGOUT",None,role)
        elif message[0] == "推定発言":
            send_contents["message"] = "{} ： 私は【{}】が【{}】だと思います。".format(
                player_name, message[1], message[2])
            if message[2] == "占い師":
                role = "SEER"
            elif message[2] == "狂人":
                role = "POSSESSED"
            elif message[2] == "人狼":
                role = "WEREWOLF"
            else:
                role = "VILLAGER"
            gm[room_name].player_talk(player_name,"ESTIMATE",message[1],role)      
        elif message[0] == "投票発言":
            send_contents["message"] = "{} ： 私は【{}】に投票します。".format(
                player_name, message[1])
            gm[room_name].player_talk(player_name,"VOTE",message[1],None)
        elif message[0] == "占い発言":
            send_contents["message"] = "{} ： 【{}】を占った結果、【{}】でした。".format(
                player_name, message[1], message[2])
            if message[2] == "人間":
                role = "HUMAN"
            elif message[2] == "人狼":
                role = "WEREWOLF"
            gm[room_name].player_talk(player_name,"DIVINED",message[1],role)      

        """
    elif mode == "vote":
        send_contents["message"] = "{} ： 【{}】に投票".format(
            player_name, message)
        gm[room_name].vote_request(message)
        server.send_message(client,json.dumps(send_contents))
        send_contents["message"] = "{}:投票".format(player_name)

    elif mode == "divine":
        result = gm[room_name].gm_divine(message)
        send_contents["message"] = "{} ： 【{}】は【{}】です".format(
            player_name, message, result)
        server.send_message(client,json.dumps(send_contents))
        
        send_contents["message"] = "\n DAY{} : TALKPART START".format(gm.day)
        send_contents["player_name"] = "GAME_MASTER"
        send_contents["mode"] = "TALK"
    
    elif mode == "attack":
        send_contents["message"] = "{} ： 【{}】を襲撃します。".format(
            player_name, message)
        server.send_message(client,json.dumps(send_contents))

        send_contents["message"] = "【{}】が襲撃されました。".format(message)
        """
    
    elif mode == "other":
        gm[room_name].action(player_name,message)        

    #send_contents["game_setting"] = gamesetting
    # server.send_message_to_all(json.dumps(send_contents))
    #def send_msg(clientlist,room_namesend_contents):
    for k, c in clientlist[room_name].items():
        server.send_message(c, json.dumps(send_contents))
    
    # gm.GameMain(room_name,server,clientlist,send_contents,mode)
    # infomap_all = gm.infomap_all


#gm = aiwolfpy.game_master.GameMaster()
gm = dict()
server = WebsocketServer(PORT, host=HOST)
# server.set_fn_new_client(new_client)
server.set_fn_message_received(send_msg_allclient)
server.run_forever()
