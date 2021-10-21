import logging
import socket
import ssl
import sys

from PyQt6 import QtWidgets

from client import Status, Client

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations("./selfsigned.crt")


# async def hello():
#     uri = "wss://localhost:8080"
#     async with websockets.connect(uri, ssl=ssl_context) as websocket:
#         name = input("What's your name? ")
#
#         await websocket.send(name)
#         print(f">>> {name}")
#
#         greeting = await websocket.recv()
#         print(f"<<< {greeting}")

# asyncio.run(hello())

# def mysend(msg, sock):
#     totalsent = 0
#     while totalsent < MSGLEN:
#         sent = sock.send(msg[totalsent:])
#         if sent == 0:
#             raise RuntimeError("socket connection broken")
#         totalsent = totalsent + sent

def main():
    hostname = 'localhost'
    with socket.create_connection((hostname, 8080)) as sock:
        with ssl_context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(ssock.version())
            print(ssock.send(b'hello'))
            # ssock.shutdown(socket.SHUT_RDWR)


class ClientApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO, handlers=[
            logging.StreamHandler(),
            logging.FileHandler('client.log', mode='w')
        ])
        self.logger = logging.getLogger('client')
        self.client: Client = Client(self.set_buttons_status)

        self.CERT_FILE = "./selfsigned.crt"

        self.button_connect = QtWidgets.QPushButton("Подключится")
        self.button_disconnect = QtWidgets.QPushButton("Отключиться")
        self.button_send_msg = QtWidgets.QPushButton("Отправить")
        self.text_field = QtWidgets.QTextEdit()
        self.label = QtWidgets.QLabel()

        self.layout = QtWidgets.QVBoxLayout(self)

        self.layout.addWidget(self.button_connect)
        self.layout.addWidget(self.button_disconnect)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text_field)
        self.layout.addWidget(self.button_send_msg)

        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_disconnect.clicked.connect(self.close_connection)
        self.button_send_msg.clicked.connect(self.send_msg)

        self.set_buttons_status(Status.DISCONNECTED)

    def connect_to_server(self):
        self.client.connect(self.CERT_FILE)

    def close_connection(self):
        self.disconnect()

    def send_msg(self):
        self.client.send_msg(self.text_field.toPlainText())

    def set_buttons_status(self, status: Status):
        # TODO: set_buttons_status
        if status == Status.CONNECTED:
            self.button_connect.setDisabled(True)
            self.button_disconnect.setDisabled(False)
            self.button_send_msg.setDisabled(False)
            self.text_field.setDisabled(False)
        elif status == Status.DISCONNECTED:
            self.button_connect.setDisabled(False)
            self.button_disconnect.setDisabled(True)
            self.button_send_msg.setDisabled(True)
            self.text_field.setDisabled(False)
        elif status == Status.CONNECTING:
            self.button_connect.setDisabled(True)
            self.button_disconnect.setDisabled(True)
            self.button_send_msg.setDisabled(True)
            self.text_field.setDisabled(False)


def start_client_app():
    app = QtWidgets.QApplication([])

    widget = ClientApp()
    widget.setWindowTitle("Client")
    widget.resize(800, 600)
    widget.move(830, 50)
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    # main()
    start_client_app()
