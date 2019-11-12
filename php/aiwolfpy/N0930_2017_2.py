#!/usr/bin/env python
from __future__ import print_function, division

# this is main script
# simple version

#import aiwolfpy
#import aiwolfpy.contentbuilder as cb
from . import contentbuilder as cb
import random
import numpy as np
import keras
import os
from keras.models import model_from_json


myname = '0930_2017_2'


class Agent(object):

    def __init__(self, agent_name):
        # myname
        self.myname = agent_name
        PATH = os.getcwd()+"/php/aiwolfpy/0930_2017_2"
        # 人狼推定モデル
        self.wolf_model = model_from_json(open(
            "%s/WOLF_model.json" % PATH).read())
        self.wolf_model.load_weights(
            "%s/WOLF_weights.h5" % PATH)
        #self.wolf_model._make_predict_function()

        # 占い師推定モデル
        self.seer_model = model_from_json(open(
            "%s/SEER_model.json" % PATH).read())
        self.seer_model.load_weights(
            "%s/SEER_weights.h5" % PATH)
        #self.seer_model._make_predict_function()

        # 狂人推定モデル
        self.poss_model = model_from_json(open(
            "%s/POSS_model.json" % PATH).read())
        self.poss_model.load_weights(
            "%s/POSS_weights.h5" % PATH)
        #self.poss_model._make_predict_function()

        """
        推定精度計算用
        """
        # 推定数
        self.sum_wolf = 0
        self.sum_seer = 0
        self.sum_poss = 0

        # 的中数
        self.acc_wolf = 0
        self.acc_seer = 0
        self.acc_poss = 0

    def getName(self):
        return self.myname

    def initialize(self, base_info, diff_data, game_setting):
        self.base_info = base_info
        self.game_setting = game_setting

        """
        予測時に扱うデータ
        """
        self.info = {}  # プレイヤーごとの特徴量
        self.LSTM_info = {}  # ターンごとのプレイヤーごとの特徴量

        self.v = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}   # 投票先予定
        self.e = {}  # 人狼と思うプレイヤー
        self.DAY = 1
        self.SEER_COUNT = 0  # 占い師の総数
        self.TURN = 0   # 占い師COしたときのターン番号
        self.CO_TURN = 0  # 占い師COした順番
        self.NUM = 15

        for p in range(1, 6):
            self.info[str(p)] = []
            for i in range(self.NUM):
                self.info[str(p)].append(0)
            self.v[str(p)] = 0
            self.e[str(p)] = 0

        """
        基本データ
        """

        # 自分のAgentID
        self.idx = base_info["agentIdx"]
        # 自分の役職
        self.role = base_info["myRole"]
        # COMINGOUTする役職
        self.comingout = ""
        # 結果内容
        self.result = ""
        # トークのターン数
        self.talk_turn = -1
        # 乱数
        self.seed = random.random()
        # スキップターン数
        self.skip_turn = 0
        # vote
        self.vote_report = False
        # estiamte
        self.estimate_report = False

        self.pre_wolf = []
        self.pre_seer = []
        self.pre_poss = []

        # 人狼確定
        self.wolf = ""
        # 白リスト
        self.WhiteList = []
        # 生存リスト
        self.AliveList = []
        # 占い師リスト
        self.SeerList = []
        # 既に占った人リスト
        self.DivinedList = []
        # 直前の投票先
        self.voted = 0
        self.vote_target = 0

        # 狂人
        self.poss = 0

        # 結果報告
        self.report = False

    def update(self, base_info, diff_data, request):
        print("---------------------------------------")
        self.base_info = base_info
        print(request)
        print(diff_data)

        if request == "DAILY_INITIALIZE" or request == "DIVINE" or request == "ATTACK":
            # ターン初期化
            self.talk_turn = -1
            self.t_turn = 0
            # 生存者を生存リストに格納する
            self.AliveList = [
                int(id) for id, status in self.base_info['statusMap'].items() if (status == 'ALIVE') and (int(id) != self.idx)]
            # 占い師リストの更新
            if self.SeerList:
                for i in self.SeerList:
                    if base_info["statusMap"][str(i)] == "DEAD":
                        self.SeerList.remove(i)
            self.DAY = base_info["day"]
            # print(base_info)
            for idx, status in self.base_info["statusMap"].items():
                self.info[idx][13] = self.DAY
                if status == "ALIVE":
                    self.info[idx][14] = 1
                else:
                    self.info[idx][14] = 0
            # 結果保存
            for i in range(diff_data.shape[0]):
                # SEER
                if diff_data["type"][i] == "divine":
                    self.report = True
                    self.result = diff_data["text"][i]
                    # 人狼確定
                    if "WEREWOLF" in diff_data["text"][i]:
                        idx = int(diff_data["agent"][i])
                        self.wolf = idx
                        self.vote_report = True
                    else:
                        idx = int(diff_data["agent"][i])
                        self.WhiteList.append(idx)
            # 狂人
            if self.role == "POSSESSED":
                self.report = True

            # 人狼
            if self.role == "WEREWOLF":
                self.report = True

        """
        TALK
        """

        if request == "TALK":
            # print(diff_data.shape)
            # COMINGOUTの内容によってリストを分ける
            for i in range(diff_data.shape[0]):
                if "COMINGOUT" in diff_data["text"][i] and diff_data["agent"][i] != self.idx:
                    if "SEER" in diff_data["text"][i] and not diff_data["agent"][i] in self.SeerList:
                        self.SeerList.append(diff_data["agent"][i])
                        # print(self.SeerList)

        for i in diff_data.values:
            # print(i)
            self.info_update(i)

        if request == "DAILY_FINISH":

            for key, val in self.info.items():
                print("プレイヤー%s：%s" % (key, val))

        print("生存者：" + str(self.AliveList))
        print("他の占い師：" + str(self.SeerList))
        print("占い済み：" + str(self.DivinedList))
        print("黒確定："+str(self.wolf))
        print("---------------------------------------")

    def dayStart(self):
        return None

    def talk(self):
        # ターン数を経過させる

        self.talk_turn += 1
        if self.skip_turn == 2:
            self.vote_report = True
            self.estimate_report = True
            self.skip_turn = 0

        """
        村人
        """
        if self.role == "VILLAGER":
            if self.DAY >= 1:
                if self.estimate_report:
                    self.estimate_report = False
                    self.vote_report = True
                    idx = self.wolfPredict()
                    self.vote_target = idx
                    estimate = cb.estimate(idx, "WEREWOLF")
                    return estimate
                elif self.vote_report:
                    self.estimate_report = True
                    self.vote_report = False
                    vote = cb.vote(self.vote_target)
                    return vote

        """
        占い師
        """
        if self.role == "SEER":
            # CO
            if self.comingout == "":
                self.comingout = "SEER"
                return cb.comingout(self.idx, self.comingout)
            # 占い結果報告
            if self.report:
                self.report = False
                self.vote_report = True
                self.estimate_report = True
                return self.result
            if self.vote_report and self.wolf != "":
                vote = cb.vote(self.wolf)
                return vote
            # 白以外の人狼らしい人に対してestimateとvote
            if self.estimate_report and self.wolf == "":
                self.estimate_report = False
                self.vote_report = True
                if self.WhiteList:
                    for i in self.WhiteList:
                        if i in self.AliveList:
                            self.AliveList.remove(i)
                idx = self.wolfPredict()
                self.vote_target = idx
                estimate = cb.estimate(idx, "WEREWOLF")
                return estimate
            if self.vote_report and self.wolf == "":
                self.vote_report = False
                self.estimate_report = True
                # print(self.vote_target)
                vote = cb.vote(self.vote_target)
                return vote

        """
        狂人
        """
        if self.role == "POSSESSED":
            # CO
            if self.comingout == "":
                self.comingout = "SEER"
                return cb.comingout(self.idx, self.comingout)
            # 占い結果報告

            if self.report:
                self.report = False
                if self.DivinedList:
                    for i in self.DivinedList:
                        if i in self.AliveList:
                            self.AliveList.remove(i)
                idx = self.seerPredict()
                self.estimate_report = True
                self.vote_report = True
                print("候補：" + str(self.AliveList))
                print("占い師："+str(idx))
                print("占い先：" + str(idx))
                self.vote_target = idx
                divined = cb.divined(idx, "WEREWOLF")
                self.DivinedList.append(idx)
                return divined
            # vote発言
            if self.estimate_report and self.DAY == 1:
                self.estimate_report = False
                self.vote_report = True
                if self.vote_target in self.AliveList:
                    self.AliveList.remove(self.vote_target)
                idx = self.wolfPredict()
                estimate = cb.estimate(idx, "VILLAGER")
                return estimate
            if self.vote_report:
                self.estimate_report = True
                self.vote_report = False
                if self.DAY == 1:
                    idx = self.vote_target
                    vote = cb.vote(idx)
                    return vote
                else:
                    idx = self.wolfPredict()
                    if len(self.AliveList) >= 3:
                        for i in self.AliveList:
                            if i != idx and i != self.idx:
                                vote = cb.vote(i)
                                return vote
                    else:
                        for i in self.AliveList:
                            if i != self.idx:
                                vote = cb.vote(i)
                                return vote

        """
        人狼
        """
        if self.role == "WEREWOLF":
            if self.estimate_report:
                self.vote_report = True
                self.estimate_report = False
                idy = self.possPredict()
                self.poss = idy
                idx = self.seerPredict()

                if not idx in self.AliveList:
                    if idy in self.AliveList and len(self.AliveList) >= 2:
                        self.AliveList.remove(idy)
                        idx = self.AliveList[0]
                    else:
                        idx = random.choice(self.AliveList)
                estimate = cb.estimate(idx, "WEREWOLF")
                self.vote_target = idx
                return estimate

            if self.vote_report:
                self.vote_report = False
                self.estimate_report = True
                vote = cb.vote(self.vote_target)
                return vote

        if self.talk_turn <= 10:
            self.skip_turn += 1
            return cb.skip()
        return cb.over()

    def whisper(self):
        return cb.over()

    def vote(self):
        print("投票予定：" + str(self.v))

        if self.role != "WEREWOLF" and self.role != "POSSESSED":
            # 占い師
            if self.wolf != "" and self.wolf in self.AliveList:
                return self.wolf
            # 白確定が人狼候補にならないようにする
            if self.role == "SEER":
                if self.DivinedList:
                    for i in self.DivinedList:
                        if i in self.AliveList:
                            self.AliveList.remove(i)
                idx = self.wolfPredict()
                idy = self.possPredict()
                self.sum_wolf += 1
                self.pre_wolf.append(idx)
                self.sum_poss += 1
                self.pre_poss.append(idy)
                print("候補：" + str(self.AliveList))
                print("人狼：" + str(idx))
                print("狂人："+str(idy))
                print("投票先：" + str(idx))
                return idx
            # 村人
            if self.role == "VILLAGER":
                idx = self.wolfPredict()
                idy = self.seerPredict()
                idz = self.possPredict()
                print("候補：" + str(self.AliveList))
                print("人狼：" + str(idx))
                print("占い師：" + str(idy))
                print("狂人："+str(idz))
                print("投票先：" + str(idx))
                self.sum_wolf += 1
                self.pre_wolf.append(idx)
                self.sum_seer += 1
                self.pre_seer.append(idy)
                self.sum_poss += 1
                self.pre_poss.append(idz)
                return idx
        # 人狼
        if self.role == "WEREWOLF":
            print("候補：" + str(self.AliveList))
            idx = self.possPredict()
            self.poss = idx
            print("狂人：" + str(idx))
            self.sum_poss += 1
            self.pre_poss.append(idx)
            idy = self.seerPredict()
            print("占い師：" + str(idy))
            self.sum_seer += 1
            self.pre_seer.append(idy)
            if idy in self.AliveList:
                print("投票先：" + str(idy))
                self.voted = idy
                return idy
            elif idx in self.AliveList:
                x = self.voted
                if len(self.AliveList) > 1:
                    self.AliveList.remove(idx)
                    x = random.choice(self.AliveList)
                print("投票先：" + str(x))
                self.voted = x
                return x
            else:
                x = 0
                if self.AliveList:
                    x = random.choice(self.AliveList)
                    self.voted = x
                else:
                    x = self.voted
                print("投票先：" + str(x))
                return x

        # 狂人
        if self.role == "POSSESSED":
            idx = self.wolfPredict()
            idy = self.seerPredict()
            print("候補：" + str(self.AliveList))
            print("人狼：" + str(idx))
            self.sum_wolf += 1
            self.pre_wolf.append(idx)
            print("占い師：" + str(idy))
            self.sum_seer += 1
            self.pre_seer.append(idy)
            if idy in self.AliveList:
                print("投票先：" + str(idy))
                self.voted = idy
                return idy
            else:
                if idx in self.AliveList:
                    self.AliveList.remove(idx)
                if self.AliveList:
                    x = random.choice(self.AliveList)
                    self.voted = x
                else:
                    x = self.voted
                print("投票先：" + str(x))
                return x

    def attack(self):
        if len(self.AliveList) >= 2:
            print("候補：" + str(self.AliveList))
            idx = self.possPredict()
            self.poss = idx
            print("狂人：" + str(idx))
            idy = self.seerPredict()
            print("占い師：" + str(idy))
            self.sum_seer += 1
            self.sum_poss += 1
            self.pre_seer.append(idy)
            self.pre_poss.append(idx)
            # if idy in self.AliveList:
            if idy in self.AliveList:
                print("襲撃先：" + str(idy))
                return idy
            elif idx in self.AliveList:
                self.AliveList.remove(idx)
                x = random.choice(self.AliveList)
                print("襲撃先：" + str(x))
                return x
            else:
                x = random.choice(self.AliveList)
                print("襲撃先：" + str(x))
                return x
        else:
            print("候補：" + str(self.AliveList))
            x = self.AliveList[0]
            print("襲撃先：" + str(x))
            return x

    def divine(self):

        # 初日は次の人を占う
        if self.DAY == 0:
            idx = random.choice(self.AliveList)
            # idx = (self.idx % 5) + 1
            print("占い先："+str(idx))
            self.DivinedList.append(idx)
            return idx
        # 二日目以降
        else:

            if self.DivinedList:
                for i in self.DivinedList:
                    if i in self.AliveList:
                        idy = i
                        self.AliveList.remove(i)
            idx = self.wolfPredict()
            self.sum_wolf += 1
            self.pre_wolf.append(idx)
            idy = self.possPredict()
            self.sum_poss += 1
            self.pre_poss.append(idx)
            if idx == None:
                return 1
            print("候補：" + str(self.AliveList))
            print("人狼：" + str(idx))
            print("狂人："+str(idy))
            print("占い先：" + str(idx))
            self.DivinedList.append(idx)
            return idx

    def guard(self):
        return self.base_info['agentIdx']

    def finish(self):
        return None
        print("【合計推定数】")
        print("人狼：%d" % self.sum_wolf)
        print("占い師：%d" % self.sum_seer)
        print("狂人：%d" % self.sum_poss)
        print("【合計的中数】")
        print("人狼：%d" % self.acc_wolf)
        print("占い師：%d" % self.acc_seer)
        print("狂人：%d" % self.acc_poss)
        wolf = 0
        seer = 0
        poss = 0
        if self.sum_wolf != 0:
            wolf = self.acc_wolf / self.sum_wolf * 100
        if self.sum_seer != 0:
            seer = self.acc_seer / self.sum_seer * 100
        if self.sum_poss != 0:
            poss = self.acc_poss / self.sum_poss * 100
        print("【的中率】")
        print("人狼：%.1f%%" % wolf)
        print("占い師：%.1f%%" % seer)
        print("狂人：%.1f%%" % poss)

        return None

    """
    予測用メソッド
    """

    def info_update(self, text):

        if text[1] == "talk":
            idx = str(text[4])
            if "COMINGOUT" in text[5] and "SEER" in text[5] and len(text[5]) <= 30:
                if "VILLAGER" in text[5]:
                    self.info[idx][0] = 1
                elif "SEER" in text[5]:
                    self.info[idx][1] = 1
                elif "POSSESSED" in text[5]:
                    self.info[idx][2] = 1
                elif "WEREWOLF" in text[5]:
                    self.info[idx][3] = 1
            if "DIVINED" in text[5] and len(text[5]) <= 35:
                result = (text[5].split("DIVINED Agent["))[1].split("] ")
                # print(result)
                idy = int(result[0])
                role = result[1]
                if "WEREWOLF" in role:
                    self.info[idx][4] = idy
                    self.info[str(idy)][11] += 1
                else:
                    self.info[idx][5] = idy
                    self.info[str(idy)][12] += 1
            if "VOTE" in text[5]:
                result = (text[5].split("VOTE Agent["))[1].split("]")
                # print(result)
                idy = int(result[0])
                self.info[idx][10] = idy
                # self.info[str(idy)][17] += 1
            if "ESTIMATE" in text[5]:
                result = (text[5].split("ESTIMATE Agent["))[1].split("] ")
                idy = int(result[0])
                role = result[1]
                if role == "WEREWOLF":
                    self.info[idx][6] = idy
                    # self.info[str(idy)][13] += 1
                elif role == "POSSESSED":
                    self.info[idx][7] = idy
                    # self.info[str(idy)][14] += 1
                elif role == "SEER":
                    self.info[idx][8] = idy
                    # self.info[str(idy)][15] += 1
                elif role == "VILLAGER":
                    self.info[idx][9] = idy
                    # self.info[str(idy)][16] += 1
            # if "Skip" in text[5]:
            #     self.info[idx][13] += 1
            # if not "Skip" in text[5] and not "Over" in text[5]:
            #     self.info[idx][14] += 1

        if text[1] == "finish":
            idx = int(text[2])
            if "WEREWOLF" in text[5]:
                if self.pre_wolf:
                    for i in self.pre_wolf:
                        if i == idx:
                            self.acc_wolf += 1
            if "SEER" in text[5]:
                if self.pre_seer:
                    for i in self.pre_seer:
                        if i == idx:
                            self.acc_seer += 1
            if "POSSESSED" in text[5]:
                if self.pre_poss:
                    for i in self.pre_poss:
                        if i == idx:
                            self.acc_poss += 1

    def wolfPredict(self):
        self.preInfo = [[]]
        for key, val in self.info.items():
            for i in val:
                self.preInfo[0].append(i)
        a = np.array(self.preInfo)
        predict = self.wolf_model.predict(a)
        # print(predict)
        idx = np.argsort(predict)
        # print(idx)
        for i in range(-1, -6, -1):
            if idx[0][i] + 1 in self.AliveList and idx[0][i] + 1 != self.idx:
                return idx[0][i] + 1

    def seerPredict(self):
        self.preInfo = [[]]
        for key, val in self.info.items():
            for i in val:
                self.preInfo[0].append(i)
        a = np.array(self.preInfo)
        predict = self.seer_model.predict(a)
        # print(predict)
        idx = np.argsort(predict)
        # print(idx)
        for i in range(-1, -6, -1):
            # if idx[0][i] + 1 != self.idx and idx[0][i]+1 != self.poss:
            if idx[0][i] + 1 != self.idx:
                return idx[0][i] + 1

    def possPredict(self):
        self.preInfo = [[]]
        for key, val in self.info.items():
            for i in val:
                self.preInfo[0].append(i)
        a = np.array(self.preInfo)
        predict = self.poss_model.predict(a)
        # print(predict)
        idx = np.argsort(predict)
        # print(idx)
        for i in range(-1, -6, -1):
            if idx[0][i] + 1 != self.idx:
                return idx[0][i] + 1


agent = Agent(myname)


# run
if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
