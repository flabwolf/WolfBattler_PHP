# -*- coding: utf-8 -*-

from __future__ import print_function, division 
import os,sys
import argparse
#import websocket
#from socket import error as SocketError
import errno
import json
from threading import Thread
from .gameinfoparser import GameInfoParser


def on_message(ws, message):
    # sock.recvに相当
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    parser = GameInfoParser()

    def run(*args):
        while(True):
            # sock.sendに相当
            ws.send(msg)
        ws.close()
        print("Thread terminating...")

    Thread(target=run).start()

def connect_parse(agent):
    # parse Args
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-p', type=int, action='store', dest='port')
    parser.add_argument('-h', type=str, action='store', dest='hostname')
    parser.add_argument('-r', type=str, action='store', dest='role', default='none')
    input_args = parser.parse_args()
    aiwolf_host = input_args.hostname
    aiwolf_port = input_args.port
    aiwolf_role = input_args.role

    #websocket
    websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = "ws://localhost:3000"
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_foever()

def conn_p():    
    # base_info
    line = ''
    while True:
        # l01:recieve 8KB
        line_recv = message
        if line_recv == '':
            break
        buffer_flg = 1
        while buffer_flg == 1:
            # l02:there's more json
            line += line_recv
            if '}\n{' in line:
                # 2 jsons recieved, goto l02 after l03
                (line, line_recv) = line.split("\n", 1)
                buffer_flg = 1
            else:
                # at most 1 json recieved, goto l01 after l03
                buffer_flg = 0
            # parse json
            try:
                # is this valid json?
                obj_recv = json.loads(line)
                # ok, goto l03
                line = ''
            except ValueError:
                # if not, there's more to read, goto l01 now
                break
            # l03 make game_info
            # print(obj_recv)
            game_info = obj_recv['gameInfo']
            if game_info is None:
                game_info = dict()
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
                ws.send((agent.getName() + '\n').encode('utf-8'))
            elif request == 'ROLE':
                ws.send((aiwolf_role+'\n').encode('utf-8'))
            elif request == 'INITIALIZE':
                # game_setting
                game_setting = obj_recv['gameSetting']
                # base_info
                base_info = dict()
                base_info['agentIdx'] = game_info['agent']
                base_info['myRole'] =  game_info["roleMap"][str(game_info['agent'])]
                base_info["roleMap"] = game_info["roleMap"]
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                # parser
                parser.initialize(game_info, game_setting)
                agent.initialize(base_info, parser.get_gamedf_diff(), game_setting)
            elif request == 'DAILY_INITIALIZE':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                agent.dayStart()
            elif request == 'DAILY_FINISH':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
            elif request == 'FINISH':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                agent.finish()
            elif request == 'VOTE':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                ws.send((json.dumps({'agentIdx':int(agent.vote())}, separators=(',', ':')) + '\n').encode('utf-8'))
            elif request == 'ATTACK':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                ws.send((json.dumps({'agentIdx':int(agent.attack())}, separators=(',', ':')) + '\n').encode('utf-8'))
            elif request == 'GUARD':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                ws.send((json.dumps({'agentIdx':int(agent.guard())}, separators=(',', ':')) + '\n').encode('utf-8'))
            elif request == 'DIVINE':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                ws.send((json.dumps({'agentIdx':int(agent.divine())}, separators=(',', ':')) + '\n').encode('utf-8'))
            elif request == 'TALK':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                ws.send((agent.talk() + '\n').encode('utf-8'))
            elif request == 'WHISPER':
                # update
                for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                    if k in game_info.keys():
                        base_info[k] =  game_info[k]
                parser.update(game_info, talk_history, whisper_history, request)
                agent.update(base_info, parser.get_gamedf_diff(), request)
                # call
                ws.send((agent.whisper() + '\n').encode('utf-8'))

if __name__ == '__main__':
    """
    PORT = 3000
    HOST = "localhost"
    server = WebsocketServer(PORT, host=HOST)
    server.set_fn_message_received(send_msg_allclient)
    server.run_forever()
    """