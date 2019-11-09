from __future__ import print_function, division

from . import contentbuilder as cb

myname = 'simple'

class SampleAgent(object):
    
    def __init__(self, agent_name):
        # myname
        self.myname = agent_name
        
        
    def getName(self):
        return self.myname
    
    def initialize(self, base_info, diff_data, game_setting):
        self.base_info = base_info
        # game_setting
        self.game_setting = game_setting
        # print(game_setting)
        #print(self.base_info)
        # print(diff_data)
        
    def update(self, base_info, diff_data, request):
        self.base_info = base_info
        # print(request)
        #print(self.base_info)
        # print(diff_data)
        
    def dayStart(self):
        return None
    
    def talk(self):
        #print(self.myname)
        return cb.comingout(self.base_info['agentIdx'],"SEER")
        # return cb.skip()
        # return cb.over()
    
    def whisper(self):
        return cb.over()
        
    def vote(self):
        return self.base_info['agentIdx']
    
    def attack(self):
        return self.base_info['agentIdx']
    
    def divine(self):
        return self.base_info['agentIdx']
    
    def guard(self):
        return self.base_info['agentIdx']
    
    def finish(self):
        return None

agent = SampleAgent(myname)

# run
if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
    