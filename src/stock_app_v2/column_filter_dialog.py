from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox


class ColumnFilterDialog(QDialog):
    def __init__(self, column_values, parent=None):
        super().__init__(parent)

        self.setWindowTitle('FILTER')

        layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.checkbox_layout = QVBoxLayout()
        layout.addLayout(self.checkbox_layout)

        # button_layout = QHBoxLayout()
        # ok_button = QPushButton("OK")
        # ok_button.clicked.connect(self.accept)
        # cancel_button = QPushButton("Cancel")
        # cancel_button.clicked.connect(self.reject)
        #
        # button_layout.addWidget(ok_button)
        # button_layout.addWidget(cancel_button)
        #
        # layout.addLayout(button_layout)

        self.column_values = column_values

        self.create_checkboxes()

    def create_checkboxes(self):
        # print('create_checkboxes')
        all_checked = all(value["checked"] for value in self.column_values)
        all_checkbox = self.add_checkbox("ALL", all_checked)
        all_checkbox.stateChanged.connect(self.on_all_checkbox_stateChanged)

        for value_info in self.column_values:
            checkbox = self.add_checkbox(value_info["value"], value_info["checked"])
            # checkbox.stateChanged.connect(self.on_checkbox_stateChanged)
        # print('END create_checkboxes')

    def add_checkbox(self, label, checked=False):
        # print('add_checkbox')
        checkbox = QCheckBox(label)
        checkbox.setChecked(checked)
        self.checkbox_layout.addWidget(checkbox)
        # print('END add_checkbox')
        return checkbox

    def get_checked_items(self):
        # print('get_checked_items + END')
        return [checkbox.text() for checkbox in self.findChildren(QCheckBox) if checkbox.isChecked()]

    @pyqtSlot(int)
    def on_all_checkbox_stateChanged(self, state):
        # print('on_all_checkbox_stateChanged')
        # print(self.findChildren(QCheckBox))
        for checkbox in self.findChildren(QCheckBox):
            # print(checkbox)
            checkbox.setChecked(state == Qt.Checked)
        # print('END on_all_checkbox_stateChanged')

    # @pyqtSlot(int)
    # def on_checkbox_stateChanged(self, state):
    #     # print('on_checkbox_stateChanged')
    #     all_checkbox = self.findChild(QCheckBox, "ALL")
    #     # print(all_checkbox)
    #     if state == Qt.Unchecked:
    #         print(1, state)
    #         # all_checkbox.setChecked(False)
    #         # print('state')
    #     else:
    #         print(2, state)
    #         if all(checkbox.isChecked() for checkbox in self.findChildren(QCheckBox) if checkbox != all_checkbox):
    #             print('checkbox')
    #             # all_checkbox.setChecked(True)
    #     # print('END on_checkbox_stateChanged')

    @pyqtSlot(int)
    def check_all_checkboxes(self, state):
        # print('check_all_checkboxes')
        # print(self.findChildren(QCheckBox))
        for checkbox in self.findChildren(QCheckBox):
            # print(checkbox)
            checkbox.setChecked(state == Qt.Checked)
        # print('check_all_checkboxes')