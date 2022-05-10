from os import listdir
from os.path import isfile, join
from typing import List
import ssl

from PyQt6 import QtWidgets


def error(text: str):
    msg = QtWidgets.QMessageBox()
    msg.setText("Error")
    msg.setInformativeText(text)
    msg.setWindowTitle("Error")
    msg.exec()


def check_associate_cert_with_private_key(cert: str, private_key: str):
    try:
        context = ssl.create_default_context()
        context.load_cert_chain(cert, private_key)
        return True
    except ssl.SSLError:
        return False


class SelectPair(QtWidgets.QDialog):
    def __init__(self, path: str):
        super(SelectPair, self).__init__()
        self.setWindowTitle("Выбор сертификата и ключа")

        self.path = path

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.certList = QtWidgets.QListWidget()
        self.certList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.keyList = QtWidgets.QListWidget()
        self.keyList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        self.layout1 = QtWidgets.QVBoxLayout()
        self.layout1.addWidget(QtWidgets.QLabel("Сертификат"))
        self.layout1.addWidget(self.certList)

        self.layout2 = QtWidgets.QVBoxLayout()
        self.layout2.addWidget(QtWidgets.QLabel("Приватный ключ"))
        self.layout2.addWidget(self.keyList)

        self.select_layout = QtWidgets.QHBoxLayout()
        # self.select_layout.addWidget(self.certList)
        # self.select_layout.addWidget(self.keyList)
        self.select_layout.addLayout(self.layout1)
        self.select_layout.addLayout(self.layout2)

        self.get_list_of_files()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.select_layout)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def get_list_of_files(self):
        files = [f for f in listdir(self.path)
                 if isfile(join(self.path, f))]
        self.certList.addItems(files)
        self.keyList.addItems(files)

    def get_data(self) -> List[QtWidgets.QListWidgetItem]:
        return self.certList.selectedItems()

    @staticmethod
    def get_certs(path: str):
        dialog = SelectPair(path)
        while dialog.exec() == 1:
            list1 = [f.text() for f in dialog.certList.selectedItems()]
            list2 = [f.text() for f in dialog.keyList.selectedItems()]
            if len(list1) == 0 or len(list2) == 0 or \
                    not check_associate_cert_with_private_key(path+list1[0], path+list2[0]):
                error("invalid certificate or key")
                continue
            return list1[0], list2[0]
        return None, None
