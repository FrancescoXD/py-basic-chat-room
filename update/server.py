import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

SOCKET_LIST = []

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted new client {addr[0]}:{addr[1]}")
    SOCKET_LIST.append(conn)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(2048)
        print(f"Received {recv_data} from {data.addr[0]}:{data.addr[1]}")
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr[0]}:{data.addr[1]}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Sending {data.outb!r} to all clients")
            for client in SOCKET_LIST:
                if client != sock:
                    sent = client.send(data.outb)
                    data.outb = data.outb[sent:]


def main(HOST, PORT):
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f"Listening on {HOST}:{PORT}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Closed by KeyboardInterrupt")
        lsock.close()
    finally:
        sel.close()
        lsock.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <HOST> <PORT>")
    else:
        main(sys.argv[1], int(sys.argv[2]))
