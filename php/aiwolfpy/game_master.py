#from websocket_server import WebsocketServer
from contextlib import closing
import random
import copy
import json
import sqlite3


class GameMaster(object):
    def __init__(self):
        self.room_flag = True
        self.game_run = True

        self.infomap_all = dict()
        self.RoleMap = dict()
        self.status = dict()
        self.request = "NAME"
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
        dbname = "db\wolf_battler.db"
        with sqlite3.connect(dbname) as conn:
            c = conn.cursor()
            #select_sql = 'select * from players'
            room_id = list(
                c.execute("select * from rooms where name = '%s'" % room_name))
            select_sql = "select * from players where room_id = '%d'" % room_id[0][0]
            players = list(c.execute(select_sql))
            # print(players)

            while(len(players)!=5):
                # PCが5人に満たないときはNPCを追加する。
                print('NPC append')
                p_id = len(players)+1
                NPC = (random.randint(0,100),'NPC-'+str(p_id),p_id,room_id[0][0])
                players.append(NPC)
            # print(players)

            rolelist = ['VILLAGER', 'VILLAGER',
                        'SEER', 'POSSESSED', 'WEREWOLF']
            for row in players:
                # 役職をランダムに割り当て、全員生存状態にしておく
                self.RoleMap[str(row[2])] = rolelist.pop(
                    random.randint(0, len(rolelist)-1))
                self.status[str(row[2])] = 'ALIVE'
            print(self.RoleMap)
            print(self.status)

            infomap = dict()
            for row in players:
                infomap['agentIdx'] = row[2]
                infomap['myRole'] = self.RoleMap[str(row[2])]
                infomap['roleMap'] = {str(infomap['agentIdx']): infomap['myRole']}
                infomap['self.statusMap'] = self.status
                infomap['remainTalkMap'] = {
                    '1': 10, '2': 10, '3': 10, '4': 10, '5': 10}
                infomap['remainWhisperMap'] = {}
                infomap['day'] = 0

                self.infomap_all[row[1]] = copy.copy(infomap)
            # print(self.infomap_all)

            return self.infomap_all

    def daily_initialize(self):
        self.request = "DAILY_INITIALIZE"
        pass
    
    def daily_finish(self):
        self.request = "DAILY_FINISH"
        pass

    def game_finish(self):
        self.request = "FINISH"
        pass

    def gm_attack(self,agent):
        self.request = "ATTACK"
        self.status[str(agent)] = 'DEAD'
        return True

    def gm_divine(self,agent):
        self.request = "DIVINE"
        role = self.RoleMap[str(agent)]
        if role == 'WEREWOLF':
            return role
        else:
            return "HUMAN"

    def gm_vote(self,agent):
        self.request = "VOTE"
        self.status[str(agnet)] = 'DEAD'
        return True

    def gm_talk(self):
        self.request = "TALK"
        pass

    def create_msg(self):
        # PCには 'request' 'gameInfo' さえ渡せていればよさそう
        # NPCには以下のデータを渡す。whisperHistoryはNoneのまま
        self.game_data = {
            'gameInfo': None,
            'talkHistory': None,
            'whisperHistory': None,
            'request': None,
            'gameSetting': self.game_setting,
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

if __name__ == '__main__':
    gm = GameMaster()
    info = gm.game_initialize('Room3')
    div = gm.gm_divine(3)
    atk = gm.gm_attack(3)
    print(gm.status)
    print(div)
