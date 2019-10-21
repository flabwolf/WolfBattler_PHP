import socket
import threading
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 接続先
host = "localhost"
port = 3000
sock.connect((host, port))


def Handler(sock):
    while True:
        try:
            read = sock.recv(4096)  # (3)
            print(read.decode())
            if (len(read) < 4096):
                continue
            # end
        except Exception as e:
            print("接続がありません")
            continue


while (True):
    thread = threading.Thread(target=Handler, args=(sock,), daemon=True)
    thread.start()
    your_input = input()  # (1)
    print(sock.send(your_input.encode("UTF-8")))  # (2)
