var flag = true;

// ルーム名をセットする
function set_room_name() {
    var urlParams = new URLSearchParams(window.location.search);
    var room_name = urlParams.get("room_name");
    $("#room_name").append(room_name);
}

// プレイヤー名をセットする
function set_player_name() {
    var urlParams = new URLSearchParams(window.location.search);
    var player_name = urlParams.get("player_name");
    $("#player_name").html(player_name);
}

// プレイヤーをログアウトする
function logout_player() {
    $(window).on("beforeunload", function () {
        if (flag) {
            var urlParams = new URLSearchParams(window.location.search);
            var result = $.isEmptyObject(urlParams);
            if (!result) {
                var player_name = urlParams.get("player_name");
                var room_name = urlParams.get("room_name");
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
        var urlParams = new URLSearchParams(window.location.search);
        var room_name = urlParams.get("room_name");
        var player_name = urlParams.get("player_name");
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
    set_room_name();
    set_player_name();
    exit_room();
    logout_player();
});