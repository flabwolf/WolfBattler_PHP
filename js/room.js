var flag = true;
var player_name = ""
var room_name = ""

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
        $("#normal_chat_body").append("<div class='card-text'>" + e.data + "</div>");
        $('#normal_chat_body').animate({ scrollTop: $('#normal_chat_body')[0].scrollHeight }, 'fast');
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
}

// ルーム名をセットする
function set_room_name() {
    $("#room_name").append(room_name);
}

// プレイヤー名をセットする
function set_player_name() {
    $("#player_name").html(player_name);
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


$(function () {
    var urlParams = new URLSearchParams(window.location.search);
    player_name = urlParams.get("player_name");
    room_name = urlParams.get("room_name");
    create_web_socket();
    set_room_name();
    set_player_name();
    exit_room();
});