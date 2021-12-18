from time import sleep

from client import Client, Status as clientStatus
from server import Server, Status as serverStatus

msg_s: str | None
msg_c: str | None
status_s: serverStatus | None
status_c: clientStatus | None


def status_handler1(s: serverStatus):
    global status_s
    status_s = s


def status_handler2(s: clientStatus):
    global status_c
    status_c = s


def msg_handler1(m: str):
    global msg_s
    msg_s = m


def msg_handler2(m: str):
    global msg_c
    msg_c = m


def check_connection(server, client):
    sleep(5)

    assert status_s == serverStatus.CONNECTED
    assert status_c == clientStatus.CONNECTED

    client.send_msg("Hello")
    sleep(3)
    assert msg_s == "Hello"

    server.send_msg("Hello")
    sleep(3)
    assert msg_c == "Hello"

    client.disconnect()
    server.stop()

    sleep(3)

    assert status_s == serverStatus.STOPPED
    assert status_c == clientStatus.DISCONNECTED


def check_failure_connection(server, client):
    assert status_s == serverStatus.WAITING
    assert status_c == clientStatus.CONNECTING

    sleep(5)

    assert status_s == serverStatus.WAITING
    assert status_c == clientStatus.DISCONNECTED

    client.disconnect()
    server.stop()

    sleep(3)

    assert status_s == serverStatus.STOPPED
    assert status_c == clientStatus.DISCONNECTED


def test_connection():
    server = Server(status_handler1, msg_handler1)
    server.start("localhost", 8080, './server_cert/example4096_1.crt', "./server_cert/example4096_1.key")

    client = Client(status_handler2)
    client.connect(msg_handler2, "localhost", 8080, './server_cert/example4096_1.crt', 0)

    check_connection(server, client)


def test_invalid_certificate():
    server = Server(status_handler1, msg_handler1)
    server.start("localhost", 8080, './server_cert/example4096_2.crt', "./server_cert/example4096_2.key")

    client = Client(status_handler2)
    client.connect(msg_handler2, "localhost", 8080, './server_cert/example4096_1.crt', 0)

    check_failure_connection(server, client)


def test_auth():
    server = Server(status_handler1, msg_handler1)
    server.start("localhost", 8080,
                 './server_cert/example4096_1.crt',
                 "./server_cert/example4096_1.key",
                 "./client_cert/client1.crt")

    client = Client(status_handler2)
    client.connect(msg_handler2, "localhost", 8080,
                   "./server_cert/example4096_1.crt", 0,
                   "./client_cert/client1.crt",
                   "./client_cert/client1.key")

    check_connection(server, client)


def test_invalid_auth():
    server = Server(status_handler1, msg_handler1)
    server.start("localhost", 8080,
                 './server_cert/example4096_1.crt',
                 "./server_cert/example4096_1.key",
                 "./client_cert/client1.crt")

    client = Client(status_handler2)
    client.connect(msg_handler2, "localhost", 8080,
                   "./server_cert/example4096_1.crt", 0,
                   "./client_cert/client2.crt",
                   "./client_cert/client2.key")

    check_failure_connection(server, client)


def test_min_key():
    server = Server(status_handler1, msg_handler1)
    server.start("localhost", 8080, './server_cert/example4096_1.crt', "./server_cert/example4096_1.key")

    client = Client(status_handler2)
    client.connect(msg_handler2, "localhost", 8080, './server_cert/example4096_1.crt', 3000)

    check_connection(server, client)


def test_invalid_min_key():
    server = Server(status_handler1, msg_handler1)
    server.start("localhost", 8080, './server_cert/server2048.crt', './server_cert/server2048.key')

    client = Client(status_handler2)
    client.connect(msg_handler2, "localhost", 8080, './server_cert/server2048.crt', 3000)

    check_failure_connection(server, client)
