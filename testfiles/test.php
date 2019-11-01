<?php
$db = new SQLite3("../db/wolf_battler.db");
$db->exec("begin");
$room_name = "渕田研究室";
try{
    $rooms = $db->query("SELECT id FROM rooms WHERE name='$room_name'");
            $player_list = array();
            while($result = $rooms->fetchArray(SQLITE3_ASSOC)){
                $room_id = $result["id"];
                $players = $db->query("SELECT * FROM players WHERE id=$room_id");
                while($result2 = $players->fetchArray(SQLITE3_ASSOC)){
                    $player_list[] = $result2["name"];
                }
            }
            echo(json_encode($player_list,JSON_UNESCAPED_UNICODE));
}
catch(Exception $e){
    $db->exec('rollback');
    echo("エラー");
}
?>