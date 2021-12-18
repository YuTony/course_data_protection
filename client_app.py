import logging
import sys

from PyQt6 import QtWidgets, QtGui

from client import Status, Client
from select_pair import SelectPair
from select_clients import SelectClients


class ClientApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.CLIENT_CERT_FILE = None
        self.CLIENT_KEY_FILE = None

        logging.basicConfig(level=logging.INFO, handlers=[
            logging.StreamHandler()
        ])
        self.logger = logging.getLogger('client')
        # self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(logging.FileHandler('client.log', mode='w', encoding='utf-8'))
        self.logger.setLevel(logging.INFO)

        self.client: Client = Client(self.set_buttons_status)

        self.CERT_FILE = "./trusted_certificates/trusted.crt"

        self.button_connect = QtWidgets.QPushButton("Подключится")
        self.button_disconnect = QtWidgets.QPushButton("Отключиться")
        self.button_send_msg = QtWidgets.QPushButton("Отправить")
        self.text_field = QtWidgets.QTextEdit()
        self.label = QtWidgets.QLabel()

        self.label.setStyleSheet("border: 1px solid black")

        self.button_valid_certs = QtWidgets.QPushButton("Выбрать доверенные сертификаты")

        self.button_cert = QtWidgets.QPushButton("Выбрать клиентский сертификат и ключ")

        self.is_auth = QtWidgets.QHBoxLayout()
        self.is_auth_checkbox = QtWidgets.QCheckBox()
        self.is_auth.addWidget(self.is_auth_checkbox)
        self.is_auth.addWidget(QtWidgets.QLabel("Включить авторизацию"))
        self.is_auth.addStretch()

        self.layout1 = QtWidgets.QHBoxLayout()
        self.layout1.addWidget(QtWidgets.QLabel("Минимальная длина ключа: "))
        self.len_key_field = QtWidgets.QLineEdit()
        self.layout1.addWidget(self.len_key_field)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button_valid_certs)
        self.layout.addWidget(self.button_cert)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.layout1)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.is_auth)
        self.layout.addWidget(self.button_connect)
        self.layout.addWidget(self.button_disconnect)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Получено сообщение:"))
        self.layout.addWidget(self.label)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Новое сообщение:"))
        self.layout.addWidget(self.text_field)
        self.layout.addWidget(self.button_send_msg)

        self.button_valid_certs.clicked.connect(self.get_valid_certs)
        self.button_cert.clicked.connect(self.get_cert)
        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_disconnect.clicked.connect(self.close_connection)
        self.button_send_msg.clicked.connect(self.send_msg)

        self.set_buttons_status(Status.DISCONNECTED)

    def connect_to_server(self):
        if self.len_key_field.text() == "":
            key_len = 0
        else:
            try:
                key_len = int(self.len_key_field.text())
            except ValueError:
                self.logger.error(f"Parse error: {self.len_key_field.text()}")
                key_len = 0
        if not self.is_auth_checkbox.isChecked():
            self.client.connect(self.label.setText, "localhost", 8080, self.CERT_FILE, key_len)
        else:
            self.client.connect(self.label.setText, "localhost", 8080, self.CERT_FILE, key_len,
                                self.CLIENT_CERT_FILE, self.CLIENT_KEY_FILE)

    def close_connection(self):
        self.client.disconnect()

    def send_msg(self):
        self.client.send_msg(self.text_field.toPlainText())

    def get_valid_certs(self):
        SelectClients.select_certs("./server_cert/", "./trusted_certificates/")

    def get_cert(self):
        cert_name, key_name = SelectPair.get_certs("./client_cert/")
        if cert_name and key_name:
            self.CLIENT_CERT_FILE = "./client_cert/" + cert_name
            self.CLIENT_KEY_FILE = "./client_cert/" + key_name
            self.set_buttons_status(Status.DISCONNECTED)

    def set_buttons_status(self, status: Status):
        if status == Status.CONNECTED:
            self.button_valid_certs.setDisabled(True)
            self.button_cert.setDisabled(True)
            self.button_connect.setDisabled(True)
            self.button_disconnect.setDisabled(False)
            self.button_send_msg.setDisabled(False)
            self.text_field.setDisabled(False)
        elif status == Status.DISCONNECTED:
            self.button_valid_certs.setDisabled(False)
            self.button_cert.setDisabled(False)
            self.button_connect.setDisabled(False)
            self.button_disconnect.setDisabled(True)
            self.button_send_msg.setDisabled(True)
            self.text_field.setDisabled(True)
        elif status == Status.CONNECTING:
            self.button_valid_certs.setDisabled(True)
            self.button_cert.setDisabled(True)
            self.button_connect.setDisabled(True)
            self.button_disconnect.setDisabled(True)
            self.button_send_msg.setDisabled(True)
            self.text_field.setDisabled(True)

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
