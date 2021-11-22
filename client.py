import logging
import socket
import ssl
from enum import Enum
from typing import Callable
import threading


class Status(Enum):
    CONNECTED = 0
    DISCONNECTED = 1
    CONNECTING = 2


class Client:
    def __init__(self, change_status: Callable[[Status], None]):
        self.change_status = change_status
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.logger = logging.getLogger('client')
        self.hostname = 'localhost'

        self.port = 8080
        self.sock: socket = None
        self.ssock: ssl.SSLSocket | None = None
        self.thread: threading.Thread | None = None
        self.is_msg_loop = False

    def connect(self, crt: str, msg_handler: Callable[[str], None]):
        self.thread = threading.Thread(target=self._connect, args=(crt, msg_handler))
        self.thread.start()

    def _connect(self, crt: str, msg_handler: Callable[[str], None]):
        try:
            self.change_status(Status.CONNECTING)
            self.sock = socket.create_connection((self.hostname, 8080))
            self.ssl_context.load_verify_locations(crt)
            self.ssock = self.ssl_context.wrap_socket(self.sock, server_hostname=self.hostname)
            self.change_status(Status.CONNECTED)
            self.msg_loop(msg_handler)
        except ConnectionError as err:
            print(err)
            self.change_status(Status.DISCONNECTED)
        except OSError as err:
            print(err)
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
                    print("data = ''")
                    self.disconnect()
                    break
            except socket.timeout:
                print('socket.timeout')
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
            print(err)
