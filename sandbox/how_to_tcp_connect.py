import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname('chromebox02')
port = 10000
s.connect((host, port))

s.send("Hello!")

s.close()
