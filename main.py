import threading

from PyQt6 import QtWidgets

from server_app import ServerApp
from client_app import ClientApp


def main():
    app = QtWidgets.QApplication([])

    widget = ServerApp()
    widget.setWindowTitle("Server")
    widget.resize(400, 300)
    widget.move(10, 50)
    widget.show()

    widget1 = ClientApp()
    widget1.setWindowTitle("Client")
    widget1.resize(400, 300)
    widget1.move(430, 50)
    widget1.show()

    app.exec()


if __name__ == "__main__":
    main()
