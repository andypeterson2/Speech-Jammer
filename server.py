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
                query_id = self.conn.recv(1024).decode()
                if not query_id:
                    logging.info(f"Connection terminated by client {self.addr}")
                    break
                elif query_id == unique_id:
                    self.conn.sendall(b"That's your own ID.")
                else:
                    addr = self.user_id_manager.get_addr(query_id)
                    if addr:
                        ip, port = addr
                        self.conn.sendall(f"The IP is {ip} and the port is {port}".encode())
                    else:
                        self.conn.sendall(b"ID doesn't exist.")
        except:
            logging.error(f"Failed to handle client {unique_id}")
        finally:
            self.conn.close()
            
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
