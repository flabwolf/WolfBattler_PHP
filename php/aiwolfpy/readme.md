#gamemaster

リクエスト処理の流れメモ

//ここはいらないかも//
NAME
ROLE

//ここから必要//
INITIALIZE:ゲームの初期化
↓
DAILY_INITIALIZE(0日目):
↓
DAILY_FINISH(0日目):
↓
DIVINE:占い師に向けて飛ばす。次のDIALY_INITIALIZEでdivineResultに値を格納。
↓
DAILY_INITIALIZE(1日目):占い師はdivineResultで占い結果を確認できる
↓
TALK(規定回数行う)
↓
DAILY_FINISH(1日目)
↓
VOTE(リクエストだけ)
↓
VOTE(インフォも飛ばす)
ここで人が死ぬ処理
↓
DIVINE
↓
DAILY_INITIALIZE(2日目)
↓
TALK()
↓
DAILY_FINISH
↓
VOTE
↓
FINISH(勝敗が決したとき)


gameInfoのtalkListに各talkHistoryを格納しておく。