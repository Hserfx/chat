import socket

HEADERSIZE = 10
IP = 'localhost'
PORT = 2530

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)
