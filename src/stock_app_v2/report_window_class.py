# from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSortFilterProxyModel, pyqtSlot, QSignalMapper, QPoint, QRegExp, Qt, QAbstractTableModel, \
    QVariant, QModelIndex, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QAction, QFileDialog, QLabel, QVBoxLayout, \
    QGridLayout, QMenu, QPushButton, QToolButton, QListWidget, QCheckBox, QHBoxLayout, QDialog

from PyQt5.QtWidgets import QLineEdit, QTableView, QComboBox, QWidget
import pandas as pd

from stock_app_v2.pandas_model import PandasModel
from stock_app_v2.column_filter_dialog import ColumnFilterDialog
from stock_app_v2.custom_proxy_model import CustomProxyModel


class ReportWindow(QMainWindow):
    def __init__(self, report_name, report_df):
        super().__init__()
        self.report_name = report_name
        self.report_df = report_df

        self.setWindowTitle(self.report_name)

        self.centralwidget  = QWidget(self)
        self.lineEdit       = QLineEdit(self.centralwidget)
        self.view           = QTableView(self.centralwidget)
        self.comboBox       = QComboBox(self.centralwidget)
        self.label          = QLabel(self.centralwidget)

        self.view.setCornerButtonEnabled(False)

        self.save_file = QAction(self)
        self.save_file.setText("Save As...")
        self.save_file.setShortcut('Ctrl+Shift+S')
        self.save_file.triggered.connect(self.show_dialog)

        self.toolButton = QToolButton()
        self.toolButton.setDefaultAction(self.save_file)

        self.reset_button = QPushButton('RESET FILTER', self)
        self.reset_button.clicked.connect(self.reset_filter)

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.view, 2, 0, 1, 3)
        self.gridLayout.addWidget(self.comboBox, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.gridLayout.addWidget(self.toolButton, 0, 0)

        self.gridLayout.addWidget(self.reset_button, 0, 2)

        self.setCentralWidget(self.centralwidget)
        self.label.setText("Regex Filter")

        self.model = PandasModel(self.report_df)

        self.proxy = CustomProxyModel(self)

        self.proxy.setSourceModel(self.model)

        self.view.setModel(self.proxy)
        self.view.setSortingEnabled(True)

        self.comboBox.addItems([col for col in self.model._dataframe.columns])
        self.view.resizeColumnsToContents()

        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.viewport().installEventFilter(self)

        self.selected_checkboxes = {}

    #  ______________________________________________________________________________________
    #     # PAGINATION
    #     self.page_size = 10
    #
    #     self.prev_button = QPushButton("Previous")
    #     self.next_button = QPushButton("Next")
    #
    #     self.prev_button.clicked.connect(self.prevPage)
    #     self.next_button.clicked.connect(self.nextPage)
    #
    #     self.gridLayout.addWidget(self.prev_button, 3, 0)
    #     self.gridLayout.addWidget(self.next_button, 3, 1)
    #
    #     self.updatePageButtons()
    #
    # def nextPage(self):
    #     print('nextPage')
    #     self.proxy.nextPage()
    #     self.updatePageButtons()
    #
    # def prevPage(self):
    #     print('prevPage')
    #     self.proxy.previousPage()
    #     self.updatePageButtons()
    #
    # def updatePageButtons(self):
    #     print('================updatePageButtons')
    #     self.prev_button.setEnabled(self.proxy.current_page > 0)
    #     self.next_button.setEnabled(self.proxy.current_page < (len(self.proxy.acceptedRows) // self.page_size))

#---------------------------------------------

    def eventFilter(self, QObject, event):
        if event.type() == QEvent.MouseButtonPress:
            print('START----------event')
            if event.button() == Qt.RightButton:
                print("-----------Right button clicked")
                index = self.view.indexAt(event.pos())
                print('index.row()', index.row())
                print('index.column()', index.column())
                self.on_view_horizontalHeader_sectionClicked(index.column())
                print("END-----------Right button clicked")
            if event.button() == Qt.LeftButton:
                print("-----------Left button clicked")
                index = self.view.indexAt(event.pos())
                print('index.row()', index.row())
                print('index.column()', index.column())
                print("END-----------Left button clicked")
            print("END-----------event")
        return False

    @pyqtSlot(int)
    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):
        sourceModel = self.proxy.sourceModel()  #

        column_values = []
        print('self.proxy.acceptedRows: ', (self.proxy.acceptedRows))
        print('self.model.rowCount(): ', self.model.rowCount())
        print('len(self.proxy.acceptedRows): ', len(self.proxy.acceptedRows))
        for row in self.proxy.acceptedRows:
            print('row: ', row)
            item = sourceModel.index(row, logicalIndex).data(Qt.DisplayRole)
            value = item
            elem = {"value": value, "checked": True}
            if elem not in column_values:
                column_values.append({"value": value, "checked": True})

        if logicalIndex in self.selected_checkboxes:
            for value_info in column_values:
                value_info["checked"] = value_info["value"] in self.selected_checkboxes[logicalIndex]
        print('-------------------------------')
        print('column_values: ', column_values)
        print('1 self.selected_checkboxes: ', self.selected_checkboxes)

        self.dialog = ColumnFilterDialog(column_values, self)

        result = self.dialog.exec_()
        print('is QDialog.Accepted: ', result)
        if result == QDialog.Accepted:
            checked_items = self.dialog.get_checked_items()
            self.selected_checkboxes[logicalIndex] = checked_items
            self.proxy.setFilterDict(self.selected_checkboxes)
            print('2 self.selected_checkboxes: ', self.selected_checkboxes)
            print('checked_items: ', checked_items)

            # self.updatePageButtons()


    @pyqtSlot(str)
    def on_lineEdit_textChanged(self, text):
        # print('on_lineEdit_textChanged')

        self.proxy.setFilter(text, self.proxy.filterKeyColumn())

        # self.updatePageButtons()


    @pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        # print('on_comboBox_currentIndexChanged')
        self.logicalIndex = index
        self.proxy.setFilterKeyColumn(index)


    def reset_filter(self):
        print('-------------reset_filter')
        sourceModel = self.proxy.sourceModel()

        self.proxy.setFilter('', self.proxy.filterKeyColumn())
        self.proxy.setFilterDict({})
        # self.proxy.setCurrentPage(0)
        print('self.model.rowCount(): ', self.model.rowCount())
        self.selected_checkboxes = {i: [
            sourceModel.index(row, i).data(Qt.DisplayRole) for row in range(self.model.rowCount())
        ] for i in range(self.model.columnCount())}

        # self.updatePageButtons()

    def is_digit_check(self, string):
        if string.isdigit():
            return int(string)
        else:
            try:
                float(string)
                return float(string)
            except ValueError:
                return string

    def getFilteredDataFrame(self):
        sourceModel = self.proxy.sourceModel()
        filtered_data = []
        for row in range(sourceModel.rowCount()):
            if self.proxy.filterAcceptsRow(row, QModelIndex()):
                row_data = [sourceModel.index(row, col).data(Qt.DisplayRole) for col in range(sourceModel.columnCount())]
                row_data = [self.is_digit_check(x) for x in row_data]
                filtered_data.append(row_data)

        res_df = pd.DataFrame(filtered_data, columns=self.model._dataframe.columns)

        return res_df

    def show_dialog(self):
        df_to_save = self.getFilteredDataFrame()
        file_path = QFileDialog.getSaveFileName(self, 'Save file', f'/{self.report_name}.xlsx')[0]
        if file_path:
            try:
                df_to_save.to_excel(f'{file_path}', index=False)
            except Exception as e:
                print(f'ОШИБКА {type(e)}: {e}')


