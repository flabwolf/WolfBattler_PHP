from websocket_server import WebsocketServer
from contextlib import closing
import random
import copy
import json
import sqlite3
import time

#from . import npc_parse
#from . import simple as summon #召喚するエージェント __init__.py も変更する
#from . import contentbuilder as cb
import aiwolfpy
import aiwolfpy.npc_parse as npc_parse
import aiwolfpy.simple as summon
import aiwolfpy.contentbuilder as cb

class GameMaster(object):
    def __init__(self):
        self.game_run = True

        self.msg = dict()
        self.namemap = dict()
        self.namelist = []
        self.infomap_all = dict()
        self.RoleMap = dict()
        self.status = dict()
        self.request = "NAME"
        self.day = 0
        self.talknum = 0
        self.turn = 0
        self.talkHistory = []
        self.infomap = {
                'day': self.day,
                'talkList':[],
                'voteList':[],
                'whisperList':[],
                'divineResult':None,

                'mediumResult':None,
                'attackVoteList':[],
                'attackedAgent':-1,
                'cursedFox':-1,
                'executedAgent':-1,
                'existingRoleList':['POSSESSED','SEER','VILLAGER','WEREWOLF'],
                'guardedAgent':-1,
                'lastDeadAgentList':[],
                'latestAttackVoteList':[],
                'latestExecutedAgent':-1,
                'latestVoteList':[],
        }
        # game_setting:INITIALIZE時のみ必要。それ以外はNoneでいい
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
            'randomSeed': random.randint(0, 10000),
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

    def game_initialize(self):
        # ゲーム開始に呼び出す
        # print(room_name)

        self.day = 0
        self.request = 'INITIALIZE'
        print("INITIALIZE")
        dbname = "db/wolf_battler.db"
        with sqlite3.connect(dbname) as conn:
            c = conn.cursor()
            #select_sql = 'select * from players'
            room_id = list(
                c.execute("select * from rooms where name = '%s'" % self.room_name))
            select_sql = "select * from players where room_id = '%d'" % room_id[0][0]
            players = list(c.execute(select_sql))
            self.playerlist = copy.deepcopy(players)
            # print(players)

            self.NpcList = []
            while(len(players)!=5):
                # PCが5人に満たないときはNPCを召喚する。
                # NPCはgame_master間でやり取りをする(ソケット通信をしない)
                # print('NPC append')
                p_id = len(players)+1
                npc_name = 'NPC-'+str(p_id)
                NPC = (random.randint(0,100),npc_name,p_id,room_id[0][0])
                # c.execute("insert into players values (?,?,?,?)",NPC)
                players.append(NPC)
                npc_agent = summon.SampleAgent(npc_name)
                self.NpcList.append([npc_agent,npc_name,p_id])
            # print(self.NpcList)

            rolelist = ['VILLAGER', 'VILLAGER',
                        'SEER', 'POSSESSED', 'WEREWOLF']
            for row in players:
                # 役職をランダムに割り当て、全員生存状態にしておく
                self.namemap[str(row[2])] = row[1]
                self.RoleMap[str(row[2])] = rolelist.pop(
                    random.randint(0, len(rolelist)-1))
                self.status[str(row[2])] = 'ALIVE'
            # print(self.RoleMap)
            # print(self.status)

            for row in players:
                self.namelist.append(row[1])
                self.infomap['agent'] = row[2]
                self.infomap['myRole'] = self.RoleMap[str(row[2])]
                self.infomap['roleMap'] = {str(self.infomap['agent']): self.infomap['myRole']}
                self.infomap['statusMap'] = self.status
                self.infomap['nameMap'] = self.namemap
                self.infomap['remainTalkMap'] = {
                    '1': 10, '2': 10, '3': 10, '4': 10, '5': 10}
                self.infomap['remainWhisperMap'] = {str(row[2]):10} if self.infomap['myRole'] == 'WEREWOLF' else {}

                self.infomap_all[row[1]] = copy.copy(self.infomap)
            
            for npc in self.NpcList :
                self.create_msg(npc)

            # print(self.infomap_all)
            # return self.infomap_all,self.request

    def daily_initialize(self):
        self.request = 'DAILY_INITIALIZE'
        print("DAILY_INITIALIZE")
        for npc in self.NpcList:
            self.create_msg(npc)
    
    def daily_finish(self):
        self.request = 'DAILY_FINISH'
        print("DAILY_FINISH")
        if self.day != 0:
            self.send_contents["message"] = "DAY{}:TALKPART FINISHED.".format(self.day)
            self.send_msg()
        #self.send_contents["mode"] = "VOTE"
        #self.send_contents["message"] = "アヤシイと思うヒトを選択してね"
        #self.send_msg()
        for npc in self.NpcList:
            self.create_msg(npc)

    def game_finish(self):
        self.request = 'FINISH'
        print("FINISH")
        for npc in self.NpcList:
            self.create_msg(npc)

    def gm_attack(self,message):
        self.request = 'ATTACK'
        print("ATTACK")
        # プレーヤーが人狼
        for row in self.playerlist:
            if self.wolf == row[2]:
                if message == 0:
                    self.send_contents["message"] = "襲撃先を決定してください"
                    self.send_contents["mode"] = self.request
                    self.server.send_message(self.clientlist[self.room_name][row[1]],json.dumps(self.send_contents))
                else:
                    self.status[self.infomap_all[message]['agent']] = 'DEAD'
            else:
                pass

        # NPC が人狼
        for npc in self.NpcList:
            if self.wolf in npc:
                recv = self.create_msg(npc)
                idx = str(recv['agentIdx'])
                self.status[idx] = 'DEAD'
                print(self.status)
                print(self.namemap)
                self.send_contents["message"] = "{}が襲撃されました。".format(self.namemap[idx])
                self.send_msg()

    def gm_divine(self,message):
        # 'divineResult': {'agent': seer_agent, 'day': day_integer, 'result': 'HUMAN' or 'WEREWOLF, 'target': target_agent},
        self.request = 'DIVINE'
        print("DIVINE")
        
        # プレーヤーが占い師
        for row in self.playerlist:
            if message == 0:
                if self.seer == row[2]:
                    self.send_contents["message"] = "占い先を決定してください"
                    self.send_contents["mode"] = self.request
                    self.server.send_message(self.clientlist[self.room_name][row[1]],json.dumps(self.send_contents))
                else:
                    self.send_contents["message"] = "あ？"
                    self.send_contents["mode"] = self.request
                    self.server.send_message(self.clientlist[self.room_name][row[1]],json.dumps(self.send_contents))
            else:
                if self.seer == row[2]:
                    role = self.infomap_all[message]['myRole']
                    return role if role == 'WEREWOLF' else 'HUMAN'

        # NPCが占い師
        for npc in self.NpcList:
            if self.seer in npc:
                recv = self.create_msg(npc)

                role = self.RoleMap[str(recv['agentIdx'])]
                self.infomap_all[npc[1]]['divineResult'] = {
                    'agent': npc[2],
                    'day': self.day,
                    'result': role if role == 'WEREWOLF' else 'HUMAN',
                    'target': recv['agentIdx'],
                }
                self.send_contents["message"] = "\n DAY{}: TALKPART START".format(self.day)
                self.send_contents["mode"] = "TALK"
                time.sleep(3)
                self.send_msg()
                break
            # print(self.infomap_all[npc[1]]['divineResult'])
            
    def gm_vote(self):
        self.request = 'VOTE'
        print("VOTE")
        self.votelist = {'1':0,'2':0,'3':0,'4':0,'5':0}
        self.votecount = 0
        for npc in self.NpcList:
            recv = self.create_msg(npc)
            self.votelist[str(recv['agentIdx'])] += 1
            self.votecount += 1

        if self.votecount != 5:
            self.send_contents["player_name"] = "GAME_MASTER"
            self.send_contents["message"] = "投票先を決定してください"
            self.send_contents["mode"] = self.request
            self.send_msg()
    
    def vote_request(self,message):
        if self.votecount == 4:
            self.votelist[str(self.infomap_all[message]['agent'])] += 1
            idx = max(self.votelist, key=self.votelist.get)
            self.status[idx] = 'DEAD'
            self.send_contents["message"] = "投票の結果、{}が追放されます".format(self.namemap[str(idx)])
            self.send_msg()
        else:
            self.votelist[str(self.infomap_all[message]['agent'])] += 1
            self.votecount += 1

    def gm_talk(self):
        # {'agent': 2, 'day': 1, 'idx': 30, 'text': 'Over', 'turn': 6}
        self.request = 'TALK'
        self.send_contents['mode'] = self.request
        # AIに送る用
        # self.talk_this_turn = []
        for npc in self.NpcList:
            recv = self.create_msg(npc)
            talk = {
                'agent': npc[2],
                'day': self.day,
                'idx': self.talknum,
                'text': recv,
                'turn': self.turn,
            }
            self.talknum += 1 
            self.talk_this_turn.append(talk)
            self.infomap['talkList'].append(talk)
        self.talkHistory = copy.deepcopy(self.talk_this_turn)
        
        # self.turn += 1

    def player_talk(self):
        self.talk_this_turn = []

    def create_msg(self,npc):
        #print(player_name)
        # PCには 'request' 'gameInfo' さえ渡せていればよさそう
        # NPCには以下のデータを渡す。whisperHistoryはNoneのまま
        if self.request == 'INITIALIZE' :
            self.game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': self.game_setting,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'DAILY_INITIALIZE':
            self.game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'FINISH':
            self.game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'DAILY_FINISH':
            self.game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': self.talkHistory,
                'whisperHistory': [],
            }
        elif self.request == 'TALK':
            self.game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': self.talkHistory,
                'whisperHistory': [],
            }
        elif self.request == 'ATTACK':
            self.game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'VOTE':
            self.game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        else :
            self.game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        return self.NpcPerse.connect_parse(npc[0],self.game_data)

    def send_msg(self):
        for k, c in self.clientlist[self.room_name].items():
            self.server.send_message(c, json.dumps(self.send_contents))

    def send_info(self):
        for k, c in self.infomap_all.items():
            try:
                c['mode'] = 'INITIALIZE'
                self.server.send_message(self.clientlist[self.room_name][k], json.dumps(c))
                self.send_contents["message"] = "あなたは {} です".format(c['myRole'])
                self.server.send_message(self.clientlist[self.room_name][k], json.dumps(self.send_contents))
            except KeyError:
                # NPCはKeyErrorを吐く
                pass


    def GameMain(self):
        self.NpcPerse = npc_parse.NPCPerse()
        
        self.day = 0

        if self.day == 0:
            # DAY 0 
            print("GAMESTART")
            self.game_initialize()
            # print(self.infomap_all)
            print(self.RoleMap)

            # 占い師、人狼をピックアップしとく
            self.seer = int([k for k, v in self.RoleMap.items() if v == 'SEER'][0])
            self.wolf = int([k for k, v in self.RoleMap.items() if v == 'WEREWOLF'][0])

            self.send_info()

            self.daily_initialize()
            self.daily_finish()
            
            #self.gm_attack(0)
            self.gm_divine(0)
            self.day += 1

        """
        else:
            # DAY 1 ~
            self.daily_initialize()
            self.turn = 0
            while(self.turn!=10):
                self.gm_talk()
                self.turn += 1
            self.daily_finish()
            self.gm_attack(0)
            self.gm_vote()
            self.day += 1
        """
        return True

    def send_msg_allclient(self, client, server, receive):
        receive = json.loads(receive.encode('iso-8859-1').decode("utf-8"))
        print(receive)
        self.player_name = receive["player_name"]
        self.room_name = receive["room_name"]
        self.message = receive["message"]
        self.mode = receive["mode"]
        self.send_contents = {"player_name": self.player_name,
                        "room_name": self.room_name, "message": "", "mode": ""}

        if mode == "init":
            self.send_contents["message"] = self.player_name + "が入室しました。"
            if self.room_name in list(self.clientlist):
                # self.clientlist[self.room_name]["clients"].append(client)
                self.clientlist[self.room_name][self.player_name] = client
            else:
                self.clientlist[self.room_name] = {}
                self.master[self.room_name] = GameMaster()
                #self.clientlist[self.room_name]["clients"] = []
                # self.clientlist[self.room_name]["clients"].append(client)
                self.clientlist[self.room_name][self.player_name] = client
        
        elif mode == "exit":
            self.send_contents["message"] = self.player_name + "が退室しました。"
        
        elif mode == "normal":
            self.send_contents["message"] = self.player_name + " ： " + message
        
        elif mode == "start":
            self.send_contents["message"] = "ゲームを開始します。"
            self.send_contents["mode"] = "start"
            for k, c in self.clientlist[self.room_name].items():
                server.send_message(c, json.dumps(self.send_contents))
            gm.GameMain()
            infomap_all = gm.infomap_all
            return 0
            """
            for k, c in infomap_all.items():
                try:
                    server.send_message(self.clientlist[self.room_name][k], json.dumps(c))
                except KeyError:
                    # NPCはKeyErrorを吐く
                    pass
            """
        
        elif mode == "talk":
            if message[0] == "カミングアウト":
                self.send_contents["message"] = "{} ： 私は【{}】です。".format(
                    self.self_player_name, message[1])
                gm.player_talk(self.self_player_name,message[1],None)
            elif message[0] == "推定発言":
                self.send_contents["message"] = "{} ： 私は【{}】が【{}】だと思います。".format(
                    self.self_player_name, message[1], message[2])
                gm.player_talk(self.self_player_name,message[1],message[2])      
            elif message[0] == "投票発言":
                self.send_contents["message"] = "{} ： 私は【{}】に投票します。".format(
                    self.self_player_name, message[1])
                gm.player_talk(self.self_player_name,message[1],None)

        elif mode == "vote":
            self.send_contents["message"] = "{} ： 【{}】に投票".format(
                self.self_player_name, message)
            gm.vote_request(message)
            server.send_message(client,json.dumps(self.send_contents))
            self.send_contents["message"] = "{}:投票".format(self.self_player_name)

        elif mode == "divine":
            result = gm.gm_divine(message)
            self.send_contents["message"] = "{} ： 【{}】は【{}】です".format(
                self.self_player_name, message, result)
            server.send_message(client,json.dumps(self.send_contents))
            
            self.send_contents["message"] = "\n DAY{} : TALKPART START".format(gm.day)
            self.send_contents["self.self_player_name"] = "GAME_MASTER"
            self.send_contents["mode"] = "TALK"
        
        elif mode == "attack":
            self.send_contents["message"] = "{} ： 【{}】を襲撃します。".format(
                self.self_player_name, message)
            server.send_message(client,json.dumps(self.send_contents))

            self.send_contents["message"] = "【{}】が襲撃されました。".format(message)
        
        elif mode == "other":
            pass

        #self.send_contents["game_setting"] = gamesetting
        # server.send_message_to_all(json.dumps(self.send_contents))
        #def send_msg(self.clientlist,room_namesend_contents):
        for k, c in self.clientlist[self.room_name].items():
            server.send_message(c, json.dumps(self.send_contents))
        
        # gm.GameMain(self.room_name,server,self.clientlist,self.send_contents,mode)
        # infomap_all = gm.infomap_all

if __name__ == "__main__":
    PORT = 3000
    HOST = "localhost"

    gm = GameMaster()
    gm.clientlist = {}
    gm.server = WebsocketServer(PORT, host=HOST)
    # server.set_fn_new_client(new_client)
    gm.server.set_fn_message_received(gm.send_msg_allclient)
    gm.server.run_forever()
