from __future__ import print_function, division 
import random
import pandas

from . import contentbuilder as cb

myname = 'wase'

class AgentW(object): 
    def __init__(self, agent_name):
        self.myname = agent_name
        self.gamecount = 0
        
    def getName(self):
        return self.myname
    
    def initialize(self, base_info, diff_data, game_setting):
        #print(base_info)
        #print(diff_data)
        #print(game_setting)
        self.base_info = base_info
        # game_setting
        self.game_setting = game_setting
        self.Players = self.game_setting['playerNum']
        self.gamecount+=1

        print("\n *** NEW GAME START *** \n")
        print("game: " , self.gamecount)
        # self_info
        self.comingout = True
        self.report = True
        self.divined = []
        self.lied = []
        self.divres = ''
        self.wolf = []
        self.colist = []
        
    def update(self, base_info, diff_data, request):
        #print(request)
        #print(base_info)
        #print(diff_data)
        self.base_info = base_info
        
        if request == 'DAILY_INITIALIZE':
            for row in diff_data.itertuples():
                if row.type == 'divine':
                    self.report = True
                    self.divres = row.text
                    if 'WEREWOLF' in self.divres:
                        self.wolf.append(row.agent)
            if self.base_info['myRole'] == 'POSSESSED':
                self.report = True
        
        if request == 'DAILY_FINISH':
            pass

        if request == 'TALK':
            for row in diff_data.itertuples():
                if 'COMINGOUT' in row.text and 'BECAUSE' not in row.text :
                    self.colist.append(row.agent)

    def dayStart(self):
        self.myturn = 0
        return None
    
    def talk(self):
        self.myturn += 1

        # comingout
        if self.base_info['myRole'] == 'SEER' and self.comingout:
            self.comingout = False
            return cb.comingout(self.base_info['agentIdx'], 'SEER')
        elif self.base_info['myRole'] == 'POSSESSED'  and self.comingout:
            self.comingout = False
            return cb.comingout(self.base_info['agentIdx'], 'SEER')

        # report
        if self.base_info['myRole'] == 'SEER' and self.report:
            self.report = False
            return self.divres
        if self.base_info['myRole'] == 'POSSESSED' and self.report:
            # FAKE divine
            lielist = []
            self.report = False
            for i in range(1,self.Players+1):
                if self.base_info['agentIdx'] == i:
                    continue
                if self.base_info['statusMap'][str(i)] == 'ALIVE' and i not in self.lied:
                    lielist.append(i)
            idx = random.choice(lielist)
            self.lied.append(idx)
            return cb.divined(idx,'HUMAN')
        
        # skip/over
        if self.myturn <= 10:
            return cb.skip()
        return cb.over()
    
    def whisper(self):
        return cb.skip()
        
    def vote(self):
        idx = 1
        if self.base_info['myRole'] == "WEREWOLF":
            for i in range(1,self.Players+1):
                if i not in self.colist and i != self.base_info['agentIdx'] and self.base_info['statusMap'][str(i)] == 'ALIVE':
                    idx = i
                    break
        elif self.base_info['myRole'] == "POSSESSED":
            for i in range(len(self.colist)):
                if self.colist[i] != self.base_info['agentIdx'] and self.base_info['statusMap'][str(i)] == 'ALIVE':
                    idx = self.colist[i]
                    break
        elif self.base_info['myRole'] == "SEER":
            for i in range(len(self.colist)):
                if self.colist[i] != self.base_info['agentIdx'] and self.base_info['statusMap'][str(i)] == 'ALIVE':
                    idx = self.colist[i]
                    break
            if self.wolf:
                idx = self.wolf[0]
        else:
            idx = 1
            pass
        return idx
        #return self.base_info['agentIdx']
    
    def attack(self):
        return self.base_info['agentIdx']
    
    def divine(self):
        divine_list = []
        for i in range(1,self.Players+1):
            if self.base_info['agentIdx'] == i:
                continue
            if self.base_info['statusMap'][str(i)] == 'ALIVE' and i not in self.divined :
                divine_list.append(i)
        idx = random.choice(divine_list)
        self.divined.append(idx)
        return idx
    
    def guard(self):
        return self.base_info['agentIdx']
    
    def finish(self):
        print("\n *** GAME OVER ***")        
        return None

agent = AgentW(myname)

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
    