import socket

s = socket.socket()
host = socket.gethostname()
print "This machine's hostname: ", host
port = 12345
s.bind((host, port))
print "Server port: ", port

s.listen(5)
while True:
    c, addr = s.accept()
    print "The client is connecting through port ", addr[1]
    c.send("Thank you for connecting")
    c.close()
