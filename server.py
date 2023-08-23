import socket
import threading
import logging

logging.basicConfig(level=logging.INFO)

class ClientHandler:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def handle(self):
        logging.info(f"Connection from {self.addr} at port {self.addr[1]}")
        try:
            self.conn.sendall(b'hello client')
        except:
            logging.error("Failed to send data to client")
        finally:
            self.conn.close()

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        logging.info(f"Server is running on {host} and port {port}")

    def start(self):
        while True:
            conn, addr = self.server_socket.accept()
            client_handler = ClientHandler(conn, addr)
            thread = threading.Thread(target=client_handler.handle)
            thread.start()

if __name__ == "__main__":
    server = Server('localhost', 23942)
    server.start()
