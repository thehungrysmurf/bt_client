import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 12345))
s.listen(3)
print "Server is ready, waiting for client to connect..."

while True:
    client_socket, address = s.accept()
    print "A client has connected from address %s, port %s."%(address[0], address[1])

    while True:
        data = raw_input("Server's message: ")
        client_socket.send(data)

    data2 = client_socket.recv(512)
    print "Client sent you this message: ", data2

s.close()

