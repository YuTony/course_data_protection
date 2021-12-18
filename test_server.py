from client import Client, Status as clientStatus
from server import Server, Status as serverStatus


def test_connection():
    msg_s: str | None
    msg_c: str | None
    status_s: serverStatus | None
    status_c: clientStatus | None

    def status_handler1(s: serverStatus):
        status_s = s

    def status_handler2(s: clientStatus):
        status_c = s

    def msg_handler1(m: str):
        assert m == "Hello, server"

    def msg_handler2(m: str):
        assert m == "Hello, client"

    server = Server(status_handler1, msg_handler1)
    server.start("localhost", 8080, './server_cert/example4096_1.crt', "./server_cert/example4096_1.key", False)

    client = Client(status_handler2)
    client.connect(msg_handler2, "localhost", 8080, './server_cert/example4096_1.crt', 0)

    client.send_msg("Hello, server")
    server.send_msg("Hello, client")
