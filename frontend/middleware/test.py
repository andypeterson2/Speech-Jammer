import time
import socket

host = "0.0.0.0"
port = 5000

print('Addr: ' + str(socket.gethostbyname(socket.gethostname())))

## peer_sock = socket.socket()
print('1')
client_sock = socket.socket()
print('2')
client_sock.bind((host,port))
print('3')
client_sock.listen(1)
print('4')

# conn, addr = client_sock.accept()
print('received connection request')

# while True:
    # data = conn.recv(1024)
    ## if data.decode() == 'exit': break
    ## peer_sock.send(data)
    # print('hehe')

for i in range(10):
    print(i)
    time.sleep(1)

# conn.close()