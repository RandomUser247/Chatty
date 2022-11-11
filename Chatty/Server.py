import json
import socket
from threading import Thread

HOST = "0.0.0.0"
PORT = 8081
clients = {}


def send_error(c, text='something went wrong'):
    # sends error message
    text_raw = bytes(text, 'utf-8')
    c.sendall(b'e')
    c.sendall(int.to_bytes(len(text_raw), 2, 'big'))
    c.sendall(text_raw)


def new_client(c):
    # receives message, when a new client logged in, updates internal client list and broadcasts it to all clients
    print('new client logged in')
    msg_length_raw = c.recv(2)
    msg_length = int.from_bytes(msg_length_raw, 'big')
    name_raw = c.recv(msg_length)
    name = str(name_raw, 'utf-8')
    print(name)
    clients[name] = c
    # msg all clients name of new client
    send_message(c, b'n', msg_length_raw, name_raw)
    send_user_list(c)


def send_user_list(c):
    # create a list from all elements in clients.keys [x for x in keys] and
    # join list elements together with ', ' in a str
    usernames = ', '.join([x for x in clients.keys()])
    list_raw = bytes(usernames, 'utf-8')
    list_length_raw = int.to_bytes(len(list_raw), 2, 'big')
    c.sendall(b'u')
    c.sendall(list_length_raw)
    c.sendall(list_raw)
    # sende steuerzeichen   schritt 1
    # sende msg_length      schritt 2
    # sende msg_raw         schritt 3


def client_left(c):
    # receives message, when a new client logged in, updates internal client list and broadcasts it to other clients
    index = list(clients.values()).index(c)
    con_name = list(clients)[index]
    # get msg length and convert name to bytes
    name_raw = bytes(con_name, 'utf-8')
    msg_length_raw = int.to_bytes(len(name_raw), 2, 'big')
    del clients[con_name]
    c.close()
    send_message(c, b'l', msg_length_raw, name_raw)


def config_client_name(c):  # ToDo implement
    # receives message, when a client changes name, updates internal client list and broadcasts name change to all
    # clients
    msg_length = int.from_bytes(c.recv(2), 'big')
    # clients[str(c.recv(msg_length), 'utf-8')] = clients[]


def normal_message(c):
    # receive message, broadcast it to all clients
    print('got message')
    header_length_raw = c.recv(2)  # Bytes
    header_length = int.from_bytes(header_length_raw, 'big')  # konvertieren Bytes zu "lesbarer Nachricht".
    header_raw = c.recv(header_length)
    header = json.loads(str(header_raw, 'utf-8'))
    message_raw = c.recv(header['length'])
    message = str(message_raw, 'utf-8')
    print(f"Header length: {header_length}\nHeader: {header}\nMessage: {message}")
    send_message(c, b's', header_length_raw, header_raw, message_raw)


def whispered(c):
    # receives message, pass it to receiver client
    print('got whisper')
    header_length_raw = c.recv(2)
    header_length = int.from_bytes(header_length_raw, 'big')
    header_raw = c.recv(header_length)
    header = json.loads(str(header_raw, 'utf-8'))
    msg_raw = c.recv(header['length'])
    msg = str(msg_raw, 'utf-8')
    send_message(c, b'w', header_length_raw, header_raw, msg_raw,
                 receiver=header['receiver'])


def send_message(c, *args, receiver='broadcast'):
    """ c is the connection the server got the recent message from
        takes a number of arguments which are sent in order which is given
        default receiver is broadcast, can be changed to single receiver"""
    print(clients)
    if receiver != 'broadcast':
        for conn in {c, clients[receiver]}:
            for msg_part in args:
                conn.sendall(msg_part)
    else:
        for name, conn in clients.items():
            for msg_part in args:
                conn.sendall(msg_part)


# clients.keys() <- alle Usernamen
def receive(c):
    # c is the connection for this client
    while True:
        try:
            message_type = str(c.recv(1), 'utf-8')
        except ConnectionError:
            client_left(c)
            print('connection lost')
            break
        print(message_type)
        match message_type:
            case 's':
                normal_message(c)
            case 'w':
                whispered(c)
            case 'n':
                new_client(c)
            case 'l':
                client_left(c)
                break
            case 'c':
                config_client_name(c)
            case _:
                pass


""" Verbindung kommt an -> Connection
    Server 'hört' auf dieser connection in einem Thread
    Steuerzeichen kommt an [w, s, l, n, c]
    wartet auf die Nachricht mit der Länge der darauffolgenden Nachricht 1Byte -> 2Byte -> xByte
    """
if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind((HOST, PORT))
        s.listen()
        print('server is now listening')
        while True:
            connection, address = s.accept()
            Thread(target=receive, args=(connection,)).start()
