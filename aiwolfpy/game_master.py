import argparse
from websocket_server import WebsocketServer
import json
import pandas as pd
import types

class GameMaster(object):
    def __init__(self):
        self.room_flag = True
        self.game_run = True

        self.game_setting = {
            'enableNoAttack': False,
            'enableNoExecution': False, 
            'enableRoleRequest': True,
            'maxAttackRevote': 1,
            'maxRevote': 1,
            'maxSkip': 2, 
            'maxTalk': 10, 
            'maxTalkTurn': 20,
            'maxWhisper': 10, 
            'maxWhisperTurn': 20, 
            'playerNum': 5, 
            'randomSeed': 409218494,
            'roleNumMap': {
                'WEREWOLF': 1, 
                'POSSESSED': 1, 
                'FREEMASON': 0, 
                'VILLAGER': 2, 
                'MEDIUM': 0, 
                'FOX': 0, 
                'BODYGUARD': 0, 
                'SEER': 1, 
                'ANY': 0
                },
            'talkOnFirstDay': False, 
            'timeLimit': 10000, 
            'validateUtterance': True, 
            'votableInFirstDay': False, 
            'voteVisible': True, 
            'whisperBeforeRevote': False
            }

    def game_server(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", type=int)
        args = parser.parse_args()

        # PORT = args.p
        PORT = 3000
        HOST = "localhost"
        # HOST = "http://f-server.ibe.kagoshima-u.ac.jp"

        # def new_client(client, server):
        #     server.send_message_to_all("Hey all, a new client has joined us")

        server = WebsocketServer(PORT, host=HOST)
        # server.set_fn_new_client(new_client)
        # server.set_fn_message_received(send_msg_allclient)
        server.set_fn_message_received(send_msg)
        server.run_forever()

    def create_msg(self):
        self.msg = {
            'gameInfo': 4,
            'talkHistory': 'test',
            'whisperHistory': 'test',
            'request': "NAME",
            'gameSetting': None,
        }

    def request_gen(self):
        """
        what requests:
        NAME ROLE INITIALIZE DAILY_INITIALIZE DAILY_FINISH
        FINISH VOTE ATTACK DIVINE GUARD TALK WHISPER
        """
        if self.room_flag:
            self.room_flag = False
            return "NAME"
        
        elif self.game_run:
            self.game_run = False
            return "INITIALIZE"
              
    def base_gen(self):
        """
        base_info = {
            'agentIdx': 5,
            'myRole': 'VILLAGER',
            'roleMap': {'5': 'VILLAGER'}, 
            'day': 2, 
            'remainTalkMap': {'1': 10, '2': 10, '3': 10, '5': 10}, 
            'remainWhisperMap': {}, 
            'statusMap': {
                '1': 'ALIVE', 
                '2': 'ALIVE', 
                '3': 'ALIVE', 
                '4': 'DEAD', 
                '5': 'ALIVE'}
            }
        """
        return 0

    def diff_gen(self):
        """
        pandas dataflame
day    type  idx  turn  agent                           text
0    2  finish    1     0      1  COMINGOUT Agent[01] POSSESSED
1    2  finish    2     0      2   COMINGOUT Agent[02] VILLAGER
2    2  finish    3     0      3       COMINGOUT Agent[03] SEER
3    2  finish    4     0      4   COMINGOUT Agent[04] WEREWOLF
4    2  finish    5     0      5   COMINGOUT Agent[05] VILLAGER
        """
        return 0

    def game_initialize(self):
        return 0

def send_msg_allclient(client, server, message):
    server.send_message_to_all("{}".format(
        message).encode('iso-8859-1').decode("utf-8"))
    print(message.encode('iso-8859-1').decode("utf-8"))
# print(client)

def send_msg(client,server):
    server.send_message(client, json.dump(self.msg))

if __name__ == '__main__':
    gamer = GameMaster()
    game_setting = gamer.game_setting
    print(game_setting)
    print(type(game_setting))