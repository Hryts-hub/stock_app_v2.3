from PyQt5.QtCore import pyqtSlot, Qt, QModelIndex, QEvent, QDate, QDateTime

from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QLabel, \
    QGridLayout, QPushButton, QToolButton, QDialog, QDateEdit, QDateTimeEdit

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
        self.reset_button.setStyleSheet('background: rgb(255,165,0);')  # orange
        self.reset_button.clicked.connect(self.reset_filter)

        self.set_button = QPushButton('APPLY FILTERS', self)
        self.set_button.setStyleSheet('background: rgb(255,255,0);')  # yellow
        self.set_button.clicked.connect(self.apply_filters)

        self.text_button = QPushButton('ACCEPT TEXT', self)
        self.text_button.setStyleSheet('background: rgb(0,255,0);')  # green
        self.text_button.clicked.connect(self.on_lineEdit_text_accept)


        self.retext_button = QPushButton('RESET TEXT', self)
        self.retext_button.setStyleSheet('background: rgb(255,165,0);')  # orange
        self.retext_button.clicked.connect(self.on_lineEdit_text_delete)

        #----------------------------
        self.fromDateEdit = QDateEdit()
        # self.fromDateEdit.setDate(QDate(2006, 12, 22))
        self.fromDateEdit.setDisplayFormat("dd-MM-yyyy")
        self.fromDateEdit.setCalendarPopup(True)
        fromLabel = QLabel("F&rom date:")
        fromLabel.setBuddy(self.fromDateEdit)
        self.fromDateEdit.setEnabled(False)

        # self.toDateEdit = QDateEdit()
        self.toDateEdit = QDateTimeEdit(QDate.currentDate())
        # self.toDateEdit.setDate(QDate(2007, 1, 5))
        # self.toDateEdit.setDateTime(QDateTime.currentDateTime())
        # dateEdit = QDateTimeEdit(QDate.currentDate())
        self.toDateEdit.setDisplayFormat("dd-MM-yyyy")
        self.toDateEdit.setCalendarPopup(True)
        toLabel = QLabel("&To date:")
        toLabel.setBuddy(self.toDateEdit)
        self.toDateEdit.setEnabled(False)

        self.redate_button = QPushButton('RESET DATE RANGE', self)
        self.redate_button.setStyleSheet('background: rgb(255,200,100);')  # orange
        self.redate_button.clicked.connect(self.reset_date_filter)
        self.redate_button.setEnabled(False)

        self.date_button = QPushButton('SET DATE RANGE', self)
        self.date_button.setStyleSheet('background: rgb(100,255,100);')  # green
        self.date_button.clicked.connect(self.set_date_filter)
        self.date_button.setEnabled(False)
        # ----------------------------+
        # rows and cols are 0-indexed
        # self.gridLayout.addWidget(widget_being_added_to_the_layout, row_idx, col_idx, rows_span, cols_span)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.view, 4, 0, 1, 5)
        self.gridLayout.addWidget(self.comboBox, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.text_button, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.retext_button, 1, 4, 1, 1)
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        #---------------------
        self.gridLayout.addWidget(self.set_button, 0, 3, 1, 1)
        self.gridLayout.addWidget(fromLabel, 2, 0)
        self.gridLayout.addWidget(self.fromDateEdit, 2, 1, 1, 2)
        self.gridLayout.addWidget(toLabel, 3, 0)
        self.gridLayout.addWidget(self.toDateEdit, 3, 1, 1, 2)
        self.gridLayout.addWidget(self.redate_button, 3, 4, 1, 1)
        self.gridLayout.addWidget(self.date_button, 3, 3, 1, 1)
        #---------------------+

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
        # self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.filter_text = ''
        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        #-----------------
        # self.dateFilterChanged()
        self.date_cols_list = self.get_date_cols_list()
        self.date_cols_dict = dict()
        #-----------------+

        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.viewport().installEventFilter(self)

        self.selected_checkboxes = {}

    #  ______________________________________________________________________________________
        # PAGINATION
        self.page_size = 10

        self.prev_button = QPushButton("Previous")
        self.current_page_label = QLabel(self.centralwidget)
        self.next_button = QPushButton("Next")
        self.page_count_label = QLabel(self.centralwidget)

        self.prev_button.clicked.connect(self.prevPage)
        self.next_button.clicked.connect(self.nextPage)

        self.gridLayout.addWidget(self.prev_button, 5, 0)
        self.gridLayout.addWidget(self.current_page_label, 5, 1)
        self.gridLayout.addWidget(self.next_button, 5, 2)
        self.gridLayout.addWidget(self.page_count_label, 5, 3)

        self.current_page_label.setText(f'{self.proxy.current_page + 1}')
        self.page_count_label.setText(f'{self.proxy.pageCount()}')

        self.updatePageButtons()

    def nextPage(self):
        print('nextPage')
        self.proxy.set_flag_acceptedRows(True)
        self.proxy.nextPage()
        self.updatePageButtons()

    def prevPage(self):
        print('prevPage')
        self.proxy.set_flag_acceptedRows(True)
        self.proxy.previousPage()
        self.updatePageButtons()

    def updatePageButtons(self):
        print('================updatePageButtons')
        self.prev_button.setEnabled(self.proxy.current_page > 0)
        print('(self.proxy.current_page+1): ', (self.proxy.current_page+1))
        print('self.proxy.pageCount(): ', self.proxy.pageCount())
        # self.next_button.setEnabled(self.proxy.current_page < (len(self.proxy.acceptedRows) // self.page_size))
        self.next_button.setEnabled((self.proxy.current_page+1) < self.proxy.pageCount())
        self.current_page_label.setText(f'CURRENT PAGE: {self.proxy.current_page + 1}')
        self.page_count_label.setText(f'TOTAL PAGES: {self.proxy.pageCount()}')

#---------------------------------------------

    #---------------
    def apply_filters(self):
        self.report_df = self.getFilteredDataFrame()
        self.model = PandasModel(self.report_df)
        self.proxy = CustomProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)
        self.reset_filter()

    def get_date_cols_list(self):
        date_cols_list = [
            self.report_df.columns.get_loc(column)
            for column in self.report_df.columns
            if self.report_df[column].dtype == 'datetime64[ns]'
        ]
        print(f'date_cols_list: {date_cols_list}')

        return date_cols_list

    def set_date_filter(self):
        self.proxy.set_flag_acceptedRows(False)
        self.date_cols_dict[self.logicalIndex] = (self.fromDateEdit.date(), self.toDateEdit.date())
        self.proxy.set_filter_date_columns(self.date_cols_dict)
        self.updatePageButtons()

    def reset_date_filter(self):
        self.proxy.set_flag_acceptedRows(False)
        try:
            self.date_cols_dict.pop(self.logicalIndex)
        except Exception as e:
            print(f'ERROR: {type(e)}: {e}')
        self.proxy.set_filter_date_columns(self.date_cols_dict)
        self.updatePageButtons()
    #---------------+

    def eventFilter(self, QObject, event):
        if event.type() == QEvent.MouseButtonPress:
            print('START----------event')
            if event.button() == Qt.RightButton:
                print("-----------Right button clicked")
                index = self.view.indexAt(event.pos())
                print('index.row()', index.row())
                print('index.column()', index.column())
                if index.column() != -1:
                    self.on_view_horizontalHeader_sectionClicked(index.column())
                else:
                    print('TRY AGAIN')
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
            value = sourceModel.index(row, logicalIndex).data(Qt.DisplayRole)
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
            self.proxy.set_flag_acceptedRows(False)
            self.proxy.setFilterDict(self.selected_checkboxes)
            print('2 self.selected_checkboxes: ', self.selected_checkboxes)
            print('checked_items: ', checked_items)

            self.updatePageButtons()

    @pyqtSlot(str)
    def on_lineEdit_textChanged(self, text):
        self.filter_text = text

    def on_lineEdit_text_accept(self):
        self.proxy.set_flag_acceptedRows(False)
        self.proxy.setFilter(self.filter_text, self.proxy.filterKeyColumn())
        self.updatePageButtons()

    def on_lineEdit_text_delete(self):
        self.proxy.set_flag_acceptedRows(False)
        self.filter_text = ''
        self.proxy.setFilter(self.filter_text, self.proxy.filterKeyColumn())
        self.lineEdit.clear()
        self.updatePageButtons()

    @pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        # print('on_comboBox_currentIndexChanged')
        self.logicalIndex = index
        self.proxy.set_flag_acceptedRows(True)
        self.proxy.setFilterKeyColumn(index)
        self.filter_text = self.proxy._filters.get(self.proxy.filterKeyColumn(), '')
        self.lineEdit.setText(self.filter_text)
        print(index)
        if index in self.date_cols_list:
            self.fromDateEdit.setEnabled(True)
            self.toDateEdit.setEnabled(True)
            self.redate_button.setEnabled(True)
            self.redate_button.setStyleSheet('background: rgb(255,155,0);')  # orange
            self.date_button.setEnabled(True)
            self.date_button.setStyleSheet('background: rgb(0,255,0);')  # green
        else:
            self.fromDateEdit.setEnabled(False)
            self.toDateEdit.setEnabled(False)
            self.redate_button.setEnabled(True)
            self.redate_button.setStyleSheet('background: rgb(255,200,100);')  # gray orange
            self.date_button.setEnabled(False)
            self.date_button.setStyleSheet('background: rgb(100,255,100);')  # gray green

    def reset_filter(self):
        print('-------------reset_filter')
        sourceModel = self.proxy.sourceModel()
        self.date_cols_dict = dict()
        self.proxy.set_filter_date_columns(self.date_cols_dict)
        self.filter_text = ''
        self.lineEdit.clear()
        self.proxy.setFilterDict(dict())
        self.proxy._filters = dict()
        self.selected_checkboxes = {i: [
            sourceModel.index(row, i).data(Qt.DisplayRole) for row in range(self.model.rowCount())
        ] for i in range(self.model.columnCount())}
        self.proxy.sort(0, Qt.AscendingOrder)
        self.updatePageButtons()

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


