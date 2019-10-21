// 閉じるフラグ
var flag = true;

// 作成済みのルームを表示する
function append_join_room() {
    $("#join_room_link").on("click", function () {
        $.ajax({
            url: "php/ajax.php",
            type: "POST",
            dataType: "json",
            data: {
                "func": "get_room_name"
            }
        })
            .done(function (data) {
                console.log("ルームリストを更新しました。");
                $("#join_room_list").text("");
                if (!Object.keys(data).length) {
                    console.log("現在ルームはありません。");
                    $("#join_room_list").append("<div class='content'><h3 class='room_name'>" + "現在作成されてるルームはありません" + "</h3></div>").trigger("create");
                }
                else {
                    console.log(data);
                }
                for (room_name in data) {
                    if (data[room_name] >= 5) {
                        console.log(room_name + "は満員です。");
                        $(".join_room").append("<div class='content'><h3 class='room_name'>" + room_name + "</h3>" + "<h4 class='player_num'>" + "現在：" + data[room_name] + "人</h4>" + "<button class='enter_room_btn btn' disabled>参加</button></div>").trigger("create");
                    }
                    else {
                        $(".join_room").append("<div class='card'><div class='card-body'><div class='content'><h3 class='room_name'>" + room_name + "</h3>" + "<h4 class='player_num'>" + "現在：" + data[room_name] + "人</h4>" + "<button class='enter_room_btn btn-danger btn'>参加</button></div></div></div>").trigger("create");
                    }

                }
            })
            .fail(function () {
                console.log("失敗");
            });
    });
}

// ルームを選択する
function select_room() {
    $(document).on("click", ".enter_room_btn", function () {
        var urlParams = new URLSearchParams(window.location.search);
        var room_name = $(this).parent().find(".room_name").text();
        join_room(room_name);
        console.log(room_name);
        var player_name = urlParams.get("player_name");
        var url = "htmls/room.html?room_name=" + room_name + "&player_name=" + player_name;
        flag = false;
        window.location.href = url;
    });
}

// ルームに参加
function join_room(room_name) {
    var urlParams = new URLSearchParams(window.location.search);
    var player_name = urlParams.get("player_name");
    $.ajax({
        url: "php/ajax.php",
        type: "POST",
        data: {
            "func": "join_room",
            "room_name": room_name,
            "player_name": player_name
        }
    })
        .done(function (data) {
            console.log("ルームに参加しました");
            var url = "htmls/room.html?room_name=" + room_name + "&player_name=" + player_name;
            flag = false;
            window.location.href = url;
        })
        .fail(function () {
            console.log("ルームの参加に失敗しました");
        });
}

// ルーム作成
function create_room() {
    $("#create_room_btn").on("click", function (e) {
        e.preventDefault();
        var room_name = $("#input_room_name").val();
        $("#input_room_name").val("");
        $.ajax({
            url: "php/ajax.php",
            type: "POST",
            data: {
                "func": "create_room",
                "room_name": room_name
            }
        })
            .done(function (data) {
                if (data.length <= 20) {
                    console.log("ルーム名：" + room_name);
                    join_room(room_name);
                }
                else {
                    console.log("既に使用されている名前です");
                    $(".used_name").text("");
                    $(".used_name").append("既に使用されている名前です！").trigger("create");
                }
            })
            .fail(function () {
                console.log("ルームの作成に失敗しました");
            });
    });
}

// プレイヤー作成
function create_player_name() {
    $("#create_player_name").on("click", function (e) {
        e.preventDefault();
        var player_name = $("#input_player_name").val();
        $("#input_player_name").val("");
        $.ajax({
            url: "php/ajax.php",
            type: "POST",
            async: false,
            data: {
                "func": "create_player_name",
                "player_name": player_name
            }
        })
            .done(function (data) {
                console.log(data);
                if (data.length <= 20) {
                    console.log("プレイヤー名：" + player_name);
                    $("#player_name").append(player_name);
                    var url = "?player_name=" + player_name;
                    var path = location.pathname;
                    window.history.pushState(null, null, path + url);
                    set_player_name();
                }
                else {
                    console.log("既に使用されている名前です");
                    $(".used_name").text("");
                    $(".used_name").append("既に使用されている名前です！").trigger("create");
                }
            })
            .fail(function () {
                console.log("プレイヤーの作成に失敗しました");
            });
    });
}

// プレイヤーをログアウトする
function logout_player() {
    $(window).on("beforeunload", function () {
        if (flag) {
            var urlParams = new URLSearchParams(window.location.search);
            var result = $.isEmptyObject(urlParams);
            if (!result) {
                var player_name = urlParams.get("player_name");
                $.ajax({
                    url: "php/ajax.php",
                    type: "POST",
                    async: false,
                    data: {
                        "func": "del_player",
                        "player_name": player_name,
                    }
                })
            }
        }
    });
}

// プレイヤー名をセットする
function set_player_name() {
    var urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("player_name") != null) {
        var player_name = urlParams.get("player_name");
        $("#player_name").html(player_name);
        show_start_page();
        hide_crate_player();
    }
}

// プレイヤー登録画面の非表示
function hide_crate_player() {
    $(".create_player").hide();
}

// スタートページの非表示
function hide_start_page() {
    $(".start_page").hide();
}

// スタートページの表示
function show_start_page() {
    $(".start_page").show();
}

// ページ読み込み時の動作
window.onload = function () {
    var urlParams = new URLSearchParams(window.location.search);

    // プレイヤーを登録していなかったら
    if (urlParams.get(["player_name"]) == null) {
        console.log("プレイヤー名を入力してください。");
        this.hide_start_page();
    }
    else {
        this.hide_crate_player();
    }
}

$(function () {
    $("#input_player_name").focus();
    set_player_name();
    create_player_name();
    create_room();
    append_join_room();
    select_room();
    logout_player();
});