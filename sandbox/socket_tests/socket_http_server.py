import socket

sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "www.google.com"
port = int(80)
sck.connect((host, port))
data = "GET / HTTP\1.1\r\n\r\n"

sck.send(data)

data_buffer = sck.recv(1024)
print "Data buffer: ", data_buffer
