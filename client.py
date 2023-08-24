import socket
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.host, self.port))
                unique_id = client_socket.recv(1024).decode().split()[-1]
                logging.info(f"Received ID {unique_id} from server")
                while True:
                    print("1) Check if an ID exists\n2) Ping server\n")
                    choice = input("Select a command: ")
                    client_socket.sendall(choice.encode())
                    if choice == '1':
                        self.query_id(client_socket)
                    elif choice == '2':
                        self.ping_server(client_socket)
                    else:
                        print("Invalid command. Try again.")
            except Exception as e:
                logging.error(f"Exception while communicating with server: {str(e)}")
            finally:
                logging.info("Connection closed")

    def query_id(self, client_socket):
        query_id = input("Enter a user ID to query: ")
        client_socket.sendall(query_id.encode())
        response = client_socket.recv(1024).decode()
        logging.info(f"Server response: {response}")

    def ping_server(self, client_socket):
        response = client_socket.recv(1024).decode()
        logging.info(f"Server response: {response}")


if __name__ == "__main__":
  HOST = '127.0.0.1'
  PORT = 65430

  client = Client(HOST, PORT)
  client.connect()
