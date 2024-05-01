from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex, QRegExp, Qt

from stock_app_v2.pandas_model import PandasModel


class CustomProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filterDict = {}
        self.acceptedRows = set()
        # self.acceptedRows = []

        self._filters = dict()
# ----------------------------------------------------------------------- PAGINATION
        self.page_size = 10  # Number of rows per page
        self.current_page = 0  # Current page index

    def setPageSize(self, page_size):
        self.page_size = page_size
        self.invalidate()

    def pageCount(self):
        print('++++++++++++++ pageCount')
        print('len(self.acceptedRows): ', (len(self.acceptedRows)))
        page_count = 1 + (len(self.acceptedRows) // self.page_size) if (
                len(self.acceptedRows) % self.page_size
        ) else (len(self.acceptedRows) // self.page_size)
        print('page_count: ', page_count)
        self.invalidate()
        return page_count

    def setCurrentPage(self, page):
        print('++++++++++++ setCurrentPage --- page: ', page)
        self.current_page = page
        self.invalidate()

    def nextPage(self):
        print('+++++++++++++++ nextPage')
        self.setCurrentPage(self.current_page + 1)

    def previousPage(self):
        print('+++++++++++++++ previousPage')
        self.setCurrentPage(self.current_page - 1)

    def rowCount(self, parent=QModelIndex()):
        # print('+++++++++++++++++ rowCount')

        start_row = self.current_page * self.page_size
        end_row = min(start_row + self.page_size, len(self.acceptedRows))
        row_count = end_row - start_row

        # print('row_count: ', row_count)
        return row_count
#
    def mapToSource(self, proxyIndex):

        if not proxyIndex.isValid():
            return QModelIndex()

        # # source_row = proxyIndex.row()  # No changes needed for row
        # source_row = list(self.acceptedRows)[proxyIndex.row()]
        # source_col = proxyIndex.column()  # No changes needed for column
        # source_row_idx = self.sourceModel().index(source_row, source_col)
        # #
        # return source_row_idx

        source_row = list(self.acceptedRows)[proxyIndex.row() + self.current_page * self.page_size]
        source_col = proxyIndex.column()  # No changes needed for column
        source_row_idx = self.sourceModel().index(source_row, source_col)

        return source_row_idx


    def mapFromSource(self, sourceIndex):

        # print('+++++++++++ mapFromSource')
        # print('sourceIndex.row(): ', sourceIndex.row())
        # print('sourceIndex.column(): ', sourceIndex.column())

        if not sourceIndex.isValid():
            # print(QModelIndex().row(), QModelIndex().column())
            return QModelIndex()

        # if sourceIndex.row() in self.acceptedRows:
        #     proxy_row = list(self.acceptedRows).index(sourceIndex.row())
        #     print('proxy_row: ', proxy_row)
        #     proxy_col = sourceIndex.column()  # No changes needed for column
        #     proxy_row_idx = self.createIndex(proxy_row, proxy_col)
        #
        #     print('proxy_row_idx: ', proxy_row_idx)
        #     return proxy_row_idx
        # else:
        #     return QModelIndex()

        # if sourceIndex.row() in self.acceptedRows:
        #     print('sourceIndex.row(): ', sourceIndex.row())
        #     print('list(self.acceptedRows).index(sourceIndex.row()): ', list(self.acceptedRows).index(sourceIndex.row()))
            proxy_row = list(self.acceptedRows).index(sourceIndex.row()) - self.current_page * self.page_size
            # print('proxy_row: ', proxy_row)
            proxy_col = sourceIndex.column()  # No changes needed for column
            proxy_row_idx = self.createIndex(proxy_row, proxy_col)

            # print('proxy_row_idx: ', proxy_row_idx)
            return proxy_row_idx
        else:
            return QModelIndex()

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
        self.setCurrentPage(0)  # pagination
        self.invalidateFilter()
        # self.invalidate()
        print('filt --- len(self.acceptedRows):', len(self.acceptedRows))
        print('2filt:', self.filters)

    def setFilterDict(self, filterDict):
        print('--------------setFilterDict:', filterDict)
        self.filterDict = filterDict
        self.setCurrentPage(0)  # pagination
        self.invalidateFilter()
        # self.invalidate()
        print('END ----------------setFilterDict:', self.filterDict)


    def filterAcceptsRow(self, sourceRow, sourceParent):
        # print('++++++++++++++filterAcceptsRow')
        if self.filters:
            for column, expresion in self.filters.items():
                # print('-----column, expresion: ', column, expresion)
                # print('source_row: ', sourceRow)
                text = self.sourceModel().index(sourceRow, column, sourceParent).data()
                # print(text)
                regex = QRegExp(
                    expresion, Qt.CaseInsensitive, QRegExp.RegExp
                )
                # print('regex.indexIn(text): ', regex.indexIn(text))
                if regex.indexIn(text) == -1:
                    self.acceptedRows.discard(sourceRow)
                    # self.acceptedRows.remove(sourceRow)
                    # print('source_row: ', sourceRow)
                    # print('3 discard from acceptedRows: ', self.acceptedRows)
                    return False
        else:
            self.acceptedRows.add(sourceRow)

        if self.filterDict:
            for column, values in self.filterDict.items():
                value = self.sourceModel().index(sourceRow, column, sourceParent).data()
                # print('value: ', value)

                if value not in values:
                    # print('!!! acceptedRows: ', self.acceptedRows)
                    self.acceptedRows.discard(sourceRow)
                    # self.acceptedRows.remove(sourceRow)
                    # print('2 discard from acceptedRows: ', self.acceptedRows)
                    return False
        else:
            self.acceptedRows.add(sourceRow)

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
            # source_column = column
            source_column = self.mapToSource(self.index(0, column)).column()
            self.acceptedRows = set([i for i in range(source_model.rowCount())])
            # self.acceptedRows = [i for i in range(source_model.rowCount())]
            source_model.sort(source_column, order)
            print('source_model.sort(source_column, order): ')

        else:
            print('isinstance_super')
            super().sort(column, order)
        print('END--------------sort proxy')

