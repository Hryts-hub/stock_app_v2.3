import pandas as pd

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QAbstractItemModel


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe):
        super().__init__()
        self._dataframe = dataframe

    def rowCount(self, parent=None):
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        return self._dataframe.shape[0]

    def columnCount(self, parent=None):
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        return self._dataframe.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        value = self._dataframe.iloc[index.row(), index.column()]

        if role == Qt.DisplayRole:

            if pd.isna(value):
                return ""

            return str(value)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None

    def sort(self, column, order):
        print('-----------column sort Panda: ', column)
        print('self._dataframe.columns[column]: ', self._dataframe.columns[column])
        print('sort Panda order: ', order)
        print('self._dataframe.dtypes[column]: ', self._dataframe.dtypes[column])

        self.layoutAboutToBeChanged.emit()

        if self._dataframe.dtypes[column] in ('int32', 'float64'):
            if order == Qt.DescendingOrder:
                self._dataframe.sort_values(
                    by=self._dataframe.columns[column],
                    ascending=False,
                    inplace=True
                )
            else:
                self._dataframe.sort_values(
                    by=self._dataframe.columns[column],
                    ascending=True,
                    inplace=True
                )
        else:
            try:
                self._dataframe.sort_values(
                    by=self._dataframe.columns[column],
                    ascending=order == Qt.AscendingOrder,
                    inplace=True,
                    key=lambda x: x.astype(str)
                )
            except Exception as e:
                print(f'ERROR: {type(e)}: {e}')
        self._dataframe.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()

        print('END----------- sort panda')
