var flag = true;
var player_name;
var room_name;
var player_info = { "1": [null, null], "2": [null, null], "3": [null, null], "4": [null, null], "5": [null, null] } // 番号：[名前、生死]
var first, second, third;
var send_contents;

// ウェブソケットの立ち上げ
function create_web_socket() {
    // ws = new WebSocket("ws://localhost:3000/htmls/room.html");
    ws = new WebSocket("ws://10.200.11.23:443/htmls/room.html");

    ws.onopen = function () {
        ws.send(JSON.stringify(send_contents));
        send_contents["mode"] = "normal"
    };
    ws.onmessage = function (e) {
        var receiveData = JSON.parse(e.data)
        console.log(receiveData)
        // ルーム内のプレイヤー名の取得
        if (receiveData["mode"] == "INITIALIZE") {
            Object.keys(receiveData["nameMap"]).forEach(function (key) {
                player_info[key][0] = receiveData["nameMap"][key];
            });
            Object.keys(receiveData["statusMap"]).forEach(function (key) {
                player_info[key][1] = receiveData["statusMap"][key];
            });
        }
        // プレイヤーの生死情報の取得
        if (receiveData["mode"] == "RESULT") {
            Object.keys(receiveData["statusMap"]).forEach(function (key) {
                player_info[key][1] = receiveData["statusMap"][key];
            });
        }
        // ゲーム開始時
        if (receiveData["mode"] == "start") {
            $(".chat_screen").text("");
            $(".free").hide();
            $(".divine");
            $(".vote");
            $(".attack");
            $(".talk").show();
        }

        // 投票、襲撃、占いフェーズ時
        if ((receiveData["mode"] == "VOTE") | (receiveData["mode"] == "ATTACK") | (receiveData["mode"] == "DIVINE")) {
            $(".talk").hide()
            $(".other").show();
            set_other_list();
        }

        // 夜フェーズ時
        else if (receiveData["mode"] == "NIGHT") {
            $(".talk").hide();
            $(".free").hide();
            $(".divine").hide();
            $(".attack").hide();
            $(".vote").hide();
        }
        // 昼フェーズ時
        else if (receiveData["mode"] == "TALK") {
            $(".talk").show();
            $(".free").hide();
            $(".other").hide();
        }
        $(".chat_screen").append("<div class='card-text'>" + receiveData["message"] + "</div>");
        $('.chat_screen').animate({ scrollTop: $('.chat_screen')[0].scrollHeight }, 'fast');
        // }
    };

    $("#normal_chat_btn").on("click", function (e) {
        e.preventDefault();
        var msg = $("#normal_chat_msg").val();
        $("#normal_chat_msg").val("");
        send_contents["message"] = msg;

        ws.send(JSON.stringify(send_contents));
    });
    $(window).on("beforeunload", function () {
        logout_player();
        send_contents["mode"] = "exit";
        ws.send(JSON.stringify(send_contents));
        ws.close();
    });
    game_start();
    speak_talk();
    speak_other();
}


// ルーム名をセットする
function set_room_name() {
    $(".room_name").text(room_name);
}

// プレイヤー名をセットする
function set_player_name() {
    $("#player_name").text(player_name);
}

// プレイヤーをログアウトする
function logout_player() {
    $(window).on("beforeunload", function () {
        if (flag) {
            var urlParams = new URLSearchParams(window.location.search);
            var result = $.isEmptyObject(urlParams);
            if (!result) {
                $.ajax({
                    url: "../php/ajax.php",
                    type: "POST",
                    async: false,
                    data: {
                        "func": "del_player",
                        "player_name": player_name,
                        "room_name": room_name
                    }
                })
            }
        }
    });
}

// ルーム退出
function exit_room() {
    $("#exit_room_btn").on("click", function () {
        $.ajax({
            url: "../php/ajax.php",
            async: false,
            type: "POST",
            data: {
                "func": "exit_room",
                "room_name": room_name,
                "player_name": player_name
            }
        })
            .done(function (data) {
                console.log("ルームを退出しました");
                var url = "/?player_name=" + player_name;
                flag = false;
                window.history.back(-1);
            });
    })
}

// ゲーム開始ボタン
function game_start() {
    $("#game_start_btn").on("click", function () {
        send_contents["mode"] = "start"
        ws.send(JSON.stringify(send_contents));
    });
}

// セレクトリストの内容表示
function set_select_val() {
    $("#first_choice").bind("change", function () {
        first = $("#first_choice").val();
        console.log(first);
        if (first == "カミングアウト") {
            $("#third_choice").show();
            $("#second_choice").hide();
            $("#third_choice").html("");
            $("#third_choice").append("<option>村人</option>");
            $("#third_choice").append("<option>占い師</option>");
            $("#third_choice").append("<option>狂人</option>");
            $("#third_choice").append("<option>人狼</option>");
        }
        else if (first == "推定発言") {
            $("#third_choice").show();
            $("#second_choice").show();
            $("#second_choice").html("");
            $("#third_choice").html("");
            Object.keys(player_info).forEach(function (key) {
                $("#second_choice").append("<option class='target_name'>" + player_info[key][0] + "</option>");
            });
            $("#third_choice").append("<option>村人</option>");
            $("#third_choice").append("<option>占い師</option>");
            $("#third_choice").append("<option>狂人</option>");
            $("#third_choice").append("<option>人狼</option>");

        }
        else if (first == "投票発言") {
            $("#third_choice").hide();
            $("#second_choice").show();
            $("#second_choice").html("");
            Object.keys(player_info).forEach(function (key) {
                $("#second_choice").append("<option class='target_name'>" + player_info[key][0] + "</option>");
            });
        }
    });
}

// 投票、襲撃、占い用の選択リストのセット
function set_other_list() {
    $("#other_list").text("")
    Object.keys(player_info).forEach(function (key) {
        $("#other_list").append("<option class='target_name'>" + player_info[key][0] + "</option>");
    });
}

// 投票、襲撃、占いの対象を送信
function speak_other() {
    $("#other_btn").on("click", function () {
        send_contents["mode"] = "other";
        var target = $("#other_list").val();
        send_contents["message"] = target;
        ws.send(JSON.stringify(send_contents));
    });
}


// 発言する（ゲーム中）
function speak_talk() {
    $("#game_chat_btn").on("click", function () {
        first = $("#first_choice").val();
        send_contents["mode"] = "talk";
        console.log(first, second, third)
        if (first == "カミングアウト") {
            third = $("#third_choice").val();
            send_contents["message"] = [first, third];
            ws.send(JSON.stringify(send_contents));
        }
        else if (first == "推定発言") {
            second = $("#second_choice").val();
            third = $("#third_choice").val();
            send_contents["message"] = [first, second, third];
            ws.send(JSON.stringify(send_contents));
        }
        else if (first == "投票発言") {
            second = $("#second_choice").val();
            send_contents["message"] = [first, second];
            ws.send(JSON.stringify(send_contents));
        }
    });
}

$(function () {
    // $(".free").hide();
    $(".other").hide();
    $(".talk").hide();
    $("#second_choice").hide();
    var urlParams = new URLSearchParams(window.location.search);
    player_name = urlParams.get("player_name");
    room_name = urlParams.get("room_name");
    send_contents = { "player_name": player_name, "room_name": room_name, "message": "", "mode": "init" };
    create_web_socket();
    set_room_name();
    set_player_name();
    exit_room();
    set_select_val();
});