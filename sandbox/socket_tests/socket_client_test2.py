import socket

s = socket.socket()
host = socket.gethostname()
print "This machine's hostname: ", host
port = 12345
print "Server port to connect to: ", port

s.connect((host, port))
print s.recv(1024)
s.close
