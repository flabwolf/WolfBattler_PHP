# from websocket_server import WebsocketServer
from contextlib import closing
import random
import copy
import json
import sqlite3

from . import agent
from .npc_perse import connect_parse

class GameMaster(object):
    def __init__(self):
        self.game_run = True

        self.msg = dict()
        self.infomap_all = dict()
        self.RoleMap = dict()
        self.status = dict()
        self.request = "NAME"
        self.infomap = {
                'day':0,
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
                'lastDaedAgentList':[],
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
                self.NpcList.append([npc_agent,npc_name])
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
                self.infomap['agentIdx'] = row[2]
                self.infomap['myRole'] = self.RoleMap[str(row[2])]
                self.infomap['roleMap'] = {str(self.infomap['agentIdx']): self.infomap['myRole']}
                self.infomap['statusMap'] = self.status
                self.infomap['remainTalkMap'] = {
                    '1': 10, '2': 10, '3': 10, '4': 10, '5': 10}
                self.infomap['remainWhisperMap'] = {str(row[2]):10} if self.infomap['myRole'] == 'WEREWOLF' else {}

                self.infomap_all[row[1]] = copy.copy(self.infomap)
            
            for npc in self.NpcList :
                self.create_msg(npc[1])

            # print(self.infomap_all)
            # return self.infomap_all,self.request

    def daily_initialize(self):
        self.request = "DAILY_INITIALIZE"
        for npc in self.NpcList:
            self.create_msg(npc[1])
        pass
    
    def daily_finish(self):
        self.request = "DAILY_FINISH"
        pass

    def game_finish(self):
        self.request = "FINISH"
        pass

    def gm_attack(self,agent):
        self.request = "ATTACK"
        self.status[agent] = 'DEAD'
        return True

    def gm_divine(self,agent):
        self.request = "DIVINE"

        role = self.RoleMap[agent]
        if role == 'WEREWOLF':
            return role
        else:
            return "HUMAN"

    def gm_vote(self,agent):
        self.request = "VOTE"
        self.status[agent] = 'DEAD'
        return True

    def gm_talk(self):
        self.request = "TALK"
        pass

    def create_msg(self,player_name):
        # PCには 'request' 'gameInfo' さえ渡せていればよさそう
        # NPCには以下のデータを渡す。whisperHistoryはNoneのまま
        if self.request == 'INITIALIZE' :
            self.game_data = {
                'gameInfo': self.infomap_all[player_name],
                'gameSetting': self.game_setting,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }
        else :
            self.game_data = {
                'gameInfo': self.infomap_all[player_name],
                'gameSetting': None,
                'request': self.request,
                'talkHistory': None,
                'whisperHistory': None,
            }

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
        self.game_initialize(room_name)
        seer = [k for k, v in self.RoleMap.items() if v == 'SEER']
        wolf = [k for k, v in self.RoleMap.items() if v == 'WEREWOLF']
        self.daily_initialize()
        self.daily_finish()
        self.infomap['divineResult'] = self.gm_divine(seer)
        self.gm_attack(wolf)

if __name__ == '__main__':
    gm = GameMaster()
    """
    gm.game_initialize
    gm.daily_initialize
    gm.daily_finish
    gm.gm_divine
    gm.daily_initialize
    gm.gm_talk
    gm.daily_finish
    """