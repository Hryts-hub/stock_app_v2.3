#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict

import pandas as pd
# to disable warnings
# pd.options.mode.chained_assignment = None  # default='warn'

from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QSpinBox, QCheckBox, QButtonGroup, QProgressBar

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
    """
    The main class.
    Class MyApp(QWidget) generates the main window of the application
    with input fields, buttons and result labels.

    BLOCK consist of MODULES and COMPONENTS (or just MODULES, or just COMPONENTS).
    MODUL consist of COMPONENTS.

    The report could be given for modules or components in modules AND for all components in block
    """

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

        self.label22 = QLabel(f'{COLUMN_DICT_OF_COMPONENTS}:', self)
        self.textbox22 = QTextEdit(self)

        self.label3 = QLabel('количество блоков:', self)
        self.textbox3 = QSpinBox()
        self.textbox3.setMinimum(1)
        self.textbox3.setMaximum(1000)

        self.addButton = QPushButton("Добавить в список")
        self.to_file_addButton = QPushButton("Добавить в файл ")

        self.label_list = QLabel("Выбранные блоки:")
        self.comboBox_list = QComboBox()

        self.removeButton = QPushButton("Убрать из списка")

        self.report_0_name = 'Report_0: существующие модули'
        self.report_1_name = 'Report_1: недостающие модули в блоках'
        self.report_2_name = 'Report_2: недостающие компоненты недостающих модулей'
        self.report_3_name = 'Report_3: BOM компонетов из модулей'
        self.report_4_name = 'Report_4: отрицательный баланс по компонентам из BOM'
        self.report_5_name = 'Report_5: BOM по всем компонентам + цены'
        self.report_6_name = 'Report_6: отрицательный баланс по всем компонентам + цены'
        self.report_7_name = 'Report_7: отрицательный баланс по недостающим компонентам недостающих модулей + цены'

        self.checkBox_report_0 = QCheckBox(self.report_0_name)
        self.checkBox_report_1 = QCheckBox(self.report_1_name)
        self.checkBox_report_2 = QCheckBox(self.report_2_name)
        self.checkBox_report_3 = QCheckBox(self.report_3_name)
        self.checkBox_report_4 = QCheckBox(self.report_4_name)
        self.checkBox_report_5 = QCheckBox(self.report_5_name)
        self.checkBox_report_6 = QCheckBox(self.report_6_name)
        self.checkBox_report_7 = QCheckBox(self.report_7_name)

        self.func_dict = {}  # {key=self.checkBox_report_N: val=ReportMaker(report_dict, DF).make_report_N}
        self.report_name_dict = {self.checkBox_report_0: self.report_0_name,
                                 self.checkBox_report_1: self.report_1_name,
                                 self.checkBox_report_2: self.report_2_name,
                                 self.checkBox_report_3: self.report_3_name,
                                 self.checkBox_report_4: self.report_4_name,
                                 self.checkBox_report_5: self.report_5_name,
                                 self.checkBox_report_6: self.report_6_name,
                                 self.checkBox_report_7: self.report_7_name,
                                 }

        self.checkBox_group = QButtonGroup()

        self.reportButton = QPushButton("Получить отчет")

        self.progress_bar = QProgressBar(self)

        self.report_info_label = QLabel()
        self.report_info_label_text = ''

        self.exitButton = QPushButton("Выйти")

        self.block_list_dict = {}  # comboBox dict
        self.old_dict_for_report = defaultdict(dict)
        self.cache_reports_dict = defaultdict(dict)

        self.modul_df = None
        self.stock_df = None

        self.initUI()

    def initUI(self):

        # Set window properties
        self.setWindowTitle("Приложение СКЛАД")
        self.setMinimumWidth(700)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._search_by_column_product_names()  # get msg and data for comboBox (<==self.data_search DF)

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

        # ADD BUTTONS
        # (self.textbox1, self.textbox2, self.textbox22, self.textbox3)
        self.addButton.clicked.connect(self.add_block_to_comboBox_list)

        self.to_file_addButton.clicked.connect(self.add_to_file_csv)

        # combo box with selected products and quantities
        self.comboBox_list.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.comboBox_list.setMinimumContentsLength(15)

        # EDIT CHOICE
        self.comboBox_list.activated.connect(self.edit_block)

        # REMOVE BUTTON
        self.removeButton.clicked.connect(self.remove_block)

        # checkBoxes to choice the report
        self.checkBox_group.addButton(self.checkBox_report_0)
        self.checkBox_group.addButton(self.checkBox_report_1)
        # self.checkBox_group.addButton(self.checkBox_report_2)
        # self.checkBox_group.addButton(self.checkBox_report_3)
        # self.checkBox_group.addButton(self.checkBox_report_4)
        self.checkBox_group.addButton(self.checkBox_report_5)
        self.checkBox_group.addButton(self.checkBox_report_6)
        self.checkBox_group.addButton(self.checkBox_report_7)

        # GET REPORT BUTTON
        self.reportButton.clicked.connect(self.get_report)

        self.report_info_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # EXIT BUTTON
        self.exitButton.clicked.connect(self.exit_app)

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

        vbox.addWidget(self.checkBox_report_0)
        vbox.addWidget(self.checkBox_report_1)
        # vbox.addWidget(self.checkBox_report_2)
        # vbox.addWidget(self.checkBox_report_3)
        # vbox.addWidget(self.checkBox_report_4)
        vbox.addWidget(self.checkBox_report_5)
        vbox.addWidget(self.checkBox_report_6)
        vbox.addWidget(self.checkBox_report_7)

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
        """
        Set color (self.color) and text (self.msg) of info label
        :return: None
        """
        self.info_label.setStyleSheet(f'color:{self.color};')
        self.info_label.setText(self.msg)

    def _refresh_comboBox(self):  # refresh loaded list of products under SEARCH
        """
        The data from csv-file filed to the comboBox.
        After entering search-string or selecting string the comboBox contains search result: rows with search_string.
        If NO results were found or just 1, the comboBox will be returned to the initial state (data from csv-file).
        :return: None
        """
        self.comboBox.clear()
        self.comboBox.addItem('Обновить поиск')
        if self.data_search is not None and self.data_search.shape[0] == 1:
            self.data_search = self.data
        if self.data_search is not None and not self.data_search.empty:
            for row in range(len(self.data_search.index)):
                self.comboBox.addItem(str(self.data_search.iloc[row, 0]))

    def _search_by_column_product_names(self):
        """
        The text in input field of comboBox is search-string.
        If block-name contains search-string, the block added to the self.data_search (DF with result of search).
        ComboBox filed by data from small DF, and search by another search-string can be provided.
        The message updated with count of search result.
        If NO results were found, the None returned.
        :return: DF with data for comboBox or None
        """
        # self.data_search instead self.data to provide search in small DF (search by several keys)
        if self.data_search is not None:
            # after initialization self.comboBox.currentText() is empty str (and self.data_search = self.data) -->
            # so self.data_search = self.data  (empty str in every data str)
            self.data_search = self.data_search.loc[
                self.data_search[COLUMN_PRODUCT_NAMES].str.find(str(self.comboBox.currentText())) != -1]
            self.msg = f"Количество найденных результатов: {self.data_search.shape[0]}"
            return self.data_search.loc[self.data_search[COLUMN_PRODUCT_NAMES] == self.comboBox.currentText()]
        else:
            return None

    def _get_value_info_label(self, combo_idx, search_result):
        """
        Updates message with count of founded results.
        Files input fields with data from search:
            empty - if NO results or several results
            search-string - if exactly search-string was found
        :param combo_idx: int
        :param search_result: DF
        :return: None
        """

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
        """
        The main function.
        Provides search, updating info label, comboBox and input fields.
        :return: None
        """

        combo_idx = self.comboBox.currentIndex()
        search_result = self._search_by_column_product_names()  # type DataFrame
        self._get_value_info_label(combo_idx, search_result)  # + set text in input fields
        self._refresh_comboBox()
        self._set_info_label()

    # --------------------- LIST for report and ADD to file

    def _refresh_comboBox_list(self):
        self.comboBox_list.clear()
        i = 0  # index is comboBox_list Index

        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, dict_e_components, q-ty moduls, idx]
        for k, v in self.block_list_dict.items():
            self.comboBox_list.addItem(f'{v[2]}  {k}')
            self.block_list_dict[k] = [v[0], v[1], v[2], i]
            i += 1

    # !!!!!!!!!!!!!! FIX class Validator !!!!!!!!!!
    def _validate_data(self):
        # need to fix eval() - forbid (+ - * ** /) from str
        # print(repr(self.textbox2.toPlainText()))

        dict_validator_flag, self.msg, block_name, moduls_dict_str, components_dict_str = Validator(
            self.textbox1.displayText(),
            self.textbox2.toPlainText(),
            self.textbox22.toPlainText()).validate()
        if dict_validator_flag:
            self.textbox1.setText(block_name)
            self.textbox2.setText(moduls_dict_str)
            self.textbox22.setText(components_dict_str)
        return dict_validator_flag

    # ADD product to list of products (dict with indexes for combobox) and add to comboBox_list
    def add_block_to_comboBox_list(self):  # self.block_list_dict = {} at the start
        if self._validate_data():
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
        """
        After validation the name and dictionaries of modules and components are written to the csv file.
        Block data appears in csv file and comboBox (can be selected from comboBox).
        If this block already in the file, the message in info label informs about it.
        The existing file info can not be changed, only supplemented by a new rows.
        :return: None
        """
        if self._validate_data():

            add_df = pd.DataFrame({
                COLUMN_PRODUCT_NAMES: [self.textbox1.displayText()],
                COLUMN_DICT_OF_MODULS: [self.textbox2.toPlainText()],
                COLUMN_DICT_OF_COMPONENTS: [self.textbox22.toPlainText()],
            })

            if (
                    self.data_search is not None and
                    self.textbox1.displayText() not in self.data_search[COLUMN_PRODUCT_NAMES].to_list()
            ) or self.data_search is None:
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
        """
        To edit your choice, select block.
        It (name, dicts of moduls and components, quantity of blocks) appears in input fields.
        :return: None
        """
        combo_idx = self.comboBox_list.currentIndex()

        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, dict_e_components, q-ty moduls, idx]
        for k, v in self.block_list_dict.items():
            if v[3] == combo_idx:
                self.textbox1.setText(k)
                self.textbox2.setText(f'{v[0]}')  # set to str-type, not dict-type
                self.textbox22.setText(f'{v[1]}')  # set to str-type, not dict-type
                self.textbox3.setValue(v[2])

    def remove_block(self):
        """
        To delete your choice from comboBox for report,
        select block and push REMOVE button.
        Selected block removed from self.block_list_dict.items() and self.comboBox_list,
        and can't be used for report.
        The message in info_label informs name of the removed block.
        :return: None
        """
        combo_idx = self.comboBox_list.currentIndex()

        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, dict_e_components, q-ty moduls, idx]
        for k, v in self.block_list_dict.items():
            if v[3] == combo_idx:
                self.block_list_dict.pop(k)
                self.msg = f'{k} удален из списка.'
                break
        self._refresh_comboBox_list()
        self.color = 'green'
        self._set_info_label()

    # ----------------------------------------------

    def make_dict_for_report(self):
        self.progress_bar.setValue(5)
        result = DictMaker(self.block_list_dict).make_report_dict() if self.block_list_dict else {}  # None
        return result

    def read_modul_from_stock_file(self):
        sheet_name = 'Склад модулей(узлов)'
        cols = 'C,F,G'
        self.modul_df, self.msg, self.color = DataReader(
            PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols)
        self.modul_df = self.modul_df.iloc[2:]
        self.progress_bar.setValue(10)
        self._set_info_label()

    @staticmethod
    def _get_column_list(moduls_dict):
        # Works with sheet_name = 'СП_плат'
        col_moduls_dict = dict([((k + 9), v) for k, v in moduls_dict.items()])
        list_of_columns = [1, 2, 3, 4, 5, 6, 7, 8]
        list_of_columns.extend(col_moduls_dict.keys())
        return list_of_columns, col_moduls_dict

    def compose_report_0(self):
        """

        :return: dict and DF with bad balance moduls (art of modul -- q-ty)
        """

        dict_for_report = self.make_dict_for_report()

        notnull_report_df, null_df = ReportMaker(self.modul_df).make_report_0(dict_for_report)

        null_report_dict = DictMaker().make_dict_from_df(null_df, 'Артикул', 'q-ty')
        not_found = list(null_report_dict.keys())

        if not_found:
            info_text = f'{not_found} - этих модулей (артикулов) НЕТ на складе "СП_плат"!!! \n'
        else:
            info_text = 'Все модули указаны корректно. \n'
        self.report_info_label.setStyleSheet(f'color:{self.color};')
        self.report_info_label_text = info_text
        self.report_info_label.setText(info_text)
        self.progress_bar.setValue(10)

        self.cache_reports_dict[self.report_0_name] = (notnull_report_df, info_text)

    def compose_report_1(self):
        """

        :return: dict and DF with bad balance moduls (art of modul -- q-ty)
        """

        if not self.cache_reports_dict[self.report_0_name]:
            self.compose_report_0()

        notnull_report_df, info_text = self.cache_reports_dict[self.report_0_name]

        (
            report_dict,
            report_df,
            quantity_min,
            good_balance   # good_balance_dict.keys()
        ) = ReportMaker(notnull_report_df).make_report_1()

        info_text += f'Модулей на складе достаточно для изготовления {quantity_min} заказов. \n'

        if good_balance:
            info_text += f'Артикулы модулей, которых достаточно для изготовления: \n'
            for art_modul in good_balance:
                info_text += f' {art_modul},'
            info_text = info_text[:-1]
            info_text += '\n'
        self.report_info_label.setText(info_text)
        self.report_info_label_text = info_text

        self.progress_bar.setValue(20)
        self.cache_reports_dict[self.report_1_name] = (report_df, info_text)

    def read_sp_plat(self, report_df, info_text, report_dict):
        if report_df.empty:
            self.cache_reports_dict[self.report_3_name] = (report_df, info_text)
            return None
        else:
            self.msg = f'ЖДИТЕ!!! Читается БОЛЬШОЙ файл!'
            self.color = 'blue'
            self._set_info_label()
            self.progress_bar.setValue(25)

            cols, col_moduls_dict = self._get_column_list(report_dict)
            sheet_name = 'СП_плат'
            big_bom_df, self.msg, self.color = DataReader(
                PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols)

            big_bom_df = big_bom_df.iloc[14:]
            big_bom_df.rename(columns={'Спецификация плат': 'Unnamed: 4'}, inplace=True)
            for col in range(8, big_bom_df.shape[1]):
                if big_bom_df.iloc[:, col].sum() == 0:
                    self.msg += f' {int(big_bom_df.iloc[:, [col]].columns[0].split(":")[-1]) - 9} '

            if self.color == 'red':
                self._set_info_label()
                self.report_info_label_text = info_text
                self.cache_reports_dict[self.report_3_name] = (None, info_text)
                return None
            else:
                if self.msg:
                    info_text += f'НЕТ СОСТАВА (артикулы модулей): {self.msg}\n'
                self.report_info_label.setStyleSheet(f'color:{self.color};')
                self.report_info_label_text = info_text
                self.report_info_label.setText(info_text)

                self.progress_bar.setValue(70)

                report_df = ReportMaker(big_bom_df).make_report_2(col_moduls_dict)
                return report_df

    def compose_report_2(self):
        """

        :return: bad balance components (not including elements from components dict)
        """

        if not self.cache_reports_dict[self.report_1_name]:
            self.compose_report_1()

        bad_balance_report_df, info_text = self.cache_reports_dict[self.report_1_name]
        bad_balance_report_dict = DictMaker().make_dict_from_df(bad_balance_report_df, 'Артикул', 'balance')

        report_df = self.read_sp_plat(bad_balance_report_df, info_text, bad_balance_report_dict)

        deficit_df = report_df[['Артикул', 'Unnamed: 3', 'Unnamed: 4',
                             'Склад основной', 'sum_components',
                             'Штук можно изготовить', 'balance']][report_df['balance'] < 0]

        proficit = report_df[['Артикул', 'balance']][report_df['balance'] >= 0]
        proficit_dict = DictMaker().make_dict_from_df(proficit, 'Артикул', 'balance')
        proficit_list = list(proficit_dict.keys())
        if proficit_list:
            info_text += f'Артикулы компонентов, которых достаточно для изготовления: \n'
            for art_modul in proficit_list:
                info_text += f' {art_modul},'
            info_text = info_text[:-1]
            info_text += '\n'

        quantity_min = report_df['Штук можно изготовить'].min()

        self.report_info_label.setStyleSheet(f'color:{self.color};')
        info_text += f'Компонентов на складе достаточно для изготовления {quantity_min} заказов. \n'
        self.report_info_label.setText(info_text)
        self.report_info_label_text = info_text

        self.progress_bar.setValue(80)

        self.cache_reports_dict[self.report_2_name] = (deficit_df, info_text)

    def compose_report_3(self):
        """
        BOM without elements from components dict
        :return:
        """

        if not self.cache_reports_dict[self.report_0_name]:
            self.compose_report_0()

        notnull_report_df, info_text = self.cache_reports_dict[self.report_0_name]

        notnull_report_dict = DictMaker().make_dict_from_df(notnull_report_df, 'Артикул', 'q-ty')

        report_df = self.read_sp_plat(notnull_report_df, info_text, notnull_report_dict)

        info_text = self.report_info_label_text

        report_df = report_df[['Артикул', 'Unnamed: 3', 'Unnamed: 4',
                                 'Склад основной', 'sum_components',
                                 'Штук можно изготовить', 'balance']]

        self.cache_reports_dict[self.report_3_name] = (report_df, info_text)

    def compose_report_4(self):
        """
        bad balance for components in moduls

        :return:
        """

        if not self.cache_reports_dict[self.report_3_name]:
            self.compose_report_3()

        report_df, info_text = self.cache_reports_dict[self.report_3_name]

        if report_df is None or report_df.empty:
            self.cache_reports_dict[self.report_4_name] = (report_df, info_text)
            return None
        else:
            report_df = report_df[['Артикул', 'Unnamed: 3', 'Unnamed: 4',
                                 'Склад основной', 'sum_components',
                                 'Штук можно изготовить', 'balance']][(report_df['balance'] < 0)]

            quantity_min = report_df['Штук можно изготовить'].min()

            self.report_info_label.setStyleSheet(f'color:{self.color};')
            info_text += f'Компонентов на складе достаточно для изготовления {quantity_min} заказов.\n'
            self.report_info_label.setText(info_text)
            self.report_info_label_text = info_text
            self.progress_bar.setValue(90)

            self.cache_reports_dict[self.report_4_name] = (report_df, info_text)

    def prepare_stock_df(self):
        cols = 'C, D, G, I, K'
        sheet_name = 'Склад'
        self.stock_df, self.msg, self.color = DataReader(
            PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols)

        self.stock_df = self.stock_df.iloc[12:]

        self.stock_df = self.stock_df.dropna(subset=['Артикул'])

        self.stock_df = self.stock_df.astype({'Артикул': int})

        self.stock_df[['Склад основной', 'Цена, $']] = self.stock_df[['Склад основной', 'Цена, $']].fillna(0)

        for val in self.stock_df['Склад основной'].values:
            self.stock_df.loc[self.stock_df['Склад основной'] == val, 'Склад основной'] = 0 if (
                not str(val).replace(',', '').isdigit()) else val

        for val in self.stock_df['Цена, $'].values:
            self.stock_df.loc[self.stock_df['Цена, $'] == val, 'Цена, $'] = 0 if (
                    str(val).isspace() or str(val) == '') else val

        self.stock_df['Цена, EURO'] = 0  # None

        for val in self.stock_df['Цена, $'].values:
            if str(val).lower().find('e') != -1 or str(val).lower().find('е') != -1:
                self.stock_df.loc[self.stock_df['Цена, $'] == val, 'Цена, $'] = 0
                self.stock_df.loc[self.stock_df['Цена, $'] == val, 'Цена, EURO'] = str(val).replace(',', '.').strip()[:-1]

        self.stock_df[['Склад основной', 'Цена, $', 'Цена, EURO']] = self.stock_df[[
            'Склад основной', 'Цена, $', 'Цена, EURO']].astype(float)

    def calculate_price(self, components_from_modules_df, info_text):

        components_from_modules_dict = DictMaker().make_dict_from_df(
            components_from_modules_df,
            'Артикул',
            'sum_components'
        )

        components_from_block_dict = DictMaker(
            self.block_list_dict).make_component_report_dict() if self.block_list_dict else {}

        res_compo_dict = DictMaker(
            self.block_list_dict).make_big_report_dict(components_from_modules_dict, components_from_block_dict)

        compo_data = defaultdict(list)
        [compo_data['Артикул'].append(k) for k in res_compo_dict.keys()]
        [compo_data['quantity'].append(v) for v in res_compo_dict.values()]
        res_compo_df = pd.DataFrame.from_dict(compo_data)

        if self.stock_df is None:
            self.prepare_stock_df()

        report_stock_df = res_compo_df.merge(self.stock_df, how='left', on='Артикул')

        not_found_df = report_stock_df[report_stock_df['Название\n(Комплектующие склада)'].isnull()]
        not_found_dict = DictMaker().make_dict_from_df(not_found_df, 'Артикул', 'quantity')
        not_found = list(not_found_dict.keys())

        if not_found:
            info_text += f'НЕТ ИНФОРМАЦИИ по артикулам этих компонентов: {not_found} \n'
        else:
            info_text += 'Все компоненты указаны корректно. \n'

        report_stock_df['total $'] = report_stock_df['quantity'] * report_stock_df['Цена, $']
        report_stock_df['total EURO'] = report_stock_df['quantity'] * report_stock_df['Цена, EURO']

        dollar_price = round(report_stock_df['total $'].sum(), 2)
        euro_price = round(report_stock_df['total EURO'].sum(), 2)

        info_text += f'Цена = {dollar_price} $ + {euro_price} euro \n'

        null_df = report_stock_df[(report_stock_df['Цена, $'] == 0) & (report_stock_df['Цена, EURO'] == 0)]
        null_price_list = list(null_df['Артикул'])
        if null_price_list:
            info_text += f'НЕТ ЦЕНЫ для этих компонентов (артикулы): {null_price_list} \n'

        self.report_info_label_text = info_text

        self.report_info_label.setText(self.report_info_label_text)

        self.progress_bar.setValue(95)
        return report_stock_df

    def compose_report_5(self):

        if not self.cache_reports_dict[self.report_3_name]:
            self.compose_report_3()

        components_from_modules_df, info_text = self.cache_reports_dict[self.report_3_name]

        if components_from_modules_df is None or components_from_modules_df.empty:
            self.cache_reports_dict[self.report_5_name] = (components_from_modules_df, info_text)
            return None

        report_stock_df = self.calculate_price(components_from_modules_df, info_text)

        info_text = self.report_info_label_text

        self.cache_reports_dict[self.report_5_name] = (report_stock_df, info_text)

    def compose_report_6(self):

        if not self.cache_reports_dict[self.report_4_name]:
            self.compose_report_4()

        components_from_modules_df, info_text = self.cache_reports_dict[self.report_4_name]

        report_stock_df = self.calculate_price(components_from_modules_df, info_text)

        info_text = self.report_info_label_text

        self.cache_reports_dict[self.report_6_name] = (report_stock_df, info_text)

    def compose_report_7(self):

        if not self.cache_reports_dict[self.report_2_name]:
            self.compose_report_2()

        components_from_modules_df, info_text = self.cache_reports_dict[self.report_2_name]

        report_stock_df = self.calculate_price(components_from_modules_df, info_text)

        info_text = self.report_info_label_text

        self.cache_reports_dict[self.report_7_name] = (report_stock_df, info_text)

    def get_report(self):

        if self.w is not None:
            self.w.close()
            self.w = None  # Discard reference to ReportWindow

        self.progress_bar.reset()
        self.color = 'blue'
        self.report_info_label.setStyleSheet(f'color:{self.color};')
        self.report_info_label.setText('.....')

        if self.modul_df is None:
            self.read_modul_from_stock_file()

        input_str = str(self.block_list_dict)

        if input_str not in str(self.old_dict_for_report.keys()):
            self.report_info_label_text = f'{list(self.block_list_dict.keys())}'
            self.color = 'blue'
            self.report_info_label.setStyleSheet(f'color:{self.color};')
            self.old_dict_for_report.clear()
            self.cache_reports_dict.clear()

        self.func_dict = {
            self.checkBox_report_0: self.compose_report_0,
            self.checkBox_report_1: self.compose_report_1,
            self.checkBox_report_2: self.compose_report_2,
            self.checkBox_report_3: self.compose_report_3,
            self.checkBox_report_4: self.compose_report_4,
            self.checkBox_report_5: self.compose_report_5,
            self.checkBox_report_6: self.compose_report_6,
            self.checkBox_report_7: self.compose_report_7,
                          }

        report_name = self.report_name_dict.get(self.checkBox_group.checkedButton())

        if self.checkBox_group.checkedButton() and self.block_list_dict and self.modul_df is not None:

            if not (self.old_dict_for_report.keys() and self.old_dict_for_report[input_str][report_name]):
                self.color = 'blue'
                self.report_info_label.setStyleSheet(f'color:{self.color};')
                self.report_info_label.setText('..........')

                self.func_dict[self.checkBox_group.checkedButton()]()

                try:
                    self.old_dict_for_report[input_str] = self.cache_reports_dict
                except Exception as e:
                    print(e)

            if self.color == 'red':
                self.msg += f'\nОбработан отчёт: {report_name}.'
            else:

                self.msg = f'Обработан отчёт: {report_name}.'
                self.color = 'green'
            res_df, info_text = self.old_dict_for_report[input_str][report_name]

        else:
            self.msg = 'Блоки не заданы' if report_name else 'Отчет не выбран'
            self.color = 'red'
            info_text = self.msg
            res_df = None

        self.progress_bar.setValue(100)
        self._set_info_label()

        self.color = 'blue'
        self.report_info_label.setStyleSheet(f'color:{self.color};')
        self.report_info_label.setText(info_text)

        # REPORT WINDOW
        if res_df is not None and not res_df.empty and report_name:
            self.w = ReportWindow(report_name, res_df)
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
