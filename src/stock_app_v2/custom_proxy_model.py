from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex, QRegExp, Qt

from stock_app_v2.pandas_model import PandasModel


class CustomProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filterDict = {}
        self.acceptedRows = set()

        self._filters = dict()
# ----------------------------------------------------------------------- PAGINATION
#         self.page_size = 10  # Number of rows per page
#         self.current_page = 0  # Current page index
#
#     def setPageSize(self, page_size):#
#         self.page_size = page_size
#         self.invalidate()
#         # self.invalidateFilter()
#
#     def pageCount(self):
#         print('++++++++++++++ pageCount')
#         # total_rows = self.sourceModel().rowCount()
#         # page_count = (total_rows + self.page_size - 1) // self.page_size
#         print('len(self.acceptedRows): ', (len(self.acceptedRows)))
#         page_count = (len(self.acceptedRows) + self.page_size - 1) // self.page_size
#         print('page_count: ', page_count)
#         self.invalidate()
#         # self.invalidateFilter()
#         return page_count
#
#     def setCurrentPage(self, page):#
#         print('++++++++++++ page: ', page)
#         self.current_page = page
#         self.invalidate()
#         # self.invalidateFilter()
#
#     def nextPage(self):#
#         print('+++++++++++++++ nextPage')
#         self.setCurrentPage(self.current_page + 1)
#
#     def previousPage(self):#
#         print('+++++++++++++++ previousPage')
#         self.setCurrentPage(self.current_page - 1)
#
#     def rowCount(self, parent=QModelIndex()): #
#         print('+++++++++++++++++ rowCount')
#         # row_count = min(
#         #     len(self.acceptedRows),
#         #     (self.current_page + 1) * self.page_size,
#         # )
#
#         start_row = self.current_page * self.page_size
#         end_row = min(start_row + self.page_size, len(self.acceptedRows))
#         row_count = end_row - start_row
#
#         print('row_count: ', row_count)
#         return row_count
#
#     def mapToSource(self, proxyIndex):
#         if not proxyIndex.isValid():
#             return QModelIndex()
#
#         source_row = proxyIndex.row() + self.current_page * self.page_size
#         source_row_idx = self.sourceModel().index(source_row, proxyIndex.column())
#
#         # source_row = proxyIndex.row()  # No changes needed for row
#         # source_col = proxyIndex.column()  # No changes needed for column
#         # source_row_idx = self.sourceModel().index(source_row, source_col)
#
#         return source_row_idx
#
#
#     def mapFromSource(self, sourceIndex):
#
#         print('+++++++++++ mapFromSource')
#
#         if not sourceIndex.isValid():
#             return QModelIndex()
#
#         print('sourceIndex.row(): ', sourceIndex.row())
#         print('sourceIndex.column(): ', sourceIndex.column())
#
#         proxy_row_idx = self.sourceModel().index(
#             sourceIndex.row() - self.current_page * self.page_size,
#             sourceIndex.column()
#         )
#
#         # proxy_row = sourceIndex.row()  # No changes needed for row
#         # proxy_col = sourceIndex.column()  # No changes needed for column
#         # proxy_row_idx = self.createIndex(proxy_row, proxy_col)
#
#         print('proxy_row_idx: ', proxy_row_idx)
#         return proxy_row_idx

# -------------------------------------------------------------------------------

    @property
    def filters(self):
        return self._filters

    def setFilter(self, expresion, column):
        print('setFilter--->', expresion, column)
        if expresion:
            self.filters[column] = expresion
        elif column in self.filters:
            del self.filters[column]
        print('1filt:', self.filters)
        # self.setCurrentPage(0)  #
        self.invalidateFilter()
        # self.setCurrentPage(0)  #
        print('2filt:', self.filters)

    def setFilterDict(self, filterDict):
        print('--------------setFilterDict:', filterDict)
        self.filterDict = filterDict
        # self.setCurrentPage(0)  #
        self.invalidateFilter()
        # self.setCurrentPage(0)  #
        print('END ----------------setFilterDict:', self.filterDict)


    def filterAcceptsRow(self, sourceRow, sourceParent):

        for column, expresion in self.filters.items():
            print('-----column, expresion: ', column, expresion)
            print('source_row: ', sourceRow)
            # index = self.sourceModel().index(sourceRow, column, sourceParent)
            # text = self.sourceModel().data(index)
            text = self.sourceModel().index(sourceRow, column, sourceParent).data()
            print(text)
            regex = QRegExp(
                expresion, Qt.CaseInsensitive, QRegExp.RegExp
            )
            # print('regex.indexIn(text): ', regex.indexIn(text))
            if regex.indexIn(text) == -1:
                self.acceptedRows.discard(sourceRow)
                print('3 discard from acceptedRows: ', self.acceptedRows)
                return False

        if not self.filterDict:
            self.acceptedRows.add(sourceRow)
            print('go')
            return True

        if sourceRow not in self.acceptedRows:
            print('1 discard from acceptedRows: ', self.acceptedRows)
            print('self.filterDict --- ', self.filterDict)
            return False

        for column, values in self.filterDict.items():
            value = self.sourceModel().index(sourceRow, column, sourceParent).data()
            print('value: ', value)

            if value not in values:
                print('!!! acceptedRows: ', self.acceptedRows)
                self.acceptedRows.discard(sourceRow)
                print('2 discard from acceptedRows: ', self.acceptedRows)
                return False

        print('row accepted')
        return True

    # def lessThan(self, left, right):
    #     print('++++++++++++ lessThan')
    #     left_data = self.sourceModel().data(left)
    #     right_data = self.sourceModel().data(right)
    #     # Check if the data is numeric
    #     if left_data.replace('.', '').isdigit() and right_data.replace('.', '').isdigit():
    #         print('digits')
    #         left_data = self.sourceModel().data(left, Qt.EditRole)
    #         right_data = self.sourceModel().data(right, Qt.EditRole)
    #         return float(left_data) < float(right_data)
    #     else:
    #         # For non-numeric data, fall back to default string comparison
    #         print('strings')
    #         return super().lessThan(left, right)

    def sort(self, column, order):

        print('--------------sort proxy')
        print('column: ', column)
        print('sort: ', order)

        source_model = self.sourceModel()

        if isinstance(source_model, PandasModel):
            source_column = self.mapToSource(self.index(0, column)).column()
            self.acceptedRows = set([i for i in range(source_model.rowCount())])
            source_model.sort(source_column, order)
            print('source_model.sort(source_column, order): ')

        else:
            print('isinstance_super')
            super().sort(column, order)
        print('END--------------sort proxy')