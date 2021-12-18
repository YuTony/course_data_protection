import logging
import socket
import ssl
from enum import Enum
from typing import Callable
import threading
from OpenSSL import crypto


class Status(Enum):
    CONNECTED = 0
    DISCONNECTED = 1
    CONNECTING = 2


class Client:
    def __init__(self, change_status: Callable[[Status], None]):
        self.change_status = change_status
        self.logger = logging.getLogger('client')
        self.hostname = 'localhost'

        self.is_auth = False
        self.CLIENT_CERT_FILE = None
        self.CLIENT_KEY_FILE = None

        self.port = 8080
        self.sock: socket = None
        self.ssock: ssl.SSLSocket | None = None
        self.thread: threading.Thread | None = None
        self.is_msg_loop = False

    def connect(self, msg_handler: Callable[[str], None], hostname: str, port: int, crt: str, len_key: int, ccrt=None, cprivat_key=None):
        self.is_auth = ccrt is not None and cprivat_key is not None
        self.hostname = hostname
        self.port = port
        self.CLIENT_CERT_FILE = ccrt
        self.CLIENT_KEY_FILE = cprivat_key
        self.thread = threading.Thread(target=self._connect, args=(crt, msg_handler, len_key))
        self.thread.start()

    def _connect(self, crt: str, msg_handler: Callable[[str], None], len_key: int):
        try:
            self.change_status(Status.CONNECTING)
            # cert = ssl.get_server_certificate((self.hostname, self.port))
            # cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
            # print(cert.get_pubkey().bits())
            self.sock = socket.create_connection((self.hostname, self.port))
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=crt)
            self.logger.info(f"create default context. cert: {crt}")
            # self.ssl_context.load_verify_locations(crt)
            if self.is_auth:
                self.ssl_context.load_cert_chain(self.CLIENT_CERT_FILE, self.CLIENT_KEY_FILE)
                self.logger.info(f"load cert chain. cert: {self.CLIENT_CERT_FILE}, private key: {self.CLIENT_KEY_FILE}")
            self.ssock = self.ssl_context.wrap_socket(self.sock, server_hostname=self.hostname, server_side=False)

            if len_key != 0:
                der = self.ssock.getpeercert(True)
                certificate = crypto.load_certificate(crypto.FILETYPE_ASN1, der)
                public_key = certificate.get_pubkey()
                key_length = public_key.bits()
                if key_length < len_key:
                    self.logger.error(f"Key length < {len_key}")
                    self.disconnect()

            self.change_status(Status.CONNECTED)
            self.msg_loop(msg_handler)
        except ConnectionError as err:
            self.logger.error(err.strerror)
            self.change_status(Status.DISCONNECTED)
        except OSError as err:
            self.logger.error(err.strerror)
            self.change_status(Status.DISCONNECTED)

    def msg_loop(self, msg_handler: Callable[[str], None]):
        self.is_msg_loop = True
        self.logger.info('msg loop start')
        while self.is_msg_loop:
            try:
                data = self.ssock.recv(1024)
                msg = data.decode("utf-8")
                self.logger.info(f'Message received: {msg}')
                msg_handler(msg)
                if not data:
                    # print("data = ''")
                    self.disconnect()
                    break
            except socket.timeout:
                self.logger.error('socket.timeout')
                continue
        self.logger.info('msg loop stop')

    def disconnect(self):
        self.is_msg_loop = False
        if self.ssock:
            self.ssock.close()
        self.change_status(Status.DISCONNECTED)

    def send_msg(self, msg: str):
        try:
            self.ssock.send(bytes(msg, "utf-8"))
        except OSError as err:
            self.disconnect()
            self.logger.error(err.strerror)

    def __del__(self):
        self.is_msg_loop = False
        if self.ssock:
            self.ssock.close()
