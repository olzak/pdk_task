import socket
import threading
import csv
from datetime import datetime

BUFFER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
LOG_FILE = "server_log.csv"
ACK_MESSAGE = "Great success!"

file_lock = threading.Lock()

def log_message(client_address, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with file_lock:
        with open(LOG_FILE, 'a', newline='', encoding=FORMAT) as csvfile:
            writer = csv.writer(csvfile)
            if message != ' ':
                writer.writerow([timestamp, client_address, message])

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(BUFFER)
            if not data:
                break
            message = data.decode(FORMAT)
            if message != ' ':
                print(f"Received from {addr}: {message}")
                log_message(addr, message)
                conn.sendall(ACK_MESSAGE.encode(FORMAT))
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection closed for {addr}")

def main():
    print("Starting server...")
    with (socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server):
        server.bind(ADDR)
        server.listen()
        print(f"Server listening on {ADDR}")
        while True:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

if __name__ == "__main__":
    main()