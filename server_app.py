import logging
import sys

from OpenSSL import crypto
from PyQt6 import QtWidgets, QtGui

from server import Status, Server


# class Server:
#     def __init__(self):
#         self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#         self.status = Status.WAIT
#
#     async def start(self):
#         self.context.load_cert_chain('./selfsigned.crt', './private.key')
#         async with websockets.serve(self.hello, "localhost", 8080, ssl=self.context) as serv:
#             print("init...")
#             self.serv = serv
#             await asyncio.Future()
#         print("Started")
#
#     async def hello(self, websocket, path):
#         name = await websocket.recv()
#         if name == 'close':
#             self.serv.close()
#         print(f"<<< {name}")
#
#         greeting = f"Hello {name}!"
#
#         await websocket.send(greeting)
#         print(f">>> {greeting}")


class ServerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO, handlers=[
                                logging.StreamHandler(),
                                logging.FileHandler('server.log', mode='w')
                            ])
        self.logger = logging.getLogger('server')
        self.server = Server(self.set_buttons_status, lambda msg: self.text_label.setText(msg))
        self.thread = None

        self.CERT_FILE = "./selfsigned.crt"
        self.KEY_FILE = "./private.key"

        self.button_cert = QtWidgets.QPushButton("Создать сертификат")
        self.button_run = QtWidgets.QPushButton("Запустить сервер")
        self.button_stop = QtWidgets.QPushButton("Отстановить сервер")
        self.text_field = QtWidgets.QTextEdit()
        self.text_label = QtWidgets.QLabel()
        self.button_send_msg = QtWidgets.QPushButton("Отправить")

        self.text_label.setStyleSheet("border: 1px solid black")

        self.ip_layout = QtWidgets.QHBoxLayout()
        self.ip_layout.addWidget(QtWidgets.QLabel("Адрес:"))
        self.ip_field = QtWidgets.QLineEdit()
        self.ip_layout.addWidget(self.ip_field)

        self.port_layout = QtWidgets.QHBoxLayout()
        self.port_layout.addWidget(QtWidgets.QLabel("Port:"))
        self.port_field = QtWidgets.QLineEdit()
        self.port_layout.addWidget(self.port_field)
        # TODO: Добавить обработку полей

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button_cert)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.ip_layout)
        self.layout.addLayout(self.port_layout)
        self.layout.addWidget(self.button_run)
        self.layout.addWidget(self.button_stop)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Получено сообщение:"))
        self.layout.addWidget(self.text_label)
        self.layout.addSpacing(10)
        self.layout.addWidget(QtWidgets.QLabel("Новое сообщение:"))
        self.layout.addWidget(self.text_field)
        self.layout.addWidget(self.button_send_msg)
        self.button_cert.clicked.connect(self.create_cert)
        self.button_run.clicked.connect(self.run_server)
        self.button_stop.clicked.connect(self.stop_server)
        self.button_send_msg.clicked.connect(self.send_msg)

        self.set_buttons_status(Status.STOPPED)

    def create_cert(self):
        email_address = "emailAddress"
        common_name = "localhost"
        country_name = "NT"
        locality_name = "localityName"
        state_or_province_name = "stateOrProvinceName"
        organization_name = "organizationName"
        organization_unit_name = "organizationUnitName"
        serial_number = 0
        validity_start_in_seconds = 0
        validity_end_in_seconds = 10 * 365 * 24 * 60 * 60
        # can look at generated file using openssl:
        # openssl x509 -inform pem -in selfsigned.crt -noout -text
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 4096)
        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = country_name
        cert.get_subject().ST = state_or_province_name
        cert.get_subject().L = locality_name
        cert.get_subject().O = organization_name
        cert.get_subject().OU = organization_unit_name
        cert.get_subject().CN = common_name
        cert.get_subject().emailAddress = email_address
        cert.set_serial_number(serial_number)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(validity_end_in_seconds)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha512')
        with open(self.CERT_FILE, "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
        with open(self.KEY_FILE, "wt") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))

    def run_server(self):
        self.server.start('localhost', 8080, self.CERT_FILE, self.KEY_FILE,)

    def stop_server(self):
        self.server.stop()

    def set_buttons_status(self, status: Status):
        if status == Status.STOPPED:
            self.button_cert.setDisabled(False)
            self.button_run.setDisabled(False)
            self.button_stop.setDisabled(True)
            self.button_send_msg.setDisabled(True)
            self.logger.info('Сервер остановлен')
        elif status == Status.WAITING:
            self.button_cert.setDisabled(True)
            self.button_run.setDisabled(True)
            self.button_stop.setDisabled(False)
            self.button_send_msg.setDisabled(True)
            self.logger.info('Ожидание подключения')
        elif status == Status.CONNECTED:
            self.button_cert.setDisabled(True)
            self.button_run.setDisabled(True)
            self.button_stop.setDisabled(False)
            self.button_send_msg.setDisabled(False)
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
