import socket
import threading
import sys


def recv_msg():
    while True:
        recv_msg = s.recv(2048)
        if not recv_msg:
            sys.exit()
        print(recv_msg.decode())


def send_msg(username, sock):
    try:
        while True:
            send_msg = input()
            if send_msg != '':
                send_msg = username + ': ' + send_msg
                s.send(send_msg.encode())
    except KeyboardInterrupt:
        print('KeyboardInterrupt, closing...')
    finally:
        sock.close()
        sys.exit()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <HOST> <PORT>')
    else:
        username = input('Username: ')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((sys.argv[1], int(sys.argv[2])))
        print("Connected to the server!")
        s.sendall(username.encode())

        t = threading.Thread(target=recv_msg)
        t.start()

        # event loop
        send_msg(username, s)
