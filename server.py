import logging
import socket
import ssl
import threading
from enum import Enum
from typing import Callable


class Status(Enum):
    STOPPED = 1
    WAITING = 2
    CONNECTED = 3


class Server:
    def __init__(self, change_status: Callable[[Status], None]):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        self.change_status = change_status
        self.logger = logging.getLogger('server')

        self.sock: socket = None
        self.ssock: ssl.SSLSocket | None = None

        self.conn: ssl.SSLSocket | None = None
        self.addr = None

        self.msg_loop_thread: threading.Thread | None = None
        self.is_msg_loop = False

    def start(self, host: str, port: int, crt: str, privat_key: str, msg_handler: Callable[[str], None]):
        self.context.load_cert_chain(crt, privat_key)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.ssock = self.context.wrap_socket(self.sock, server_side=True)
        # self.ssock.setblocking(False)
        self.msg_loop_thread = threading.Thread(target=self.wait_connect, args=(msg_handler, ))
        self.msg_loop_thread.start()

    def wait(self, set_text: Callable[[str], None]):
        self.context.load_cert_chain('./selfsigned.crt', './private.key')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind(('localhost', 8080))
            sock.listen(5)
            with self.context.wrap_socket(sock, server_side=True) as ssock:
                conn, addr = ssock.accept()
                # print(conn.read(64).decode('utf-8'))
                set_text(conn.read(64).decode('utf-8'))

    def wait_connect(self, msg_handler: Callable[[str], None]):
        try:
            self.change_status(Status.WAITING)
            self.conn, self.addr = self.ssock.accept()
            self.change_status(Status.CONNECTED)
            self.logger.info(f'Connected {self.addr}')
            self.msg_loop(msg_handler)
        except OSError:
            self.logger.info('Socket.accept is forced to terminate')

    def send_msg(self, msg: str):
        if self.conn:
            self.conn.send(bytes(msg, "utf-8"))

    def msg_loop(self, msg_handler: Callable[[str], None]):
        self.is_msg_loop = True
        self.logger.info('msg loop start')
        while self.is_msg_loop:
            data = self.conn.recv(1024)
            print(data)
            if data != b'':
                msg = data.decode("utf-8")
                self.logger.info(f'Message received from {self.addr}: {msg}')
                msg_handler(msg)
        self.logger.info('msg loop stop')

    def stop(self):
        if self.ssock:
            self.is_msg_loop = False
            if self.conn:
                self.conn.close()
                self.conn = None
            self.ssock.close()
            self.ssock = None
            # if self.is_msg_loop:
            #     self.is_msg_loop = False
            #     # self.msg_loop_thread.join()
            #     self.ssock.close()
            # else:
            #     self.ssock.close()
                # self.msg_loop_thread.join()
            # self.is_msg_loop = False
            # self.ssock.close()
            # if self.msg_loop_thread:
            #     self.msg_loop_thread.join()
        self.change_status(Status.STOPPED)
