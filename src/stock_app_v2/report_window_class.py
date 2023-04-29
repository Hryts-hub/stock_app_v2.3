# from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QAction, QFileDialog, QLabel, QVBoxLayout


class ReportWindow(QMainWindow):
    def __init__(self, report_name, report_df):
        super().__init__()
        self.report_name = report_name
        self.report_df = report_df

        self.setWindowTitle(self.report_name)
        self.table = QTableWidget()
        self.setCentralWidget(self.table)

        # def fillTable
        cols = self.report_df.shape[1]
        rows = self.report_df.shape[0]

        self.table.setColumnCount(cols)
        self.table.setRowCount(rows)

        [self.table.setHorizontalHeaderItem(i, QTableWidgetItem(report_df.columns[i]))
         for i in range(cols)]

        [[self.table.setItem(i, j, QTableWidgetItem(str(report_df.iloc[i, j])))
          for j in range(cols)]
         for i in range(rows)]

        save_file = QAction('Save As...', self)  # QIcon('save.png'),
        save_file.setShortcut('Ctrl+Shift+S')
        save_file.triggered.connect(self.show_dialog)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&Save data to your Excel File')
        file_menu.addAction(save_file)

    def show_dialog(self):
        file_path = QFileDialog.getSaveFileName(self, 'Save file', f'/{self.report_name}.xlsx')[0]
        if file_path:
            try:
                self.report_df.to_excel(f'{file_path}', index=False)
            except Exception as e:
                print(f'ОШИБКА {type(e)}: {e}')


