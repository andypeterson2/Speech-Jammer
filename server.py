import socket
import threading
import logging
import hashlib

# Setup Logging
logging.basicConfig(level=logging.INFO)

class UserIDManager:
    def __init__(self):
        self.client_ids = {}

    def generate_id(self, addr):
        addr_str = f"{addr[0]}:{addr[1]}"
        return hashlib.sha1(addr_str.encode()).hexdigest()[:5]

    def add_id(self, unique_id, addr):
        self.client_ids[unique_id] = addr

    def get_addr(self, query_id):
        return self.client_ids.get(query_id, None)

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, user_id_manager):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.user_id_manager = user_id_manager

    def run(self):
        try:
            self.handle()
        except Exception as e:
            logging.error(f"Exception while handling client {self.addr}: {str(e)}")
        finally:
            self.conn.close()
            logging.info(f"Connection closed with {self.addr}")

    def handle(self):
        try:
            unique_id = self.user_id_manager.generate_id(self.addr)
            self.user_id_manager.add_id(unique_id, self.addr)
            logging.info(f"Assigned ID {unique_id} to {self.addr}")
            self.conn.sendall(f"Your ID is {unique_id}".encode())
            while True:
                command = self.conn.recv(1024).decode()
                if not command:
                    logging.info(f"Connection terminated by client {self.addr}")
                    break
                
                if command == '1':
                    self.check_id_existence()
                elif command == '2':
                    self.ping()
        except:
            logging.error(f"Failed to handle client {unique_id}")
        finally:
            self.conn.close()
            
    def check_id_existence(self):
        query_id = self.conn.recv(1024).decode()
        logging.info(f"Received ID check request from IP: {self.addr[0]}, Port: {self.addr[1]}")
                
        if query_id in self.user_id_manager.client_ids:
            client_addr = self.user_id_manager.get_addr(query_id)
            response = f"ID {query_id} exists with IP: {client_addr[0]} and Port: {client_addr[1]}"            
        else:
            response = "ID does not exist."
        self.conn.sendall(response.encode())

    def ping(self):
        logging.info(f"Ping received from client {self.addr}")        
        self.conn.sendall(b"Pong")
            
if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 65430

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        logging.info(f"Server listening on {HOST}:{PORT}")
        user_id_manager = UserIDManager()
        while True:
            conn, addr = server_socket.accept()
            client_handler = ClientHandler(conn, addr, user_id_manager)
            client_handler.start()
