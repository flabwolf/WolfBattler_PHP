function append_player_list() {
    $.ajax({
        url: "../php/ajax.php",
        type: "POST",
        dataType: "json",
        data: {
            "func": "get_player_name"
        }
    })
        .done(function (data) {
            console.log(data);
            $("#player_list").text("");
            if (!Object.keys(data).length) {
                console.log("現在プレイヤーはいません。");
                $("#player_list").append("<div class='content'><h3 class='player_name'>" + "現在プレイヤーはいません" + "</h3></div>").trigger("create");
            }
            else {
                console.log(data);
            }
            data.forEach(function (player_name) {
                $("#player_list").append("<div class='card'><div class='card-body'><div class='content'><h3 class='player_name'>" + player_name + "</h3>" + "<button class='del_player_btn btn-danger btn'>削除</button></div></div></div>").trigger("create");

            });
        })
        .fail(function () {
            console.log("プレイヤーリストの取得に失敗しました");
        });
}

// プレイヤーを削除する
function del_player() {
    $(document).on("click", ".del_player_btn", function () {
        var player_name = $(this).parent().find(".player_name").text();
        $.ajax({
            url: "../php/ajax.php",
            type: "post",
            data: {
                "func": "del_player",
                "player_name": player_name
            }
        })
            .done(function () {
                console.log(player_name + "を削除しました");
                append_player_list();
            });
    });
}

function append_room_list() {
    $.ajax({
        url: "../php/ajax.php",
        type: "post",
        dataType: "json",
        data: {
            "func": "get_room_name"
        }
    })
        .done(function (data) {
            $("#room_list").text("");
            if (!Object.keys(data).length) {
                console.log("現在ルームはありません。");
                $("#room_list").append("<div class='content'><h3 class='room_name'>" + "現在作成されてるルームはありません" + "</h3></div>").trigger("create");
            }
            else {
                console.log(data);
            }
            for (room_name in data) {
                $("#room_list").append("<div class='card'><div class='card-body'><div class='content'><h3 class='room_name'>" + room_name + "</h3>" + "<h4 class='player_num'>" + "現在：" + data[room_name] + "人</h4>" + "<button class='del_room_btn btn-danger btn'>削除</button></div></div></div>").trigger("create");
            }
        });
}

function del_room() {
    $(document).on("click", ".del_room_btn", function () {
        var room_name = $(this).parent().find(".room_name").text();
        $.ajax({
            url: "../php/ajax.php",
            type: "post",
            data: {
                "func": "del_room",
                "room_name": room_name
            }
        })
            .done(function () {
                console.log(room_name + "を削除しました");
                append_room_list();
            });
    });
}

function admin_login() {
    $("#admin_login_btn").on("click", function () {
        $admin_id = $("#admin_id").val();
        $admin_pw = $("#admin_pw").val();
        if ($admin_id == "f-lab" & $admin_pw == "suuri4f") {
            console.log("管理者ページにログインしました");
            hide_login_page();
            show_main_page();
        }
        else {
            console.log("認証に失敗しました");
        }
    });
}

function show_main_page() {
    $(".main_page").show();
}

function hide_main_page() {
    $(".main_page").hide();
}
function hide_login_page() {
    $(".login_page").hide();
}
$(function () {
    hide_main_page();
    admin_login();
    $("#player_list_btn").on("click", function () {
        append_player_list();
    });
    del_player();
    $("#room_list_btn").on("click", function () {
        append_room_list();
    });
    del_room();
});