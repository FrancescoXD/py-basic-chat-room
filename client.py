import socket
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data_sent = input("Write some text to send to the server: ")
    #s.sendall(data_sent.encode())
    s.send(data_sent.encode())
    data = s.recv(2048)

print(f"Data received from server: {data}")
