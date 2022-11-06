import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()  # efficient I/O multiplexing


def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted new client {addr[0]}:{addr[1]}")
    conn.setblocking(False)
    # qui si crea un oggetto in cui includere i dati per tutta la vita del socket
    # questo perché si deve sapere quando il client è pronto per leggere e scrivere
    # tutti e due gli eventi sono impostati tramite l'operatore bitwise OR
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # registro il socket
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    # socket
    sock = key.fileobj
    # data
    data = key.data
    # mask & selectors.EVENT_READ ritorna TRUE se il socket è pronto per leggere
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(2048)
        print(f"Received {recv_data} from {data.addr[0]}:{data.addr[1]}")
        # aggiungo i dati a data.outb da inviare successivamente
        if recv_data:
            data.outb += recv_data
        # se non riceviamo dati il client ha chiuso il suo socket
        # e quindi anche il server dovrebbe chiuderlo
        else:
            print(f"Closing connection to {data.addr[0]}:{data.addr[1]}")
            # eliminiamo la registrazione in modo che non venga più monitorato
            sel.unregister(sock)
            sock.close()
    # se il socket è pronto per scrivere
    # invio data.outb al client
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Sending {data.outb!r} to {data.addr[0]}:{data.addr[1]}")
            # sent contiene il numero di byte inviati (ritornato da send())
            sent = sock.send(data.outb)
            # è un numero che non mi serve, quindi uso la notazione slice
            # per eliminarlo
            data.outb = data.outb[sent:]


def main(HOST, PORT):
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f"Listening on {HOST}:{PORT}")
    # non blocking mode
    lsock.setblocking(False)
    # registra il socket da monitorare con sel.select() per gli eventi a cui si è interessati.
    # Per il socket in ascolto, si vogliono leggere gli eventi: selectors.EVENT_READ
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            # select(timeout=None) ferma tutto finché non ci sono socket pronti per l'I/O
            # ritorna una tupla per ogni socket contenente una key ed una mask
            # es: key.fileobj è un socket
            events = sel.select(timeout=None)
            for key, mask in events:
                # se key.data è None bisogna prima accettare il socket
                # chiamo accept_wrapper() in modo da accettare la connessione e
                # registrarla con il selector
                if key.data is None:
                    accept_wrapper(key.fileobj)
                # in questo caso il client è stato già accettato
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Closed by KeyboardInterrupt")
    finally:
        sel.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <HOST> <PORT>")
    else:
        main(sys.argv[1], int(sys.argv[2]))
