# from websocket_server import WebsocketServer
from contextlib import closing
import random
import copy
import json
import sqlite3

from . import agent
from . import npc_parse

class GameMaster(object):
    def __init__(self):
        self.game_run = True

        self.msg = dict()
        self.infomap_all = dict()
        self.RoleMap = dict()
        self.status = dict()
        self.request = "NAME"
        self.day = 0
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

        self.request = "INITIALIZE"
        dbname = "db/wolf_battler.db"
        with sqlite3.connect(dbname) as conn:
            c = conn.cursor()
            #select_sql = 'select * from players'
            room_id = list(
                c.execute("select * from rooms where name = '%s'" % room_name))
            select_sql = "select * from players where room_id = '%d'" % room_id[0][0]
            players = list(c.execute(select_sql))
            # print(players)

            self.NpcList = []
            while(len(players)!=5):
                # PCが5人に満たないときはNPCを召喚する。
                # print('NPC append')
                p_id = len(players)+1
                npc_name = 'NPC-'+str(p_id)
                NPC = (random.randint(0,100),npc_name,p_id,room_id[0][0])
                players.append(NPC)
                npc_agent = agent.SampleAgent(npc_name)
                self.NpcList.append([npc_agent,npc_name,p_id])
            # print(self.NpcList)

            rolelist = ['VILLAGER', 'VILLAGER',
                        'SEER', 'POSSESSED', 'WEREWOLF']
            for row in players:
                # 役職をランダムに割り当て、全員生存状態にしておく
                self.RoleMap[str(row[2])] = rolelist.pop(
                    random.randint(0, len(rolelist)-1))
                self.status[str(row[2])] = 'ALIVE'
            # print(self.RoleMap)
            # print(self.status)

            for row in players:
                self.infomap['agent'] = row[2]
                self.infomap['myRole'] = self.RoleMap[str(row[2])]
                self.infomap['roleMap'] = {str(self.infomap['agent']): self.infomap['myRole']}
                self.infomap['statusMap'] = self.status
                self.infomap['remainTalkMap'] = {
                    '1': 10, '2': 10, '3': 10, '4': 10, '5': 10}
                self.infomap['remainWhisperMap'] = {str(row[2]):10} if self.infomap['myRole'] == 'WEREWOLF' else {}

                self.infomap_all[row[1]] = copy.copy(self.infomap)
            
            for npc in self.NpcList :
                self.create_msg(npc)

            # print(self.infomap_all)
            # return self.infomap_all,self.request

    def daily_initialize(self):
        self.request = "DAILY_INITIALIZE"
        for npc in self.NpcList:
            self.create_msg(npc)
        pass
    
    def daily_finish(self):
        self.request = "DAILY_FINISH"
        self.day += 1
        pass

    def game_finish(self):
        self.request = "FINISH"
        pass

    def gm_attack(self,agent):
        self.request = "ATTACK"
        for npc in self.NpcList:
            if agent in npc:
                recv = self.create_msg(npc)
                self.status[str(recv['agentIdx'])] = 'DEAD'
        return True

    def gm_divine(self,agent):
        # 'divineResult': {'agent': seer_agent, 'day': day_integer, 'result': 'HUMAN' or 'WEREWOLF, 'target': target_agent},
        self.request = "DIVINE"
        for npc in self.NpcList:
            if agent in npc:
                recv = self.create_msg(npc)

                role = self.RoleMap[str(recv['agentIdx'])]
                self.infomap_all[npc[1]]['divineResult'] = {
                    'agent': npc[2],
                    'day': self.day,
                    'result': role if role == 'WEREWOLF' else 'HUMAN',
                    'target': recv['agentIdx'],
                }
            # print(self.infomap_all[npc[1]]['divineResult'])
        return True
            
    def gm_vote(self):
        self.request = "VOTE"
        votelist = {'1':0,'2':0,'3':0,'4':0,'5':0}
        votecount = 0
        for npc in self.NpcList:
            recv = self.create_msg(npc)
            votelist[str(recv['agentIdx'])] += 1
            votecount += 1
        while(votecount!=5):
            # PC vote 試験導入
            votelist['2'] += 1
            votecount += 1
        self.status[max(votelist, key=votelist.get)] = 'DEAD'
        return True

    def gm_talk(self):
        self.request = "TALK"
        pass

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
        else :
            self.game_data = {
                'gameInfo': None,
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        return self.NpcPerse.connect_parse(npc[0],self.game_data)

    def request_gen(self):
        """
        what requests:
        NAME ROLE INITIALIZE DAILY_INITIALIZE DAILY_FINISH
        FINISH VOTE ATTACK DIVINE GUARD TALK WHISPER
        
        # player name は既知のステータスなのでリクエストの必要はない。
        # role もランダムに割り当てるのでリクエストの必要はない
        # GUARD,WHISPER は使用しない。
        """
        if self.game_run:
            self.game_run = False
            return "INITIALIZE"

    def gm_diff(self):
        """
        以下のデータがgameinfoparserで生成される。
        その下準備としてTalkHistoryを作る。
        pandas dataflame
            day    type  idx  turn  agent                           text
        0    2  finish    1     0      1  COMINGOUT Agent[01] POSSESSED
        1    2  finish    2     0      2   COMINGOUT Agent[02] VILLAGER
        2    2  finish    3     0      3       COMINGOUT Agent[03] SEER
        3    2  finish    4     0      4   COMINGOUT Agent[04] WEREWOLF
        4    2  finish    5     0      5   COMINGOUT Agent[05] VILLAGER
        """
        return 0

    def GameStart(self, room_name):
        self.NpcPerse = npc_parse.NPCPerse()
        self.game_initialize(room_name)
        # print(self.infomap_all)

        # 占い師を人狼をピックアップしとく
        seer = [k for k, v in self.RoleMap.items() if v == 'SEER']
        wolf = [k for k, v in self.RoleMap.items() if v == 'WEREWOLF']
        seer = int(seer[0])
        wolf = int(wolf[0])

        self.daily_initialize()
        self.daily_finish()
        #self.gm_divine(seer)
        #self.gm_attack(wolf)
        #self.gm_talk()
        self.gm_vote()
        # print(self.infomap_all)

if __name__ == '__main__':
    gm = GameMaster()