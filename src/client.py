import threading
import socket

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock, mainthread

BUFFER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

class ClientSocket:
    def __init__(self):
        self.sock = None
        self.connected = False

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(ADDR)
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False

    def send_message(self, message):
        try:
            self.sock.sendall(message.encode(FORMAT))
            # Wait for acknowledgment from the server
            data = self.sock.recv(BUFFER)
            return data.decode(FORMAT)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
            return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.connected = False

class ClientGUI(BoxLayout):
    connection_status = ObjectProperty(None)
    console = ObjectProperty(None)
    message_input = ObjectProperty(None)
    status_text = StringProperty("Disconnected")
    client_socket = None
    connection_check_interval = 2

    def __init__(self, **kwargs):
        super(ClientGUI, self).__init__(**kwargs)
        self.client_socket = ClientSocket()
        threading.Thread(target=self.connect_to_server, daemon=True).start()
        Clock.schedule_interval(self.check_connection_status, self.connection_check_interval)

    def on_kv_post(self, base_widget):
        self.connection_status = self.ids.connection_status
        self.console = self.ids.console
        self.message_input = self.ids.message_input

    def connect_to_server(self):
        if self.client_socket.connect():
            self.update_connection_status(True)
            self.append_console("Connected to server.")
        else:
            self.update_connection_status(False)
            self.append_console("Failed to connect to server.")

    def check_connection_status(self, dt):
        if self.client_socket.connected:
            try:
                self.client_socket.sock.send(b' ')
                self.update_connection_status(True)
            except Exception as e:
                self.client_socket.connected = False
                self.update_connection_status(False)
                self.append_console("Connection lost. Server is off.")
        else:
            if self.client_socket.connect():
                self.update_connection_status(True)
                self.append_console("Reconnected to server.")
            else:
                self.update_connection_status(False)

    @mainthread
    def update_connection_status(self, connected):
        if connected:
            self.status_text = "Connected"
            self.connection_status.canvas.before.clear()
            with self.connection_status.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0, 1, 0, 1)  # green
                Rectangle(pos=self.connection_status.pos, size=self.connection_status.size)
        else:
            self.status_text = "Disconnected"
            self.connection_status.canvas.before.clear()
            with self.connection_status.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(1, 0, 0, 1)  # red
                Rectangle(pos=self.connection_status.pos, size=self.connection_status.size)

    @mainthread
    def append_console(self, text):
        self.console.text += text + "\n"

    def send_button_pressed(self):
        message = self.message_input.text.strip()
        if message:
            self.append_console(f"Sending: {message}")
            threading.Thread(target=self.send_message, args=(message,), daemon=True).start()
            self.message_input.text = ""

    def test_button_pressed(self):
        test_message = "Test"
        self.append_console(f"Sending test message: {test_message}")
        threading.Thread(target=self.send_message, args=(test_message,), daemon=True).start()

    def send_message(self, message):
        if not self.client_socket.connected:
            self.append_console("Not connected to server.")
            return
        response = self.client_socket.send_message(message)
        if response:
            self.append_console(f"Received: {response}")
        else:
            self.append_console("No response or error occurred.")

class ClientApp(App):
    def build(self):
        return ClientGUI()

if __name__ == '__main__':
    ClientApp().run()