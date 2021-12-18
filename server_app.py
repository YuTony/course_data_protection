import logging
import sys

from PyQt6 import QtWidgets, QtGui

from server import Status, Server
from select_pair import SelectPair
from select_clients import SelectClients


class ServerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO, handlers=[
            logging.StreamHandler()
        ])
        self.logger = logging.getLogger('server')
        # self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(logging.FileHandler('server.log', mode='w', encoding='utf-8'))
        self.logger.setLevel(logging.INFO)
        self.server = Server(self.set_buttons_status, lambda msg: self.text_label.setText(msg))
        self.thread = None

        self.CERT_FILE = None
        self.KEY_FILE = None

        self.button_cert = QtWidgets.QPushButton("Выбрать сертификат и ключ")
        self.button_run = QtWidgets.QPushButton("Запустить сервер")
        self.button_stop = QtWidgets.QPushButton("Остановить сервер")
        self.text_field = QtWidgets.QTextEdit()
        self.text_label = QtWidgets.QLabel()
        self.button_send_msg = QtWidgets.QPushButton("Отправить")

        self.text_label.setStyleSheet("border: 1px solid black")

        self.is_auth_layout = QtWidgets.QHBoxLayout()
        self.is_auth_checkbox = QtWidgets.QCheckBox()
        self.is_auth_layout.addWidget(self.is_auth_checkbox)
        self.is_auth_layout.addWidget(QtWidgets.QLabel("Включить авторизацию"))
        self.is_auth_layout.addStretch()

        self.select_client_btn = QtWidgets.QPushButton("Выбрать сертификаты клиентов")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button_cert)
        self.layout.addWidget(self.select_client_btn)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.is_auth_layout)
        self.layout.addWidget(self.button_run)
        self.layout.addWidget(self.button_stop)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Получено сообщение:"))
        self.layout.addWidget(self.text_label)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Новое сообщение:"))
        self.layout.addWidget(self.text_field)
        self.layout.addWidget(self.button_send_msg)
        self.button_cert.clicked.connect(self.get_cert)
        self.select_client_btn.clicked.connect(self.select_clients)
        self.button_run.clicked.connect(self.run_server)
        self.button_stop.clicked.connect(self.stop_server)
        self.button_send_msg.clicked.connect(self.send_msg)

        self.set_buttons_status(Status.NOT_SELECTED)

    def get_cert(self):
        cert_name, key_name = SelectPair.get_certs("./server_cert/")
        if cert_name and key_name:
            self.CERT_FILE = "./server_cert/" + cert_name
            self.KEY_FILE = "./server_cert/" + key_name
            self.set_buttons_status(Status.STOPPED)

    def select_clients(self):
        SelectClients.select_certs("./client_cert/", "./authorized_clients/")

    def run_server(self):
        self.server.start('localhost', 8080, self.CERT_FILE, self.KEY_FILE, self.is_auth_checkbox.isChecked())

    def stop_server(self):
        self.server.stop()

    def set_buttons_status(self, status: Status):
        if status == Status.STOPPED:
            self.select_client_btn.setDisabled(False)
            self.is_auth_checkbox.setDisabled(False)
            self.button_cert.setDisabled(False)
            self.button_run.setDisabled(False)
            self.button_stop.setDisabled(True)
            self.button_send_msg.setDisabled(True)
            self.text_field.setDisabled(True)
            self.logger.info('Сервер остановлен')
        elif status == Status.WAITING:
            self.select_client_btn.setDisabled(True)
            self.is_auth_checkbox.setDisabled(True)
            self.button_cert.setDisabled(True)
            self.button_run.setDisabled(True)
            self.button_stop.setDisabled(False)
            self.button_send_msg.setDisabled(True)
            self.text_field.setDisabled(True)
        elif status == Status.CONNECTED:
            self.select_client_btn.setDisabled(True)
            self.is_auth_checkbox.setDisabled(True)
            self.button_cert.setDisabled(True)
            self.button_run.setDisabled(True)
            self.button_stop.setDisabled(False)
            self.button_send_msg.setDisabled(False)
            self.text_field.setDisabled(False)
            self.logger.info('Клиент подключен')
        elif status == Status.NOT_SELECTED:
            self.select_client_btn.setDisabled(True)
            self.is_auth_checkbox.setDisabled(True)
            self.button_cert.setDisabled(False)
            self.button_run.setDisabled(True)
            self.button_stop.setDisabled(True)
            self.button_send_msg.setDisabled(True)
            self.text_field.setDisabled(True)
        else:
            pass

    def send_msg(self):
        self.server.send_msg(self.text_field.toPlainText())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.logger.info('Close')
        self.server.stop()
        a0.accept()


def start_server_app():
    app = QtWidgets.QApplication([])

    widget = ServerApp()
    widget.setWindowTitle("Server")
    widget.resize(400, 300)
    widget.move(10, 50)
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_server_app()
