<?php
    // データベースの作成
    function create_db(){
            $db = new SQLite3("../db/wolf_battler.db");
            $db->exec("CREATE TABLE rooms(id INTEGER PRIMARY KEY,name text UNIQUE, setting INTEGER)");
            $db->exec('CREATE TABLE players(id INTEGER PRIMARY KEY,name text UNIQUE, agent_id INTEGER, room_id INTEGER)');
            $db->exec('CREATE TABLE messages(id INTEGER PRIMARY KEY,content text, agent_id INTEGER, room_id INTEGER)');
    
    }
    // プレイヤーの作成
    function create_player_name(){
        $db = new SQLite3("../db/wolf_battler.db");
        $db->exec('begin');
        try{
            $player_name = $_POST["player_name"];
            if($player_name != ""){
                $db->query('INSERT INTO players (name) VALUES '."('$player_name')");
            }
            $db->exec("commit");
            $db->close();
        }
        catch(Exception $e){
            $db->exec('rollback');
        }
    }

    // ルーム作成
    function create_room(){
        $db = new SQLite3("../db/wolf_battler.db");
        $db->exec("begin");
        try{
            $room_name = $_POST["room_name"];
            if($room_name != ""){
                $db->query('INSERT INTO rooms (name) VALUES '."('$room_name')");
            }
            $db->exec("commit");
            $db->close();
        }
        catch(Exception $e){
            $db->exec('rollback');
        }
    }

    // ルーム参加
    function join_room(){
        $db = new SQLite3("../db/wolf_battler.db");
        $room_name = $_POST["room_name"];
        // $room_name = "渕田研究室";
        $player_name = $_POST["player_name"];
        // $player_name = "神様";
        $agent_id = array();
        $agent_id_list = array(1,2,3,4,5);
        $rooms = $db->query('SELECT * FROM rooms WHERE name='."'$room_name'");
        $id=0;
        while ($result = $rooms->fetchArray(SQLITE3_ASSOC)){
            $id = $result["id"];
        }
        $agent_ids = $db->query('SELECT * FROM players WHERE room_id='."$id");
        while ($result2 = $agent_ids->fetchArray(SQLITE3_ASSOC)){
            if($result2["agent_id"] != null){
                array_push($agent_id, $result2["agent_id"]);
            }
        }
        foreach($agent_id_list as $val){
            if(!in_array($val,$agent_id)){
                echo($val);
                $db->query("UPDATE players SET agent_id=$val WHERE name='$player_name'");
                break;
            }
        }
        $db->query("UPDATE players SET room_id=$id WHERE name='$player_name'");
        $db->close();
    }

    // プレイヤーを取得する
    function get_player_name(){
        $db = new SQLite3("../db/wolf_battler.db");
        $players = $db->query("SELECT * FROM players");
        $player_list = array();
        while($result = $players->fetchArray(SQLITE3_ASSOC)){
            $player_list[] = $result["name"];
        }
        $db->close();
        echo(json_encode($player_list,JSON_UNESCAPED_UNICODE));
    }

    // ルーム名を取得する
    function get_room_name(){
        $db = new SQLite3("../db/wolf_battler.db");
        $rooms = $db->query("SELECT * FROM rooms");
        $room_list = array();   // キー：ルーム名、値：人数
        $room_name_list = array();
        while($room = $rooms->fetchArray(SQLITE3_ASSOC)){
            $room_name_list[] = $room["name"];
        }
        foreach($room_name_list as $room_name){
            $room_ids = $db->query("SELECT * FROM rooms WHERE name='$room_name'");
            while($room_id = $room_ids->fetchArray(SQLITE3_ASSOC)){
                $id = $room_id["id"];
                $room_counts = $db->query("SELECT COUNT(*) FROM players WHERE room_id=$id");
                while ($room_count = $room_counts->fetchArray()){
                    $room_list = array_merge($room_list,array($room_name=>$room_count[0]));
                }
            }
        }
        $db->close();
        echo(json_encode($room_list,JSON_UNESCAPED_UNICODE));
    }

    // ルーム退出
    function exit_room(){
        if(isset($_POST["room_name"])){
            $room_name = $_POST["room_name"];
            // $room_name = "渕田研究室";
            $player_name = $_POST["player_name"];
            // $player_name = "中原";
            $db = new SQLite3("../db/wolf_battler.db");
            $rooms = $db->query("SELECT * FROM rooms WHERE name='$room_name'");
            $room_id = 0;
            while($result = $rooms->fetchArray(SQLITE3_ASSOC)){
                $room_id = $result["id"];
            }
            $db->query("UPDATE players SET room_id=NULL, agent_id=NULL WHERE name='$player_name'");
            $player_counts = $db->query("SELECT COUNT(*) FROM players WHERE room_id=$room_id");
            while($result = $player_counts->fetchArray()){
                $player_count = $result[0];
                if($player_count == 0){
                    $db->close();
                    del_room($room_name);
                }
                else{
                    $db->close();
                }
            }
        }
    }

    // ルーム削除
    function del_room($room_name){
        $db = new SQLite3("../db/wolf_battler.db");
        $db->query("DELETE FROM rooms WHERE name='$room_name'");
        $db->close();
    }

    // プレイヤー削除
    function del_player($player_name){
        exit_room();
        $db = new SQLite3("../db/wolf_battler.db");
        $db->query("DELETE FROM players WHERE name='$player_name'");
        $db->close();
    }

    // プレイヤー情報の取得
    function get_player_info($room_name){
        $db = new SQLite3("../db/wolf_battler.db");
        $db->exec("begin");
        try{
            $rooms = $db->query("SELECT id FROM rooms WHERE name='$room_name'");
            $player_list = array();
            while($result = $rooms->fetchArray(SQLITE3_ASSOC)){
                $room_id = $result["id"];
                $players = $db->query("SELECT * FROM players WHERE room_id=$room_id");
                while($result2 = $players->fetchArray(SQLITE3_ASSOC)){
                    $player_list[] = $result2["name"];
                }
            }
            echo(json_encode($player_list,JSON_UNESCAPED_UNICODE));
        }
        catch(Exception $e){
            $db->exec('rollback');
        }
        
    }

    // 分岐用
    switch($_POST["func"]){
        case "create_player_name": create_player_name(); break;
        case "create_room": create_room(); break;
        case "join_room": join_room(); break;
        case "get_room_name": get_room_name(); break;
        case "get_player_name": get_player_name(); break;
        case "exit_room": exit_room(); break;
        case "del_player": del_player($_POST["player_name"]); break;
        case "del_room": del_room($_POST["room_name"]); break;
        case "get_player_info": get_player_info($_POST{"room_name"}); break;
    }
?>