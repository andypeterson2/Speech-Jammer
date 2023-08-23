import socket
import logging

logging.basicConfig(level=logging.INFO)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            data = client_socket.recv(1024)
            logging.info(f"Received: {data.decode()}")
        except:
            logging.error("Failed to connect or receive data from server")
        finally:
            client_socket.close()

if __name__ == "__main__":
    client = Client('localhost', 23942)
    client.connect()
