import socket
import threading
import logging
import hashlib

logging.basicConfig(level=logging.INFO)

class ClientHandler:
    def __init__(self, conn, addr, client_ids):
        self.conn = conn
        self.addr = addr
        self.client_ids = client_ids

    def generate_id(self):
        ip, port = self.addr
        ip = socket.gethostbyname(ip) # Resolving hostname to IP
        unique_str = ip + str(port)
        return hashlib.sha1(unique_str.encode()).hexdigest()[:10]

    def handle(self):
        try:
            unique_id = self.generate_id()
            self.client_ids[unique_id] = self.addr
            logging.info(f"Assigned ID {unique_id} to {self.addr}")
            self.conn.sendall(f"Your ID is {unique_id}".encode())
        except:
            logging.error("Failed to handle client connection")
        finally:
            self.conn.close()

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_ids = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        logging.info(f"Server is running on {host} and port {port}")

    def start(self):
        while True:
            conn, addr = self.server_socket.accept()
            client_handler = ClientHandler(conn, addr, self.client_ids)
            thread = threading.Thread(target=client_handler.handle)
            thread.start()

if __name__ == "__main__":
    server = Server('localhost', 60535)
    server.start()
