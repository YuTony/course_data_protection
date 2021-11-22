import logging
import sys

from PyQt6 import QtWidgets, QtGui

from client import Status, Client


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

        self.label.setStyleSheet("border: 1px solid black")
        # self.label

        self.ip_layout = QtWidgets.QHBoxLayout()
        self.ip_layout.addWidget(QtWidgets.QLabel("Адрес:"))
        self.ip_field = QtWidgets.QLineEdit()
        self.ip_layout.addWidget(self.ip_field)

        self.port_layout = QtWidgets.QHBoxLayout()
        self.port_layout.addWidget(QtWidgets.QLabel("Port:"))
        self.port_field = QtWidgets.QLineEdit()
        self.port_layout.addWidget(self.port_field)

        self.layout = QtWidgets.QVBoxLayout(self)

        # self.layout.addLayout(self.ip_layout)
        # self.layout.addLayout(self.port_layout)
        self.layout.addWidget(self.button_connect)
        self.layout.addWidget(self.button_disconnect)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Получено сообщение:"))
        self.layout.addWidget(self.label)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Новое сообщение:"))
        self.layout.addWidget(self.text_field)
        self.layout.addWidget(self.button_send_msg)

        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_disconnect.clicked.connect(self.close_connection)
        self.button_send_msg.clicked.connect(self.send_msg)

        self.set_buttons_status(Status.DISCONNECTED)

    def connect_to_server(self):
        self.client.connect(self.CERT_FILE, self.label.setText)

    def close_connection(self):
        self.client.disconnect()

    def send_msg(self):
        self.client.send_msg(self.text_field.toPlainText())

    def set_buttons_status(self, status: Status):
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

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.client.disconnect()
        a0.accept()


def start_client_app():
    app = QtWidgets.QApplication([])

    widget = ClientApp()
    widget.setWindowTitle("Client")
    widget.resize(400, 300)
    widget.move(430, 50)
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    start_client_app()
