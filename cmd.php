<?php
    // $port = $_POST["port"];
    echo("hello");
    $port = 3001;
    // $command = "nohup python websocket.py -p $port 2>/dev/null &";
    $command = "dir";
    exec($command,$out);
    print($out[0]);
?>