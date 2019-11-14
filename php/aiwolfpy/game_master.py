# from websocket_server import WebsocketServer
from contextlib import closing
import random
import copy
import json
import sqlite3
import time

from . import npc_parse
#from . import simple as summon #召喚するエージェント __init__.py も変更する
#from . import wasetch as summon
from . import N0930_2017_2 as summon
from . import contentbuilder as cb

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
        self.deadplayer = 0
        self.deadpc = 0
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

    def game_initialize(self, room_name):
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
                c.execute("select * from rooms where name = '%s'" % room_name))
            select_sql = "select * from players where room_id = '%d'" % room_id[0][0]
            players = list(c.execute(select_sql))
            self.playerlist = copy.deepcopy(players)
            # print(players)

            self.NpcList = []
            while(len(players)!=5):
                # PCが5人に満たないときはNPCを召喚する。
                # NPCはgame_master間でやり取りをする(ソケット通信をしない)
                print('NPC append')
                p_id = len(players)+1
                npc_name = 'NPC-'+str(p_id)
                NPC = (random.randint(0,100),npc_name,p_id,room_id[0][0])
                # c.execute("insert into players values (?,?,?,?)",NPC)
                players.append(NPC)
                # npc_agent = summon.SampleAgent(npc_name)
                npc_agent = summon.Agent(npc_name)
                parse = npc_parse.NPCParse(npc_agent)
                self.NpcList.append([npc_agent,npc_name,p_id,parse])
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
        if self.day != 0:
            self.send_contents["message"] = "DAY{}: TALKPART START".format(self.day)
            self.send_contents["mode"] = "TALK"
            self.send_msg()
    
    def daily_finish(self):
        self.request = 'DAILY_FINISH'
        print("DAILY_FINISH")
        if self.day != 0:
            self.send_contents["message"] = "DAY{}:TALKPART FINISHED.".format(self.day)
            self.send_msg()
        for npc in self.NpcList:
            self.create_msg(npc)

    def game_finish(self):
        self.request = 'FINISH'
        print("FINISH")
        for npc in self.NpcList:
            self.create_msg(npc)
        self.send_contents['mode'] = self.request
        self.send_contents['message'] = "役職リスト <br /> {}:{} <br /> {}:{} <br /> {}:{} <br /> {}:{} <br /> {}:{} <br />".format(
            self.namemap['1'],self.role_translate(self.RoleMap['1']),
            self.namemap['2'],self.role_translate(self.RoleMap['2']),
            self.namemap['3'],self.role_translate(self.RoleMap['3']),
            self.namemap['4'],self.role_translate(self.RoleMap['4']),
            self.namemap['5'],self.role_translate(self.RoleMap['5']),
        )
        for k, c in self.clientlist[self.room_name].items():
            self.server.send_message(c, json.dumps(self.send_contents))

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
                    self.status[str(self.infomap_all[message]['agent'])] = 'DEAD'
                    self.send_contents["message"] = "{}が襲撃されました。".format(message)
                    self.send_msg()
            else:
                pass

        # NPC が人狼
        for npc in self.NpcList:
            if self.wolf in npc:
                recv = self.create_msg(npc)
                idx = str(recv['agentIdx'])
                self.status[idx] = 'DEAD'
                # print(self.status)
                # print(self.namemap)
                self.send_contents["message"] = "{}が襲撃されました。".format(self.namemap[idx])
                self.send_msg()

    def attack_request(self):
        self.request = "ATTACK"
        for row in self.playerlist:
            if self.status[str(row[2])] == 'ALIVE':
                self.send_contents["message"] = "襲撃先を決定してください"
                self.send_contents["mode"] = self.request
                self.server.send_message(self.clientlist[self.room_name][row[1]],json.dumps(self.send_contents))

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
                if self.seer == row[2] and self.status[str(row[2])] == 'ALIVE':
                    role = self.infomap_all[message]['myRole']
                    role = role if role == 'WEREWOLF' else 'HUMAN'
                    self.send_contents["message"] = "{}は{}です。".format(message,role)
                    self.server.send_message(self.clientlist[self.room_name][row[1]],json.dumps(self.send_contents))
                    #return role if role == 'WEREWOLF' else 'HUMAN'

        # NPCが占い師
        for npc in self.NpcList:
            if self.seer in npc:
                if self.status[str(npc[2])] == 'ALIVE':
                    recv = self.create_msg(npc)
                    role = self.RoleMap[str(recv['agentIdx'])]
                    self.infomap_all[npc[1]]['divineResult'] = {
                        'agent': npc[2],
                        'day': self.day,
                        'result': role if role == 'WEREWOLF' else 'HUMAN',
                        'target': recv['agentIdx'],
                    }
                break
            # print(self.infomap_all[npc[1]]['divineResult'])
    
    def divine_request(self):
        self.request = "DIVINE"
        for row in self.playerlist:
            if self.status[str(row[2])] == 'ALIVE':
                self.send_contents["message"] = "占い先を決定してください"
                self.send_contents["mode"] = self.request
                self.server.send_message(self.clientlist[self.room_name][row[1]],json.dumps(self.send_contents))

    def action(self,player,message):
        try:
            idx = [k for k, v in self.namemap.items() if v == player][0]
            self.actionlist.append(player)

            if self.RoleMap[idx] == 'SEER' and self.request == "DIVINE":
                self.act_target = message
                #self.gm_divine(message)
            elif self.RoleMap[idx] == 'WEREWOLF' and self.request == "ATTACK":
                self.act_target = message
                #self.gm_attack(message)
            elif self.request == "VOTE":
                self.vote_request(message)
            else :
                pass
        except IndexError:
            pass

        if len(self.actionlist) == len(self.playerlist) - self.deadpc :
            self.actionflag = False
            if self.request == "DIVINE":
                self.gm_divine(self.act_target)
            elif self.request == "ATTACK":
                self.gm_attack(self.act_target)
            else:
                pass

    def gm_vote(self):
        self.request = 'VOTE'
        print("VOTE")
        self.votelist = {'1':0,'2':0,'3':0,'4':0,'5':0}
        self.votecount = 0
        for npc in self.NpcList:
            if self.status[str(npc[2])] == 'ALIVE':
                recv = self.create_msg(npc)
                self.votelist[str(recv['agentIdx'])] += 1
                self.votecount += 1

        if len(self.playerlist)-self.deadpc == 0:           
            idx = max(self.votelist, key=self.votelist.get)
            self.status[idx] = 'DEAD'
            self.send_contents["message"] = "投票の結果、{}が追放されます".format(self.namemap[str(idx)])
            self.send_msg()
            self.actionflag = False
        
        #if self.votecount != 5 -self.deadplayer:
        else:
            for row in self.playerlist:
                if self.status[str(row[2])] == 'ALIVE':
                    self.send_contents["player_name"] = "GAME_MASTER"
                    self.send_contents["message"] = "投票先を決定してください"
                    self.send_contents["mode"] = self.request
                    self.server.send_message(self.clientlist[self.room_name][row[1]],json.dumps(self.send_contents))
    
    def vote_request(self,message):
        if self.votecount == 4 - self.deadplayer:
            self.actionflag = False
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
            if self.status[str(npc[2])] == 'ALIVE':
                # print(self.talkHistory)
                recv = self.create_msg(npc)
                # print(npc)
                # print(recv)
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

                #ここからプレーヤーに渡す処理
                recv_s = recv.split()

                # print(recv_s)
                try:
                    for i in range(1,6):
                        if str(i) in recv_s[1]:
                            idx = i
                            break
                except IndexError:
                    pass

                try:
                    role = self.role_translate(recv_s[2])
                except IndexError:
                    pass
        
                target = self.namemap[str(i)]
                player = self.namemap[str(npc[2])]

                self.send_contents["mode"] = self.request
                if recv_s[0] == 'COMINGOUT':
                    self.send_contents["message"] = "{}: 私は {} です。".format(player,role)
                elif recv_s[0] == 'ESTIMATE':
                    self.send_contents["message"] = "{}: 私は{}が{}だとおもいます。".format(player,target,role)
                elif recv_s[0] == 'VOTE':
                    self.send_contents["message"] = "{}:私は{}に投票します。".format(player,target)
                elif recv_s[0] == 'DIVINED':
                    self.send_contents["message"] = "{}:{}を占った結果、{}でした。".format(player,target,role)
                else:
                    self.send_contents["message"] = "{}:SKIP".format(player)            
                self.send_msg()
                
        self.talkHistory = copy.deepcopy(self.talk_this_turn)
        
        # self.turn += 1

    def player_talk(self,player,talktype,target,role):
        # self.talk_this_turn = []
        idx = self.infomap_all[player]['agent']
        if talktype == "COMINGOUT":
            recv = cb.comingout(idx,role)
        elif talktype == "ESTIMATE":
            target_idx = self.infomap_all[target]['agent']
            recv = cb.estimate(target_idx,role)
        elif talktype == "VOTE":
            target_idx = self.infomap_all[target]['agent']
            recv = cb.vote(target_idx)
        elif talktype == "DIVINED":
            target_idx = self.infomap_all[target]['agent']
            recv = cb.divined(target_idx,role)
        talk = {
            'agent': idx,
            'day' : self.day,
            'idx': self.talknum,
            'text': recv,
            'turn': self.turn,
        }
        self.talknum += 1
        self.talk_this_turn.append(talk)
        self.infomap['talkList'].append(talk)
        self.player_talked += 1
        #print(talk)


    def role_translate(self,role):
        if role == 'VILLAGER':
            return '村人'
        elif role == 'SEER':
            return  '占い師'
        elif role == 'POSSESSED':
            return  '狂人'
        elif role == 'WEREWOLF':
            return '人狼'

    def judge(self):
        print(self.status)
        print(self.RoleMap)
        print(self.namemap)
        dead_agent = [k for k, v in self.status.items() if v == 'DEAD']
        alive_human = 4
        # 勝敗判定
        for idx in dead_agent:
            if self.RoleMap[idx] == 'WEREWOLF':
                self.game_run = False
                self.request = "FINISH"
                self.send_contents["message"] = "人狼が死んだので、村人陣営の勝利です。"
                self.send_contents["mode"] = self.request
                self.send_msg()
                for npc in self.NpcList:
                    self.create_msg(npc)
                return False
            else:
                alive_human -=1
        if alive_human <= 1:
            self.game_run = False
            self.request = "FINISH"
            self.send_contents["message"] = "生存者の半数が人狼になったので、人狼陣営の勝利です。"
            self.send_contents["mode"] = self.request
            self.send_msg()
            for npc in self.NpcList:
                self.create_msg(npc)
            return False
        
        # 死んだプレーヤーに"死にました"をわたす。
        self.deadplayer = 0
        self.deadpc = 0
        for idx in dead_agent:
            self.deadplayer += 1
            self.send_contents["message"] = "あなたは死にました。ゲームが終わるまで発言できません。"
            self.send_contents["mode"] = "DEAD"
            # print(self.namemap[idx])
            try:
                self.server.send_message(self.clientlist[self.room_name][self.namemap[idx]], json.dumps(self.send_contents))
                self.deadpc += 1
                if self.deadpc == len(self.playerlist):
                    self.actionflag == False
            except KeyError:
                pass
        # print(self.deadpc)
        return True   

    def create_msg(self,npc):
        #print(player_name)
        # PCには 'request' 'gameInfo' さえ渡せていればよさそう
        # NPCには以下のデータを渡す。whisperHistoryはNoneのまま
        if self.request == 'INITIALIZE' :
            game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': self.game_setting,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'DAILY_INITIALIZE':
            game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'FINISH':
            game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'DAILY_FINISH':
            game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': self.talkHistory,
                'whisperHistory': [],
            }
        elif self.request == 'TALK':
            game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': self.talkHistory,
                'whisperHistory': [],
            }
        elif self.request == 'ATTACK':
            game_data = {
                'gameInfo': self.infomap_all[npc[1]],
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        elif self.request == 'VOTE':
            game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        else :
            game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        #return self.NpcParse.connect_parse(npc[0],game_data)
        return npc[3].connect_parse(game_data)

    def send_msg(self):
        for k, c in self.clientlist[self.room_name].items():
            if self.status[str(c['id'])] == 'DEAD':
                self.send_contents['mode'] = 'DEAD'
            else:
                self.send_contents['mode'] = self.request
            self.server.send_message(c, json.dumps(self.send_contents))

    def send_info(self):
        for k, c in self.infomap_all.items():
            try:
                c['mode'] = 'INITIALIZE'
                self.server.send_message(self.clientlist[self.room_name][k], json.dumps(c))
                role = self.role_translate(c['myRole'])
                self.send_contents["message"] = "あなたは {} です".format(role)
                self.server.send_message(self.clientlist[self.room_name][k], json.dumps(self.send_contents))
            except KeyError:
                # NPCはKeyErrorを吐く
                pass


    def GameMain(self, room_name, server, clientlist, send_contents):
        # self.NpcPerse = npc_parse.NPCPerse()
        
        game_run = True
        self.day = 0
        self.room_name = room_name
        self.server = server
        self.clientlist = clientlist
        self.send_contents = copy.deepcopy(send_contents)

        while(game_run):
            if self.day == 0:
                # DAY 0 
                print("GAMESTART")
                self.game_initialize(room_name)
                # print(self.infomap_all)
                print(self.RoleMap)

                # 占い師、人狼をピックアップしとく
                self.seer = int([k for k, v in self.RoleMap.items() if v == 'SEER'][0])
                self.wolf = int([k for k, v in self.RoleMap.items() if v == 'WEREWOLF'][0])

                self.send_info()

                self.daily_initialize()
                self.daily_finish()
                
                time.sleep(0.3)
                self.actionflag = True
                self.actionlist = []
                self.act_target = None
                self.divine_request()
                while(self.actionflag):
                    pass
                self.day += 1

            else:
                # DAY 1 ~
                time.sleep(0.3)
                talkstart = time.time()
                self.daily_initialize()
                self.turn = 0
                self.player_talked = 0
                self.talk_this_turn = []
                while(self.turn != 10):
                    if self.player_talked == len(self.playerlist)-self.deadpc:
                        self.gm_talk()
                        self.turn += 1
                        self.player_talked = 0
                        self.talk_this_turn = []
                self.daily_finish()
                
                time.sleep(0.3)
                self.actionflag = True
                self.actionlist = []
                self.act_target = None
                self.gm_vote()
                while(self.actionflag):
                    pass
                
                time.sleep(0.3)
                game_run = self.judge()
                if game_run == False:
                    break

                time.sleep(0.3)
                if len(self.playerlist)-self.deadpc == 0:
                    self.action(None,None)
                else:        
                    self.actionflag = True
                    self.actionlist = []
                    self.act_target = None
                    self.attack_request()
                    while(self.actionflag):
                        pass
                
                time.sleep(0.3)
                game_run = self.judge()
                if game_run == False:
                    break

                time.sleep(0.3)
                if len(self.playerlist)-self.deadpc == 0:
                    self.action(None,None)
                else:
                    self.actionflag = True
                    self.actionlist = []
                    self.act_target = None
                    self.divine_request()
                    while(self.actionflag):
                        pass
                
                self.day += 1
        
        self.game_finish()
        
if __name__ == '__main__':
    gm = GameMaster()