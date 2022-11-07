import socket
import threading
import sys


def recv_msg():
    while True:
        recv_msg = s.recv(2048)
        if not recv_msg:
            sys.exit(0)
        #print('\n< ' + recv_msg)
        print(recv_msg.decode())


def send_msg(username, sock):
    try:
        while True:
            send_msg = input()
            if send_msg != '':
                send_msg = username + ': ' + send_msg
                s.send(send_msg.encode())
                # print(send_msg)
                #print('=== Message sent ===')
    except KeyboardInterrupt:
        print('KeyboardInterrupt, closing...')
    finally:
        sock.close()
        sys.exit()


s = socket.socket()
s.connect((sys.argv[1], int(sys.argv[2])))

username = input('Username: ')

print("Connected to the server!")

t = threading.Thread(target=recv_msg)
t.start()

# event loop
send_msg(username, s)
