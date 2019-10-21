<?php
    $socket = socket_create_pair(AF_INET, SOCK_STREAM, SOL_TCP);
    if(!is_resource($socket)) onSocketFailure("Failed to create socket");
?>