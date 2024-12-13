import socket
import select
import pickle

HEADERSIZE = 10
IP = 'localhost'
PORT = 2530
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IP, PORT))
s.listen()

sockets_list = [s]

chatrooms = ['first','second','third']
pick_chatroom = pickle.dumps(chatrooms)

clients = {}
clients_room = {}

for room in chatrooms:
    clients_room[room] = []

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADERSIZE)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8'))

        if not client_socket in sockets_list:
            return {'header': message_header, 'data': client_socket.recv(message_length),'chatroom':False}

        if clients[client_socket]['chatroom'] is False:
            return client_socket.recv(message_length)

        return {"header": message_header, "data": client_socket.recv(message_length)}

    except Exception as e:
        print(str(e))
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list,[],sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == s:
            client_socket, client_address = s.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user
            print(clients)
            print()
            print(f"New connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")
            datalen = f'{len(pick_chatroom):<{HEADERSIZE}}'.encode('utf-8')
            client_socket.send(datalen)
            client_socket.send(pick_chatroom)

        else:
            message = receive_message(notified_socket)

            if clients[notified_socket]['chatroom'] == False:
                if message.decode('utf-8') in clients_room.keys():
                    clients[notified_socket]['chatroom'] = message.decode('utf-8')
                    clients_room[message.decode('utf-8')].append(notified_socket)
                    continue
                continue

            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]

            print(f"Received message from {user['data'].decode('utf-8')}:{message['data'].decode('utf-8')}")
            for client_socket in clients_room[user['chatroom']]:
                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
