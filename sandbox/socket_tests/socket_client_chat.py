import socket

c = socket.socket()
port = 12345
c.connect(("localhost", 12345))

while True:
    data = c.recv(1024)
    print "Server sent you this message: ", data
    data = raw_input("Client's message: ")
    c.send(data)

c.close()
