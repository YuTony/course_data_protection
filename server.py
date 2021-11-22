import logging
import socket
import ssl
import threading
from enum import Enum
from typing import Callable
import os


class Status(Enum):
    STOPPED = 1
    WAITING = 2
    CONNECTED = 3


class Server:
    def __init__(self, change_status: Callable[[Status], None], msg_handler: Callable[[str], None]):
        # self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)

        self.change_status = change_status
        self.logger = logging.getLogger('server')

        self.sock: socket = None
        self.ssock: ssl.SSLSocket | None = None

        self.conn: ssl.SSLSocket | None = None
        self.addr = None

        self.wait_thread: threading.Thread | None = None
        self.msg_loop_thread: threading.Thread | None = None
        self.is_msg_loop = False

        self.msg_handler: Callable[[str], None] = msg_handler

    def start(self, host: str, port: int, crt: str, privat_key: str):
        self.context.load_cert_chain(crt, privat_key)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.ssock = self.context.wrap_socket(self.sock, server_side=True)
        self.wait_connect()

    def wait_connect(self):
        self.wait_thread = threading.Thread(target=self._wait_connect)
        self.wait_thread.start()

    def _wait_connect(self):
        try:
            self.change_status(Status.WAITING)
            self.conn, self.addr = self.ssock.accept()
            self.change_status(Status.CONNECTED)
            self.logger.info(f'Connected {self.addr}')
            self.msg_loop()
        except OSError:
            self.logger.info('Socket.accept is forced to terminate')

    def send_msg(self, msg: str):
        if self.conn:
            try:
                a = self.conn.send(bytes(msg, "utf-8"))
                print(a)
            except OSError as err:
                self.conn.close()
                self.wait_connect()
                print(err)

    def msg_loop(self):
        self.msg_loop_thread = threading.Thread(target=self._msg_loop)
        self.msg_loop_thread.start()

    def _msg_loop(self):
        self.is_msg_loop = True
        self.logger.info('msg loop start')
        while self.is_msg_loop:
            data = self.conn.recv(1024)
            msg = data.decode("utf-8")
            self.logger.info(f'Message received from {self.addr}: {msg}')
            self.msg_handler(msg)
            if not data:
                print("data = ''")
                self.stop()
                break
        self.logger.info('msg loop stop')

    def stop(self):
        if self.ssock:
            self.is_msg_loop = False
            if self.conn:
                self.conn.close()
                self.conn = None
            self.ssock.close()
            self.ssock = None
        self.change_status(Status.STOPPED)
