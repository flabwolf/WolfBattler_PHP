from __future__ import print_function, division 
import json
from .gameinfoparser import GameInfoParser

class NPCParse(object):
    def __init__(self,agent):
        self.parser = GameInfoParser()
        self.agent = agent

    def connect_parse(self,obj_recv):
        #self.parser = GameInfoParser()
        # self.base_info
        #print()
        #print(obj_recv)
        self.game_info = obj_recv['gameInfo']
        if self.game_info is None:
            self.game_info = dict()
        # talk_history and whisper_history
        talk_history = obj_recv['talkHistory']
        if talk_history is None:
            talk_history = []
        whisper_history = obj_recv['whisperHistory']
        if whisper_history is None:
            whisper_history = []
        # request must exist
        # print(obj_recv['request'])
        request = obj_recv['request']
        
        # run requested
        if request == 'NAME':
            # sock.send((self.agent.getName() + '\n').encode('utf-8'))
            return self.agent.getName()
        elif request == 'ROLE':
            # sock.send((aiwolf_role+'\n').encode('utf-8'))
            pass
        elif request == 'INITIALIZE':
            # game_setting
            game_setting = obj_recv['gameSetting']
            # self.base_info
            self.base_info = dict()
            self.base_info['agentIdx'] = self.game_info['agent']
            self.base_info['myRole'] =  self.game_info['myRole']
            self.base_info["roleMap"] = self.game_info["roleMap"]
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            # self.parser
            self.parser.initialize(self.game_info, game_setting)
            self.agent.initialize(self.base_info, self.parser.get_gamedf_diff(), game_setting)
            return True
        elif request == 'DAILY_INITIALIZE':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            self.agent.dayStart()
            return True
        elif request == 'DAILY_FINISH':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            return True
        elif request == 'FINISH':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            self.agent.finish()
            return True
        elif request == 'VOTE':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            # sock.send((json.dumps({'agentIdx':int(agent.vote())}, separators=(',', ':')) + '\n').encode('utf-8'))
            return {'agentIdx':int(self.agent.vote())}
        elif request == 'ATTACK':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            # sock.send((json.dumps({'agentIdx':int(self.agent.attack())}, separators=(',', ':')) + '\n').encode('utf-8'))
            return {'agentIdx':int(self.agent.attack())}
        elif request == 'GUARD':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            # sock.send((json.dumps({'agentIdx':int(self.agent.guard())}, separators=(',', ':')) + '\n').encode('utf-8'))
            return {'agentIdx':int(self.agent.guard())}
        elif request == 'DIVINE':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            # sock.send((json.dumps({'agentIdx':int(self.agent.divine())}, separators=(',', ':')) + '\n').encode('utf-8'))
            return {'agentIdx':int(self.agent.divine())}
        elif request == 'TALK':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            # sock.send((self.agent.talk() + '\n').encode('utf-8'))
            return self.agent.talk()
        elif request == 'WHISPER':
            # update
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in self.game_info.keys():
                    self.base_info[k] =  self.game_info[k]
            self.parser.update(self.game_info, talk_history, whisper_history, request)
            self.agent.update(self.base_info, self.parser.get_gamedf_diff(), request)
            # call
            # sock.send((self.agent.whisper() + '\n').encode('utf-8'))
            return self.agent.whiaper()
