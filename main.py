import sys

from PyQt6 import QtWidgets

from server_app import ServerApp
from client_app import ClientApp


def main():
    app = QtWidgets.QApplication([])

    server_app = ServerApp()
    server_app.setWindowTitle("Server")
    server_app.resize(400, 300)
    server_app.move(10, 50)
    server_app.show()

    client_app = ClientApp()
    client_app.setWindowTitle("Client")
    client_app.resize(400, 300)
    client_app.move(430, 50)
    client_app.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
