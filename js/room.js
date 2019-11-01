var flag = true;
var player_name;
var room_name;
var player_info;
var first, second, third;
var send_contents;

// ウェブソケットの立ち上げ
function create_web_socket() {
    // var url = "ws://localhost:3000/htmls/room.html?room_name=" + room_name + "&player_name=" + player_name
    ws = new WebSocket("ws://localhost:3000/htmls/room.html");
    // ws = new WebSocket("ws://f-server.ibe.kagoshima-u.ac.jp:3000/htmls/room.html");

    ws.onopen = function () {
        ws.send(JSON.stringify(send_contents));
        send_contents["mode"] = "normal"
    };
    ws.onmessage = function (e) {
        var receiveData = JSON.parse(e.data)
        // if (receiveData["room_name"] == room_name) {
        console.log(receiveData)
        // ゲーム開始時
        if (receiveData["mode"] == "start") {
            $(".chat_screen").text("");
            $(".free").hide();
            $(".divine");
            $(".vote");
            $(".attack");
            $(".talk").show();
            get_player_info();
        }
        // 投票フェイズ時
        else if (receiveData["mode"] == "vote") {
            $(".chat_screen").text("");
            $(".talk").hide();
            $(".free").hide();
            $(".divine").hide();
            $(".attack").hide();
            $(".vote").show();
            get_player_info();
            set_vote_list();
        }
        // 占いフェイズ時
        else if (receiveData["mode"] == "divine") {
            $(".chat_screen").text("");
            $(".talk").hide();
            $(".free").hide();
            $(".divine").show();
            $(".attack").hide();
            $(".vote").hide();
            get_player_info();
            set_divine_list();
        }
        // 襲撃フェーズ時
        else if (receiveData["mode"] == "divine") {
            $(".chat_screen").text("");
            $(".talk").hide();
            $(".free").hide();
            $(".divine").hide();
            $(".attack").show();
            $(".vote").hide();
            get_player_info();
            set_divine_list();
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
    speak();
    vote();
    divine();
    attack();
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
            player_info.forEach(function (data) {
                $("#second_choice").append("<option class='target_name'>" + data + "</option>");
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
            player_info.forEach(function (data) {
                $("#second_choice").append("<option>" + data + "</option>");
            });
        }
    });
}

// 投票先の名前をセットする
function set_vote_list() {
    $("#vote_list").val();
    player_info.forEach(function (data) {
        $("#vote_list").append("<option class='target_name'>" + data + "</option>");
    });
}

// 投票する
function vote() {
    $("#vote_btn").on("click", function () {
        send_contents["mode"] = "vote";
        var target = $("#vote_list").val();
        send_contents["message"] = target;
        ws.send(JSON.stringify(send_contents));
    });
}

// 占い先をセットする
function set_divine_list() {
    $("#divine_list").val();
    player_info.forEach(function (data) {
        $("#divine_list").append("<option class='target_name'>" + data + "</option>");
    });
}

// 投票する
function divine() {
    $("#divine_btn").on("click", function () {
        send_contents["mode"] = "divine";
        var target = $("#divine_list").val();
        send_contents["message"] = target;
        ws.send(JSON.stringify(send_contents));
    });
}

// 襲撃先をセットする
function set_attack_list() {
    $("#attack_list").val();
    player_info.forEach(function (data) {
        $("#attack_list").append("<option class='target_name'>" + data + "</option>");
    });
}

// 投票する
function attack() {
    $("#attack_btn").on("click", function () {
        send_contents["mode"] = "attack";
        var target = $("#attack_list").val();
        send_contents["message"] = target;
        ws.send(JSON.stringify(send_contents));
    });
}

// ルーム内のプレイヤー情報取得
function get_player_info() {
    $.ajax({
        url: "../php/ajax.php",
        dataType: "json",
        type: "post",
        async: false,
        data: {
            "func": "get_player_info",
            "room_name": room_name
        }
    })
        .done(function (data) {
            console.log(data);
            player_info = data;
            $("#second_choice").hide();
        });
}

// 発言する（ゲーム中）
function speak() {
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
    $(".vote").hide();
    $(".talk").hide();
    $(".divine").hide();
    $(".attack").hide();
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