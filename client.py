import socket
import logging
import time

logging.basicConfig(level=logging.INFO)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            unique_id = client_socket.recv(1024).decode().split()[-1]
            logging.info(f'Received ID:{unique_id}')
            while True:
                time.sleep(30)
                client_socket.sendall(b'ping')
                logging.info(f"Sent 'ping' to server from ID {unique_id}, IP {self.host}, port {self.port} at {time.ctime()}")
                data = client_socket.recv(1024)
        except:
            logging.error("Failed to connect or communicate with the server")
        finally:
            client_socket.close()

if __name__ == "__main__":
    client = Client('localhost', 60535)
    client.connect()
