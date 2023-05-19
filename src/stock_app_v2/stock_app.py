#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pandas as pd
# to disable warnings
# pd.options.mode.chained_assignment = None  # default='warn'

from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QSpinBox, QCheckBox, QButtonGroup, QProgressBar

# import os.path
#
# from math import fabs

from stock_app_v2.data_reader_class import DataReader
from stock_app_v2.dict_macker_class import DictMaker
from stock_app_v2.report_maker_class import ReportMaker
from stock_app_v2.report_window_class import ReportWindow
from stock_app_v2.validator_class import Validator

# file with names of products and dicts of moduls
# FILE_OF_PRODUCTS = 'data.csv'
FILE_OF_PRODUCTS = 'data_3_col.csv'
PATH_TO_FILE_OF_PRODUCTS = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/'  # {FILE_OF_PRODUCTS}'
# PATH_TO_FILE_OF_PRODUCTS = 'Z:/Склад/'

# columns in this file = columns in data frame
COLUMN_PRODUCT_NAMES = 'наименование блока'
COLUMN_DICT_OF_MODULS = 'словарь модулей'
# !!!
COLUMN_DICT_OF_COMPONENTS = 'словарь эл.компонентов'

FILE_STOCK = 'Склад 14.01.16.xlsx'
# FILE_STOCK = 'Z:/Склад/Склад 14.01.16.xlsx'
PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/'
# PATH_TO_FILE_STOCK = 'Z:/Склад/'


# FILE_OF_SP_PLAT # Склад 14.01.16


class MyApp(QWidget):

    def __init__(self,
                 path_to_file=PATH_TO_FILE_OF_PRODUCTS,
                 file_name=FILE_OF_PRODUCTS,
                 column_name=COLUMN_PRODUCT_NAMES
                 ):
        super().__init__()

        self.path_to_file = path_to_file
        self.file_name = file_name
        # ????????????
        self.column_name = column_name

        self.w = None  # No external window yet

        self.info_label = QLabel()

        self.combo_box_label = QLabel("Выберите изделие:")
        self.comboBox = QComboBox()

        # from class DataReader
        self.data, self.msg, self.color = DataReader(
            self.path_to_file,
            self.file_name).read_csv_file(self.column_name)
        self.data_search = self.data

        # Create widgets for inserting data
        self.label1 = QLabel(f'{COLUMN_PRODUCT_NAMES}:', self)
        self.textbox1 = QLineEdit(self)

        self.label2 = QLabel(f'{COLUMN_DICT_OF_MODULS}:', self)
        self.textbox2 = QTextEdit(self)

        # !!!
        self.label22 = QLabel(f'{COLUMN_DICT_OF_COMPONENTS}:', self)
        self.textbox22 = QTextEdit(self)

        self.label3 = QLabel('количество блоков:', self)
        self.textbox3 = QSpinBox()
        self.textbox3.setMinimum(1)

        self.addButton = QPushButton("Добавить в список")
        self.to_file_addButton = QPushButton("Добавить в файл ")

        self.label_list = QLabel("Выбранные блоки:")
        self.comboBox_list = QComboBox()

        self.removeButton = QPushButton("Убрать из списка")

        # Report_1 получить словарь модулей, которые надо изготовить {арт модуля:кол-во}
        self.report_1_name = 'Report_1: баланс по модулям в блоках'
        self.report_2_name = 'Report_2: баланс по компонентам модулей с отрицатльным балансом'
        self.report_3_name = 'Report_3: BOM'
        self.report_4_name = 'Report_4: баланс по компонентам модулей'

        self.checkBox_report_1 = QCheckBox(self.report_1_name)
        self.checkBox_report_2 = QCheckBox(self.report_2_name)
        self.checkBox_report_3 = QCheckBox(self.report_3_name)
        self.checkBox_report_4 = QCheckBox(self.report_4_name)

        self.func_dict = {}  # {key=self.checkBox_report_N: val=ReportMaker(report_dict, DF).make_report_N}
        self.report_name_dict = {self.checkBox_report_1: self.report_1_name,
                                 self.checkBox_report_2: self.report_2_name,
                                 self.checkBox_report_3: self.report_3_name,
                                 self.checkBox_report_4: self.report_4_name,
                                 }

        self.checkBox_group = QButtonGroup()

        self.reportButton = QPushButton("Получить отчет")

        self.progress_bar = QProgressBar(self)

        self.report_info_label = QLabel()
        self.report_info_label_text = ''

        self.exitButton = QPushButton("Выйти")

        self.block_list_dict = {}  # comboBox dict
        self.old_dict_for_report = {}

        self.modul_stock_isRead = False
        self.modul_df = None

        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle("Приложение СКЛАД")
        self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._search_by_column_product_names()  # get msg and data for comboBox (=self.data_search DF)

        self.info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._set_info_label()

        self.comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.comboBox.setMinimumContentsLength(15)
        self.comboBox.setEditable(True)

        # Add items to combo box
        self._refresh_comboBox()

        # CHOICE AND SEARCH
        self.comboBox.activated.connect(self.update_info_label)
        # ADD BUTTON
        self.addButton.clicked.connect(self.add_block_to_comboBox_list)  # (self.textbox1, self.textbox2, self.textbox3)

        self.to_file_addButton.clicked.connect(self.add_to_file_csv)  # (self.textbox1, self.textbox2, self.textbox3)

        # combo box with selected products and quantities
        self.comboBox_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.comboBox_list.setMinimumContentsLength(15)
        #         self.comboBox_list.setEditable(True)
        # self.comboBox_list.addItem('')  # add empty string
        # CHOICE
        self.comboBox_list.activated.connect(self.edit_block)

        # REMOVE BUTTON
        self.removeButton.clicked.connect(self.remove_block)

        # checkBoxes to choice the report
        self.checkBox_group.addButton(self.checkBox_report_1)
        self.checkBox_group.addButton(self.checkBox_report_2)
        self.checkBox_group.addButton(self.checkBox_report_3)
        self.checkBox_group.addButton(self.checkBox_report_4)

        # GET REPORT BUTTON
        self.reportButton.clicked.connect(self.get_report)

        self.report_info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # self.report_info_label.setStyleSheet(f'color: green')
        # self.report_info_label.setText('ВЫВОД: нет')

        # EXIT BUTTON
        self.exitButton.clicked.connect(self.exit_app)
        #         self.exitButton.clicked.connect(QCoreApplication.instance().quit)

        hbox = QHBoxLayout()
        hbox.addWidget(self.combo_box_label)
        hbox.addWidget(self.comboBox)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.label1)
        hbox1.addWidget(self.textbox1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.label2)
        hbox2.addWidget(self.textbox2)

        hbox22 = QHBoxLayout()
        hbox22.addWidget(self.label22)
        hbox22.addWidget(self.textbox22)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.label3)
        hbox3.addWidget(self.textbox3)

        hbox_list = QHBoxLayout()
        hbox_list.addWidget(self.label_list)
        hbox_list.addWidget(self.comboBox_list)

        vbox = QVBoxLayout()
        vbox.addWidget(self.info_label)  # widget with selected data_name
        vbox.addLayout(hbox)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox22)
        vbox.addLayout(hbox3)
        vbox.addWidget(self.addButton)
        vbox.addWidget(self.to_file_addButton)
        vbox.addLayout(hbox_list)  # widget with list selected data_names (blocks)
        vbox.addWidget(self.removeButton)

        vbox.addWidget(self.checkBox_report_1)
        vbox.addWidget(self.checkBox_report_2)
        vbox.addWidget(self.checkBox_report_3)
        vbox.addWidget(self.checkBox_report_4)

        vbox.addWidget(self.reportButton)

        vbox.addWidget(self.progress_bar)

        vbox.addWidget(self.report_info_label)

        vbox.addWidget(self.exitButton)

        # Set layout
        self.setLayout(vbox)

        self.show()

    # ----------------------------------------------------------------
    # functions for loading data

    def _set_info_label(self):
        self.info_label.setStyleSheet(f'color:{self.color};')
        self.info_label.setText(self.msg)
        # print(f'Hi from _set_info_label! msg = {self.msg}')

    def _refresh_comboBox(self):  # refresh loaded list of products under SEARCH
        self.comboBox.clear()
        self.comboBox.addItem('Обновить поиск')
        if self.data_search is not None and self.data_search.shape[0] == 1:
            self.data_search = self.data
        if self.data_search is not None and not self.data_search.empty:
            for row in range(len(self.data_search.index)):
                self.comboBox.addItem(str(self.data_search.iloc[row, 0]))

    def _search_by_column_product_names(self):  # DF with data for comboBox
        # self.data_search instead self.data to provide search in small DF (search by several keys)
        if self.data_search is not None:
            # self.comboBox.currentText() is empty str (and self.data_search = self.data) after initialization -->
            # so self.data_search = self.data_search = self.data  (empty str in every data str)
            self.data_search = self.data_search.loc[
                self.data_search[COLUMN_PRODUCT_NAMES].str.find(str(self.comboBox.currentText())) != -1]
            self.msg = f"Количество найденных результатов: {self.data_search.shape[0]}"
            return self.data_search.loc[self.data_search[COLUMN_PRODUCT_NAMES] == self.comboBox.currentText()]
        else:
            return None
            # good info print
            # print(self.data_search.shape, self.data_search.shape[0], len(self.data_search.index), self.data_search.index)

    def _get_value_info_label(self, combo_idx, search_result):

        if self.data_search is None:
            self.color = 'red'
            self.msg = "Файл не найден или пуст"

        # self.msg stated in func _search_by_column_product_names
        elif self.data_search.shape[0] > 1:
            self.textbox1.setText('')
            self.textbox2.setText('')
            self.textbox22.setText('')
            self.color = 'green'
            if not search_result.empty:  # key_string in list of products
                self.textbox1.setText(search_result.iloc[0][COLUMN_PRODUCT_NAMES])
                self.textbox2.setText(search_result.iloc[0][COLUMN_DICT_OF_MODULS])
                self.textbox22.setText(search_result.iloc[0][COLUMN_DICT_OF_COMPONENTS])
                self.textbox3.setValue(1)
        elif self.data_search.shape[0] == 1:
            self.textbox1.setText(self.data_search.iloc[0][COLUMN_PRODUCT_NAMES])
            self.textbox2.setText(self.data_search.iloc[0][COLUMN_DICT_OF_MODULS])
            self.textbox22.setText(self.data_search.iloc[0][COLUMN_DICT_OF_COMPONENTS])
            self.textbox3.setValue(1)
            self.color = 'green'

        # 0 results were found
        else:
            # if new string, it automatically adds to the comboBox with text and index, and combo_idx = last idx
            self.msg, self.color = (
                'Поиск обновлен', 'blue') if combo_idx == 0 else (
                "Выбранная строка не найдена", 'red')
            self.textbox1.setText('')
            self.textbox2.setText('')
            self.textbox22.setText('')
            self.data_search = self.data

    def update_info_label(self):
        combo_idx = self.comboBox.currentIndex()
        search_result = self._search_by_column_product_names()  # type DataFrame
        self._get_value_info_label(combo_idx, search_result)  # + set text in input fields
        self._refresh_comboBox()
        self._set_info_label()

    # --------------------- LIST for report and ADD to file

    def _refresh_comboBox_list(self):
        self.comboBox_list.clear()
        i = 0  # index is comboBox_list Index
        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, q-ty moduls, idx]
        # for k, v in self.block_list_dict.items():
        #     self.comboBox_list.addItem(f'{v[1]}  {k}')
        #     self.block_list_dict[k] = [v[0], v[1], i]
        #     i += 1

        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, dict_e_components, q-ty moduls, idx]
        for k, v in self.block_list_dict.items():
            self.comboBox_list.addItem(f'{v[2]}  {k}')
            self.block_list_dict[k] = [v[0], v[1], v[2], i]
            i += 1

    # !!!!!!!!!!!!!! FIX class Validator !!!!!!!!!!
    def _validate_data(self):
        # need to fix eval() - forbid (+ - * ** /) from str
        # print(self.textbox2.toPlainText())
        # print(list(self.textbox2.toPlainText()))
        # print(repr(self.textbox2.toPlainText()))
        # print(type(self.textbox2.toPlainText()))

        # dict_validator_flag, self.msg, block_name = Validator(
        #     self.textbox2.toPlainText(), self.textbox1.displayText()).validate()
        dict_validator_flag, self.msg, block_name, moduls_dict_str, components_dict_str = Validator(
            self.textbox1.displayText(),
            self.textbox2.toPlainText(),
            self.textbox22.toPlainText()).validate()
        if dict_validator_flag:
            self.textbox1.setText(block_name)
            # self.textbox2.setText(self.msg)
            self.textbox2.setText(moduls_dict_str)
            self.textbox22.setText(components_dict_str)
        return dict_validator_flag

    # ADD product to list of products (dict with indexes for combobox) and add to comboBox_list
    def add_block_to_comboBox_list(self):  # self.block_list_dict = {} at the start
        if self._validate_data():
            # self.block_list_dict[self.textbox1.displayText()] = [
            #     eval(self.textbox2.toPlainText()),
            #     self.textbox3.value()]  # idx will be added under _refresh_comboBox_list
            self.block_list_dict[self.textbox1.displayText()] = [
                eval(self.textbox2.toPlainText()),
                eval(self.textbox22.toPlainText()),
                self.textbox3.value()]  # idx will be added under _refresh_comboBox_list
            self._refresh_comboBox_list()
            self.msg += f'\n\nДобавлено в список блоков для отчета: ' \
                        f'{self.textbox1.displayText()}\n{self.textbox3.value()} шт.'
            self.color = 'green'
        else:
            self.color = 'red'

        self._set_info_label()  # self.msg from validation

    def add_to_file_csv(self):
        if self._validate_data():

            add_df = pd.DataFrame({
                COLUMN_PRODUCT_NAMES: [self.textbox1.displayText()],
                COLUMN_DICT_OF_MODULS: [self.textbox2.toPlainText()],
                COLUMN_DICT_OF_COMPONENTS: [self.textbox22.toPlainText()],
            })

            if (
                    self.data_search is not None and
                    self.textbox1.displayText() not in self.data_search[COLUMN_PRODUCT_NAMES].to_list()
            ):
                self.msg, self.color = DataReader(
                    self.path_to_file,
                    self.file_name).add_to_file_csv(add_df)
                self.data = pd.concat([self.data, add_df], ignore_index=True).sort_values(by=COLUMN_PRODUCT_NAMES,
                                                                                          ascending=False)
                self.data_search = self.data
            else:
                self.color = 'orange'
                self.msg = 'Уже есть. Нужно изменить название'
        else:
            self.color = 'red'

        self._set_info_label()

    def edit_block(self):
        combo_idx = self.comboBox_list.currentIndex()
        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, q-ty moduls, idx]
        # for k, v in self.block_list_dict.items():
        #     if v[2] == combo_idx:
        #         self.textbox1.setText(k)
        #         self.textbox2.setText(f'{v[0]}')  # set to str-type, not dict-type
        #         self.textbox3.setValue(v[1])

        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, dict_e_components, q-ty moduls, idx]
        for k, v in self.block_list_dict.items():
            if v[3] == combo_idx:
                self.textbox1.setText(k)
                self.textbox2.setText(f'{v[0]}')  # set to str-type, not dict-type
                self.textbox22.setText(f'{v[1]}')  # set to str-type, not dict-type
                self.textbox3.setValue(v[2])

    def remove_block(self):
        combo_idx = self.comboBox_list.currentIndex()
        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, q-ty moduls, idx]
        # for k, v in self.block_list_dict.items():
        #     if v[2] == combo_idx:
        #         self.block_list_dict.pop(k)
        #         self.msg = f'{k} удален из списка.'
        #         break

        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, dict_e_components, q-ty moduls, idx]
        for k, v in self.block_list_dict.items():
            if v[3] == combo_idx:
                # print(self.block_list_dict)
                self.block_list_dict.pop(k)
                # print(self.block_list_dict)
                self.msg = f'{k} удален из списка.'
                break
        self._refresh_comboBox_list()
        self.color = 'green'
        self._set_info_label()

    # ----------------------------------------------

    def make_dict_for_report(self):
        self.progress_bar.setValue(5)
        # print(self.block_list_dict)
        result = DictMaker(self.block_list_dict).make_report_dict() if self.block_list_dict else {}  # None
        return result

    def read_modul_from_stock_file(self):
        self.modul_stock_isRead = True
        sheet_name = 'Склад модулей(узлов)'
        cols = 'C,F,G'
        self.modul_df, self.msg, self.color = DataReader(
            PATH_TO_FILE_STOCK, FILE_STOCK).read_modul_from_stock_file(sheet_name, cols)
        self.progress_bar.setValue(10)
        self._set_info_label()

    @staticmethod
    def _get_column_list(moduls_dict):
        # Works with sheet_name = 'СП_плат'
        col_moduls_dict = dict([((k + 9), v) for k, v in moduls_dict.items()])
        list_of_columns = [1, 2, 3, 4, 5, 6, 7, 8]
        list_of_columns.extend(col_moduls_dict.keys())
        return list_of_columns, col_moduls_dict

    def compose_report_1(self, dict_for_report):
        """
        :param dict_for_report:
        :return: dict and DF with bad balance moduls (art of modul -- q-ty)
        """
        report_dict, report_df, quantity_min, not_found = ReportMaker(dict_for_report, self.modul_df).make_report_1()

        self.report_info_label.setStyleSheet(f'color:{self.color};')
        self.report_info_label_text = ''
        if not_found:
            self.report_info_label_text += f'{not_found} - этих модулей (артикулов) НЕТ на складе "СП_плат"!!! \n'
        self.report_info_label_text += f'Модулей на складе достаточно для изготовления {quantity_min} заказов. \n'
        self.report_info_label.setText(self.report_info_label_text)

        self.progress_bar.setValue(20)
        if report_df.empty:
            # return None, None
            return {}, report_df
        return report_dict, report_df

    def compose_report_2(self, dict_for_report):
        """

        :param dict_for_report:
        :return: bad balance components (not including elements from components dict)
        """
        # if dict_for_report != self.old_dict_for_report:
        bad_balance_report_dict, bad_balance_report_df = self.compose_report_1(dict_for_report)
        # else:
        #     bad_balance_report_dict = self.old_dict_for_report

        # print(f'bad_balance_report_df.empty = {bad_balance_report_df.empty}')
        if bad_balance_report_df.empty:
            print("Hi from empty")
            return {}, bad_balance_report_df
        else:
            # cols, col_moduls_dict = self._get_column_list(bad_balance_report_dict)
            self.msg = f'ЖДИТЕ!!! Читается БОЛЬШОЙ файл!'
            self.color = 'blue'
            self._set_info_label()
            self.progress_bar.setValue(25)

            cols, col_moduls_dict = self._get_column_list(bad_balance_report_dict)
            sheet_name = 'СП_плат'
            big_bom_df, self.msg, self.color = DataReader(
                PATH_TO_FILE_STOCK, FILE_STOCK).read_bom_from_stock_file(sheet_name, cols)
            print(f'msg from report2 {self.msg}')
            self.report_info_label_text += f'НЕТ СОСТАВА атикулы модулей: {self.msg}\n'

        self._set_info_label()
        self.progress_bar.setValue(80)
        report_dict, report_df = ReportMaker(col_moduls_dict, big_bom_df).make_report_2()
        dificit = report_df[['Артикул', 'Unnamed: 3', 'Unnamed: 4',
                             'Склад основной', 'sum_components',
                             'quantity', 'balance']][report_df['balance'] < 0]

        # proficit = report_df[['Артикул', 'Unnamed: 3', 'Unnamed: 4',
        #                       'Склад основной', 'sum_components',
        #                       'quantity', 'balance']][report_df['balance'] >= 0]
        #
        quantity_min = report_df['quantity'].min()

        self.report_info_label.setStyleSheet(f'color:{self.color};')
        # self.report_info_label_text = ''
        self.report_info_label_text += f'Компонентов на складе достаточно для изготовления {quantity_min} заказов. '
        self.report_info_label.setText(self.report_info_label_text)

        return None, dificit

    # def inner_func_for_label(self):
    #     self.msg = f'ЖДИТЕ!!! Читается БОЛЬШОЙ файл - страница СП_плат!'
    #     self.color = 'blue'
    #     self._set_info_label()
    #     self.progress_bar.setValue(20)

    def compose_report_3(self, dict_for_report):
        """
        BOM without elements from components dict
        :param dict_for_report:
        :return:
        """
        self.report_info_label_text = ''
        notnull_report_df, null_report_df = ReportMaker(dict_for_report, self.modul_df).make_report_0()
        # print(f'notnull_report_df: {notnull_report_df}')
        notnull_report_dict = DictMaker().make_dict_from_modul_df(notnull_report_df, 'Артикул', 'moduls_in_order')
        null_report_dict = DictMaker().make_dict_from_modul_df(null_report_df, 'Артикул', 'moduls_in_order')
        not_found = list(null_report_dict.keys())

        if not_found:
            self.report_info_label_text += f'{not_found} - этих модулей (артикулов) НЕТ на складе "СП_плат"!!! \n'

        if notnull_report_df.empty:
            print("Hi from empty input dict")
            # ??? None?
            return {}, notnull_report_df
        else:

            self.msg = f'ЖДИТЕ!!! Читается БОЛЬШОЙ файл - страница СП_плат!'
            self.color = 'blue'
            self._set_info_label()
            self.progress_bar.setValue(20)
            cols, col_moduls_dict = self._get_column_list(notnull_report_dict)
            # print(cols)
            # print(col_moduls_dict)
            sheet_name = 'СП_плат'
            big_bom_df, self.msg, self.color = DataReader(
                PATH_TO_FILE_STOCK, FILE_STOCK).read_bom_from_stock_file(sheet_name, cols)
            # print(self.msg)
            self.report_info_label_text += f'НЕТ СОСТАВА атикулы модулей: {self.msg}\n'

        self._set_info_label()
        self.progress_bar.setValue(80)
        report_dict, report_df = ReportMaker(col_moduls_dict, big_bom_df).make_report_2()

        self.report_info_label.setStyleSheet(f'color:{self.color};')
        self.report_info_label.setText(self.report_info_label_text)

        return None, report_df[['Артикул', 'Unnamed: 3', 'Unnamed: 4',
                                 'Склад основной', 'sum_components',
                                 'quantity', 'balance']]

    def compose_report_4(self, dict_for_report):
        """
        bad balance for components in moduls
        :param dict_for_report:
        :return:
        """
        # self.report_info_label.setText('')
        a, report_df = self.compose_report_3(dict_for_report)
        if report_df.empty:
            self.report_info_label.setStyleSheet(f'color:{self.color};')
            self.report_info_label.setText(self.report_info_label_text)
            return None, None
        else:
            deficit = report_df[['Артикул', 'Unnamed: 3', 'Unnamed: 4',
                                 'Склад основной', 'sum_components',
                                 'quantity', 'balance']][report_df['balance'] < 0]

            quantity_min = report_df['quantity'].min()

            self.report_info_label.setStyleSheet(f'color:{self.color};')
            self.report_info_label_text += f'Компонентов на складе достаточно для изготовления {quantity_min} заказов. '
            self.report_info_label.setText(self.report_info_label_text)

            return None, deficit

    def get_report(self):

        if self.w is not None:
            self.w.close()
            self.w = None  # Discard reference to ReportWindow

        self.progress_bar.reset()
        self.report_info_label.setText('.....')

        if not self.modul_stock_isRead:
            self.read_modul_from_stock_file()

        dict_for_report = self.make_dict_for_report()
        if dict_for_report == self.old_dict_for_report:
            print('old_dict_for_report = dict_for_report')
            pass

        self.func_dict = {
            # self.checkBox_report_1: ReportMaker(dict_for_report, self.modul_df).make_report_1,
            self.checkBox_report_1: self.compose_report_1,
            self.checkBox_report_2: self.compose_report_2,
            self.checkBox_report_3: self.compose_report_3,
            self.checkBox_report_4: self.compose_report_4,
            # self.checkBox_report_2: ReportMaker(dict_for_report, self.modul_df).make_report_2
                          }
        report_name = self.report_name_dict.get(self.checkBox_group.checkedButton())
        if self.checkBox_group.checkedButton() and dict_for_report and self.modul_df is not None:
            report_dict, report_df = self.func_dict[self.checkBox_group.checkedButton()](dict_for_report)

            print(f'report_dict = {report_dict}')
            print(f'report_df = {report_df}')

            self.msg = f'Обработан отчёт: {report_name}.'
            self.color = 'green'
        else:
            self.msg = 'Блоки не заданы' if report_name else 'Отчет не выбран'
            self.color = 'red'
            report_dict, report_df = None, None

        self.progress_bar.setValue(100)
        self._set_info_label()

        self.old_dict_for_report = dict_for_report

        # REPORT WINDOW
        if report_df is not None and not report_df.empty and report_name:
            self.w = ReportWindow(report_name, report_df)
            self.w.show()

    def exit_app(self):
        sys.exit()

# -------------------------------------------------------------------------
# !!!!!!!   RUN  !!!!!!
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = MyApp()
#     #     ex.show()
#     sys.exit(app.exec_())
