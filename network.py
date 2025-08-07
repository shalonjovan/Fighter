# network.py
import socket
import threading
import json

class NetworkHandler:
    def __init__(self, is_host, ip='127.0.0.1', port=5555):
        self.is_host = is_host
        self.port = port
        self.ip = ip
        self.conn = None
        self.listener_thread = None
        self.received_data = {}

        if self.is_host:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((ip, port))
            self.sock.listen(1)
            print(f"[HOST] Waiting for connection on {ip}:{port}")
            self.conn, _ = self.sock.accept()
            print("[HOST] Player connected.")
        else:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[CLIENT] Connecting to {ip}:{port}...")
            self.conn.connect((ip, port))
            print("[CLIENT] Connected to host.")

        self.start_listener()

    def start_listener(self):
        self.listener_thread = threading.Thread(target=self.listen, daemon=True)
        self.listener_thread.start()

    def listen(self):
        while True:
            try:
                data = self.conn.recv(1024).decode()
                if data:
                    self.received_data = json.loads(data)
            except:
                break

    def send(self, data_dict):
        try:
            message = json.dumps(data_dict).encode()
            self.conn.sendall(message)
        except:
            pass

    def get_latest_data(self):
        return self.received_data
