var flag = true;
var player_name;
var room_name;
var player_info;
var first, second, third

// ウェブソケットの立ち上げ
function create_web_socket() {
    // var url = "ws://localhost:3000/htmls/room.html?room_name=" + room_name + "&player_name=" + player_name
    ws = new WebSocket("ws://localhost:3000/htmls/room.html");
    // ws = new WebSocket("ws://f-server.ibe.kagoshima-u.ac.jp:3000/htmls/room.html");


    ws.onopen = function () {
        ws.send(player_name + "が入室しました");
        // ws.send("Hello");
    };
    ws.onmessage = function (e) {
        console.log(e.data);
        if (e.data == "ゲームを開始しました。") {
            $(".game_before").hide();
            $(".game_after").show();
            set_room_name();
            get_player_info();
        }
        $(".chat_screen").append("<div class='card-text'>" + e.data + "</div>");
        $('.chat_screen').animate({ scrollTop: $('.chat_screen')[0].scrollHeight }, 'fast');
    };

    $("#normal_chat_btn").on("click", function (e) {
        e.preventDefault();
        var msg = $("#normal_chat_msg").val();
        $("#normal_chat_msg").val("");
        ws.send(player_name + " > " + msg);
    });
    $(window).on("beforeunload", function () {
        logout_player();
        ws.send(player_name + "が退室しました");
        ws.close();
    });

    speak();

    game_start();
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
        // $(".game_before").hide();
        // $(".game_after").show();
        // set_room_name();
        // get_player_info();
        ws.send("ゲームを開始しました。");
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
        console.log(first, second, third)
        if (first == "カミングアウト") {
            third = $("#third_choice").val();
            console.log(first, second, third)
            ws.send(first + " " + player_name + " " + third);
        }
        else if (first == "推定発言") {
            second = $("#second_choice").val();
            third = $("#third_choice").val();
            console.log(first, second, third)
            ws.send(first + " " + player_name + " " + second + " " + third);
        }
        else if (first == "投票発言") {
            second = $("#second_choice").val();
            console.log(first, second, third)
            ws.send(first + " " + player_name + " " + second);
        }
    });
}

$(function () {
    $(".game_after").hide();
    var urlParams = new URLSearchParams(window.location.search);
    player_name = urlParams.get("player_name");
    room_name = urlParams.get("room_name");
    create_web_socket();
    set_room_name();
    set_player_name();
    exit_room();
    set_select_val();
});