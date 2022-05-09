from os import listdir, remove
from os.path import isfile, join
import re

from PyQt6 import QtWidgets


def error(text: str):
    msg = QtWidgets.QMessageBox()
    msg.setText("Error")
    msg.setInformativeText(text)
    msg.setWindowTitle("Error")
    msg.exec()


class SelectClients(QtWidgets.QDialog):
    def __init__(self, path1: str, path2: str):
        super(SelectClients, self).__init__()
        self.setWindowTitle("Выбор сертификатов")

        self.path1 = path1
        self.path2 = path2

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.certList = QtWidgets.QListWidget()
        self.certList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

        self.select_layout = QtWidgets.QHBoxLayout()
        self.select_layout.addWidget(self.certList)

        self.get_list_of_files()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.select_layout)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def get_list_of_files(self):
        files = [f for f in listdir(self.path1)
                 if isfile(join(self.path1, f)) and re.search(r"^\w*\.crt$", f)]
        self.certList.addItems(files)

    def select_items(self):
        files = [f.text() for f in self.certList.selectedItems()]
        # for file in files:
        #     copyfile(self.path1 + file, self.path2 + file)
        data = ""
        for f in files:
            with open(self.path1 + f) as fp:
                data += fp.read() + "\n"
        with open(self.path2 + "trusted.crt", 'w') as fp:
            fp.write(data)

    def clear_dir(self):
        for filename in listdir(self.path2):
            file_path = join(self.path2, filename)
            try:
                if isfile(file_path):
                    remove(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    @staticmethod
    def select_certs(path1: str, path2: str):
        dialog = SelectClients(path1, path2)
        if dialog.exec() == 1:
            dialog.clear_dir()
            dialog.select_items()
