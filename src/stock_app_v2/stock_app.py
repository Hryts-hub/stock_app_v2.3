#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime, date, time
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
# to disable warnings
# pd.options.mode.chained_assignment = None  # default='warn'

import ast

from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QSpinBox, QCheckBox, QButtonGroup, QProgressBar

from stock_app_v2.data_reader_class import DataReader
from stock_app_v2.dict_macker_class import DictMaker
from stock_app_v2.report_maker_class import ReportMaker
from stock_app_v2.report_window_class import ReportWindow
from stock_app_v2.validator_class import Validator
from stock_app_v2.func_library_class import FuncLibrary


FILE_STOCK = 'Склад 14.01.16.xlsx'

# .csv - file with names of products and dicts of moduls

# prod
FILE_OF_PRODUCTS = 'data.csv'
PATH_TO_FILE_OF_PRODUCTS = 'Z:/Склад/'
PATH_TO_FILE_STOCK = 'Z:/Склад/'

# dev
# FILE_OF_PRODUCTS = 'data_3_col.csv'
# PATH_TO_FILE_OF_PRODUCTS = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/'
# PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/stock_versions/stock_5044/'

# columns in this file = columns in data frame
COLUMN_PRODUCT_NAMES = 'наименование блока'
COLUMN_DICT_OF_MODULS = 'словарь модулей'
# !!!
COLUMN_DICT_OF_COMPONENTS = 'словарь эл.компонентов'


class MyApp(QWidget):
    """
    The main class.
    Class MyApp(QWidget) generates the main window of the application
    with input fields, buttons and result labels.

    BLOCK consists of MODULES and COMPONENTS (or just MODULES, or just COMPONENTS).
    MODUL consists of COMPONENTS.

    The report could be given for modules OR components in modules AND for all components in block
    (order of blocks)
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
        self.addButton.setStyleSheet('background: rgb(0,255,200);')  # green-mint
        self.to_file_addButton = QPushButton("Добавить в файл (не добавляйте мусорные, непроверенные данные!!!)")
        self.to_file_addButton.setStyleSheet('background: rgb(200,255,200);')  # green-light

        self.label_list = QLabel("Выбранные блоки:")
        self.comboBox_list = QComboBox()

        self.removeButton = QPushButton("Убрать из списка")
        self.removeButton.setStyleSheet('background: rgb(255,155,0);')  # orange

        # BOM - Bill Of Materials

        # Check               BOM                 Price     Stock Output
        # modules
        # existence
        # rep_0 --> rep_1 --> rep_2 -->           rep_7
        # rep_0 -->           rep_3 -->           rep_5
        # rep_0 -->           rep_3 --> rep_4 --> rep_6
        #                                                   rep_8 stock
        #                                                   rep_9 stock_dev
        #                                                   rep_10 stock+stock_dev

        self.report_0_name = 'Report_0 существующие модули'
        self.report_1_name = 'Report_1 недостающие модули в блоках'
        self.report_2_name = 'Report_2 недостающие компоненты недостающих модулей'
        self.report_3_name = 'Report_3 BOM (компонеты из модулей)'
        self.report_4_name = 'Report_4 недостающие компоненты из BOM (компонеты из модулей)'
        self.report_5_name = 'Report_5 BOM по всем компонентам + цены'
        self.report_6_name = 'Report_6 недостающие компоненты из BOM + цены'
        self.report_7_name = 'Report_7 недостающие компоненты недостающих модулей + цены'
        self.report_8_name = 'Report_8 Склад основной с датами последних поступлений'
        self.report_9_name = 'Report_9 Склад разработки (компоненты). Все столбцы с датами'

        self.checkBox_report_0 = QCheckBox(self.report_0_name)
        self.checkBox_report_1 = QCheckBox(self.report_1_name)
        self.checkBox_report_2 = QCheckBox(self.report_2_name)
        self.checkBox_report_3 = QCheckBox(self.report_3_name)
        self.checkBox_report_4 = QCheckBox(self.report_4_name)
        self.checkBox_report_5 = QCheckBox(self.report_5_name)
        self.checkBox_report_6 = QCheckBox(self.report_6_name)
        self.checkBox_report_7 = QCheckBox(self.report_7_name)
        self.checkBox_report_8 = QCheckBox(self.report_8_name)
        self.checkBox_report_9 = QCheckBox(self.report_9_name)

        self.checkBox_report_5.setStyleSheet("color: green")
        self.checkBox_report_8.setStyleSheet("color: darkgreen")
        self.checkBox_report_9.setStyleSheet("color: darkgreen")

        self.func_dict = {}  # {key=self.checkBox_report_N: val=ReportMaker(DF).make_report_N}

        self.report_name_dict = {self.checkBox_report_0: self.report_0_name,
                                 self.checkBox_report_1: self.report_1_name,
                                 self.checkBox_report_2: self.report_2_name,
                                 self.checkBox_report_3: self.report_3_name,
                                 self.checkBox_report_4: self.report_4_name,
                                 self.checkBox_report_5: self.report_5_name,
                                 self.checkBox_report_6: self.report_6_name,
                                 self.checkBox_report_7: self.report_7_name,
                                 self.checkBox_report_8: self.report_8_name,
                                 self.checkBox_report_9: self.report_9_name,
                                 }

        self.checkBox_group = QButtonGroup()

        self.reportButton = QPushButton("Получить отчет")
        #
        self.reportButton.setStyleSheet('background: rgb(0,255,0);')  # green

        self.stockButton = QPushButton("Склад + разраб.")
        self.stockButton.setStyleSheet('background: rgb(255,255,0);')  # yellow

        self.stock_modButton = QPushButton("Склад модулей(узлов)")
        self.stock_modButton.setStyleSheet('background: rgb(255,255,200);')  # light yellow

        self.progress_bar = QProgressBar(self)

        # the label with report info - output results and calculations
        self.report_info_label = QLabel()
        self.report_info_label_text = ''

        self.exitButton = QPushButton("Выйти")
        self.exitButton.setStyleSheet('background: rgb(255,200,200);')  # red-light

        # self.block_list_dict structure --> {k=modul_name: v=[dict_of_moduls, dict_of_components, q-ty of moduls, idx]
        # dict were key is a module name, and value is a list of input data
        self.block_list_dict = {}  # comboBox dict

        # Reports are cached on creation, and you can quickly retrieve an already calculated report.
        # If input data changed, the self.old_dict_for_report and self.cache_reports_dict are cleared.
        # This behavior easily can be changed to caching different input data but no need.

        # STRUCTURE -- {self.block_list_dict : [self.cache_reports_dict]}
        #               self.old_dict_for_report[input_str] = self.cache_reports_dict
        #               res_df, info_text = self.old_dict_for_report[input_str][report_name]
        #               res_df, info_text = self.cache_reports_dict[report_name]
        self.old_dict_for_report = defaultdict(dict)
        self.cache_reports_dict = defaultdict(dict)

        self.modul_df = None  # from stock file -- sheet_name = 'Склад модулей(узлов)', cols = 'C,F,G'
        self.stock_df = None  # from stock file -- sheet_name = 'Склад', cols = 'C, D, E, G, I, K, L, M, N, O, Q'
        self.stock_dev_df = None  # from stock file -- sheet_name = 'Скл.Р(компоненты)', all columns

        self.initUI()

    def initUI(self):

        # Set window properties
        self.setWindowTitle("Приложение СКЛАД")
        self.setMinimumWidth(800)
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
        self.checkBox_group.addButton(self.checkBox_report_2)
        self.checkBox_group.addButton(self.checkBox_report_3)
        self.checkBox_group.addButton(self.checkBox_report_4)
        self.checkBox_group.addButton(self.checkBox_report_5)
        self.checkBox_group.addButton(self.checkBox_report_6)
        self.checkBox_group.addButton(self.checkBox_report_7)
        self.checkBox_group.addButton(self.checkBox_report_8)
        self.checkBox_group.addButton(self.checkBox_report_9)

        # GET_REPORT BUTTON --> opens ReportWindow with report table (can be saved in excel file)
        # and shows report text in self.report_info_label
        self.reportButton.clicked.connect(self.get_report)
        self.stockButton.clicked.connect(self.get_stock)
        self.stock_modButton.clicked.connect(self.get_stock_mod)

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

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.reportButton)
        hbox_buttons.addWidget(self.stockButton)
        hbox_buttons.addWidget(self.stock_modButton)

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

        v1_box = QVBoxLayout()
        v1_box.addWidget(self.checkBox_report_0)
        v1_box.addWidget(self.checkBox_report_1)
        v1_box.addWidget(self.checkBox_report_2)
        v1_box.addWidget(self.checkBox_report_3)
        v1_box.addWidget(self.checkBox_report_4)
        # v1_box.addWidget(self.checkBox_report_5)
        # v1_box.addWidget(self.checkBox_report_6)
        # v1_box.addWidget(self.checkBox_report_7)

        v2_box = QVBoxLayout()
        v2_box.addWidget(self.checkBox_report_5)
        v2_box.addWidget(self.checkBox_report_6)
        v2_box.addWidget(self.checkBox_report_7)
        v2_box.addWidget(self.checkBox_report_8)
        v2_box.addWidget(self.checkBox_report_9)

        hbox_reports = QHBoxLayout()
        hbox_reports.addLayout(v1_box)
        hbox_reports.addLayout(v2_box)

        vbox.addLayout(hbox_reports)

        vbox.addLayout(hbox_buttons)

        vbox.addWidget(self.progress_bar)

        vbox.addWidget(self.report_info_label)

        vbox.addWidget(self.exitButton)

        # Set layout
        self.setLayout(vbox)

        self.show()

    # ----------------------------------------------------------------
    # functions for loading data (filling input fields and combo boxes)

    def _set_info_label(self):
        """
        Set color (self.color) and text (self.msg) of the main info label --- self.info_label
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
        ComboBox filed by data from small DF (self.data_search), and search by another search-string can be provided.
        The message updated with count of search results.
        If NO results were found, None returned.
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
        Fills input fields with data from search:
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
            # to search enter search_str into combo_idx input field --> self.data_search
            # this str automatically added to the comboBox with text and index, and combo_idx = last idx
            # if string has idx=0 (text = 'Обновить поиск' ) --> refresh search
            # if self.data_search.shape[0] == 0 and combo_idx != 0 --> NO results --> refresh search
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
        search_result = self._search_by_column_product_names()  # type is DataFrame or None
        self._get_value_info_label(combo_idx, search_result)  # + set text in input fields
        self._refresh_comboBox()
        self._set_info_label()

    # --------------------- LIST for report and ADD to file

    def _refresh_comboBox_list(self):
        """
        Fills self.comboBox_list with refreshed data from self.block_list_dict
        :return: None
        """
        self.comboBox_list.clear()
        i = 0  # comboBox_list Index

        # self.block_list_dict structure --> {k=modul_name: v=[dict_moduls, dict_components, q-ty moduls, idx]
        for k, v in self.block_list_dict.items():
            self.comboBox_list.addItem(f'{v[2]}  {k}')
            self.block_list_dict[k] = [v[0], v[1], v[2], i]
            i += 1

    # !!!!!!!!!!!!!! FIX class Validator !!!!!!!!!!
    def _validate_data(self):
        """
        Sends input data to the class Validator where function validate() cleans and transform input to correct usage.
        After validation, you need to check dicts for report!!!
        Some forms of input can't be accepted, and func returns False and recommendations in info label.
        :return: dict_validator_flag: Bool
        """
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
        """
        After validation correct data replace text in input fields.
        Combo box with blocks for report contains refreshed data.
        And info label informs about last actions.
        :return: None
        """
        if self._validate_data():
            self.block_list_dict[self.textbox1.displayText()] = [
                eval(self.textbox2.toPlainText()),
                eval(self.textbox22.toPlainText()),
                self.textbox3.value()]  # idx will be added under _refresh_comboBox_list
            self._refresh_comboBox_list()
            self.msg += f'\nДобавлено в список блоков для отчета: ' \
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
        To delete your choice from comboBox for report
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
                print(f'self.block_list_dict: {self.block_list_dict}')
                break
        self._refresh_comboBox_list()
        self.color = 'green'
        self._set_info_label()

    # ----------------------------------------------

    def make_dict_for_report(self):
        """
        Set value of progress_bar and gets dict using class DictMaker and func make_report_dict().
        This step in independent func because of progress_bar can be changed once in func,
        and control progress is the desired result.
        :return: dict
        """
        self.progress_bar.setValue(5)
        result = DictMaker(self.block_list_dict).make_report_dict() if self.block_list_dict else {}  # None
        return result

    def read_modul_from_stock_file(self):
        """
        Gets DF from excel file using class DataReader.
        In fanc sheet_name and cols are stated.
        Top rows from DF removed.
        Progress bar and message in info label are updated.
        :return: None
        """
        sheet_name = 'Склад модулей(узлов)'
        cols = 'C,F,G, H'  # col H added
        self.modul_df, self.msg, self.color = DataReader(
            PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols)

        if self.modul_df is not None and not self.modul_df.empty:
            self.modul_df = self.modul_df.iloc[2:]

        self.progress_bar.setValue(10)
        self._set_info_label()

    @staticmethod
    def _get_column_list(moduls_dict):
        """
        Works with sheet_name = 'СП_плат'.
        Forms columns for file reading for func read_sp_plat that used in rep_2 and rep_3.
        :param moduls_dict: dict
        :return: list_of_columns -> list, col_moduls_dict -> dict
        """

        col_moduls_dict = dict([((k + 9), v) for k, v in moduls_dict.items()])
        list_of_columns = [1, 2, 3, 4, 5, 6, 7, 8]
        list_of_columns.extend(col_moduls_dict.keys())
        return list_of_columns, col_moduls_dict

    def compose_report_0(self):
        """
        The base report.
        It checks modules existence.
        Result: DF with balance existing moduls (art of modul -- q-ty) and text with info messages
        :return: None
        """
        if self.modul_df is None:
            self.read_modul_from_stock_file()

        dict_for_report = self.make_dict_for_report()

        notnull_report_df, null_df, quantity_min, = ReportMaker(self.modul_df).make_report_0(dict_for_report)

        null_report_dict = DictMaker().make_dict_from_df(null_df, 'Артикул', 'q-ty')
        not_found = list(null_report_dict.keys())

        if not_found:
            info_text = f'{not_found} - этих модулей (артикулов) НЕТ на складе "СП_плат"!!! \n'
        else:
            info_text = 'Все модули указаны корректно. \n'

        info_text += f'Модулей на складе достаточно для изготовления {quantity_min} заказов. \n'

        self.report_info_label.setStyleSheet(f'color:{self.color};')
        self.report_info_label_text = info_text
        self.report_info_label.setText(info_text)
        self.progress_bar.setValue(10)

        self.cache_reports_dict[self.report_0_name] = (notnull_report_df, info_text)

    def compose_report_1(self):
        """
        Result: DF with bad balance moduls (art of modul -- q-ty) and text with info messages
        :return: None
        """

        if not self.cache_reports_dict[self.report_0_name]:
            self.compose_report_0()

        notnull_report_df, info_text = self.cache_reports_dict[self.report_0_name]

        if notnull_report_df.empty:
            report_df = notnull_report_df
            good_balance = {}
        else:
            (
                report_dict,
                report_df,
                good_balance   # good_balance_dict.keys()
            ) = ReportMaker(notnull_report_df).make_report_1()

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

    def read_sp_plat(self, report_df,
                     info_text,
                     ):
        """
        Reads sheet_name = 'СП_плат' using dict based on DF from sheet_name = 'Склад модулей(узлов)'
        (dict from self.modul_df).
        :param report_df:
        :param info_text:
        :return: report_df -> DF
        """

        if report_df.empty:
            return report_df
        else:
            self.msg = f'ЖДИТЕ!!! Читается БОЛЬШОЙ файл!'
            self.color = 'blue'
            self._set_info_label()
            self.progress_bar.setValue(25)

            report_dict = DictMaker().make_dict_from_df(report_df, 'Артикул', 'q-ty')

            cols, col_moduls_dict = self._get_column_list(report_dict)
            sheet_name = 'СП_плат'
            big_bom_df, self.msg, self.color = DataReader(
                PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols)

            if not big_bom_df.empty:

                big_bom_df = big_bom_df.iloc[14:]
                big_bom_df.rename(columns={'Спецификация плат': 'Unnamed: 4'}, inplace=True)

                for col in range(8, big_bom_df.shape[1]):
                    if big_bom_df.iloc[:, col].sum() == 0:
                        self.msg += f' {int(big_bom_df.iloc[:, [col]].columns[0].split(":")[-1]) - 9} '

                if self.color == 'red':
                    self._set_info_label()
                    self.report_info_label_text = info_text
                    return None
                else:
                    if self.msg:
                        info_text += f'НЕТ СОСТАВА (артикулы модулей): {self.msg}\n'

                    self.report_info_label.setStyleSheet(f'color:{self.color};')
                    self.report_info_label_text = info_text
                    self.report_info_label.setText(info_text)

                    self.progress_bar.setValue(70)

                    report_df = ReportMaker(big_bom_df).make_report_2(col_moduls_dict)

                    report_df.rename(columns={'Unnamed: 3': 'Подвид', 'Unnamed: 4': 'Название'}, inplace=True)
                    report_df = report_df.astype({'Артикул': int})

                return report_df
            else:
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print('else')

    def compose_report_2(self):
        """
        bad balance components (not including elements from components dict)
        :return: None
        """

        if not self.cache_reports_dict[self.report_1_name]:
            self.compose_report_1()

        bad_balance_report_df, info_text = self.cache_reports_dict[self.report_1_name]

        if bad_balance_report_df is None or bad_balance_report_df.empty:
            deficit_df = bad_balance_report_df
        else:

            report_df = self.read_sp_plat(bad_balance_report_df,
                                          info_text,
                                          # bad_balance_report_dict
                                          )
            info_text = self.report_info_label_text
            # print('1')
            # report_df.rename(columns={'Unnamed: 3': 'Подвид', 'Unnamed: 4': 'Название'}, inplace=True)
            # print(report_df.columns)
            deficit_df = report_df[['Артикул',
                                    # 'Unnamed: 3', 'Unnamed: 4',
                                    'Подвид', 'Название',
                                 'Склад основной', 'sum_components',
                                 'Штук можно изготовить', 'balance']][report_df['balance'] < 0]
            # print('2')

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
        :return: None
        """

        if not self.cache_reports_dict[self.report_0_name]:
            self.compose_report_0()

        notnull_report_df, info_text = self.cache_reports_dict[self.report_0_name]

        if notnull_report_df.empty:
            report_df = notnull_report_df
        else:

            report_df = self.read_sp_plat(notnull_report_df,
                                          info_text,
                                          )

            info_text = self.report_info_label_text

            report_df = report_df[['Артикул',
                                   # 'Unnamed: 3', 'Unnamed: 4',
                                   'Подвид', 'Название',
                                     'Склад основной', 'sum_components',
                                     'Штук можно изготовить', 'balance']]

            quantity_min = report_df['Штук можно изготовить'].min()
            self.report_info_label.setStyleSheet(f'color:{self.color};')
            info_text += f'Компонентов на складе достаточно для изготовления {quantity_min} заказов.\n'
            self.report_info_label.setText(info_text)
            self.report_info_label_text = info_text
            self.progress_bar.setValue(90)

        self.cache_reports_dict[self.report_3_name] = (report_df, info_text)

    def compose_report_4(self):
        """
        bad balance for components in moduls

        :return: None
        """

        if not self.cache_reports_dict[self.report_3_name]:
            self.compose_report_3()

        report_df, info_text = self.cache_reports_dict[self.report_3_name]

        if report_df is None or report_df.empty:
            self.cache_reports_dict[self.report_4_name] = (report_df, info_text)
            return None
        else:
            report_df = report_df[['Артикул',
                                   # 'Unnamed: 3', 'Unnamed: 4',
                                   'Подвид', 'Название',
                                 'Склад основной', 'sum_components',
                                 'Штук можно изготовить', 'balance']][(report_df['balance'] < 0)]

            self.cache_reports_dict[self.report_4_name] = (report_df, info_text)

    def prepare_stock_df(self):
        """

        :return: None
        """
        print('prepare_stock_df')
        self.progress_bar.setValue(20)
        cols = 'C, D, E, G, I, K, L, M, N, O, Q'  # added E, L, M, N, O +Q
        sheet_name = 'Склад'
        self.stock_df, self.msg, self.color = DataReader(
            PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols)

        self.progress_bar.setValue(50)

        self.stock_df = ReportMaker(self.stock_df).prepare_stock_df(sheet_name, PATH_TO_FILE_STOCK, FILE_STOCK)
        self.progress_bar.setValue(70)
        print('END prepare_stock_df')

    def prepare_block_report_df(self, components_from_modules_df):
        """

        :return:
        """

        components_from_modules_dict = DictMaker().make_dict_from_df(
            components_from_modules_df,
            'Артикул',
            'sum_components'
        )

        components_from_block_dict = DictMaker(
            self.block_list_dict).make_component_report_dict() if self.block_list_dict else {}

        if components_from_modules_df is None or components_from_modules_df.empty:
            res_compo_dict = components_from_block_dict
        else:
            res_compo_dict = DictMaker(
                self.block_list_dict).make_big_report_dict(components_from_modules_dict, components_from_block_dict)

        compo_data = defaultdict(list)
        [compo_data['Артикул'].append(k) for k in res_compo_dict.keys()]
        [compo_data['quantity'].append(v) for v in res_compo_dict.values()]
        res_compo_df = pd.DataFrame.from_dict(compo_data)

        return res_compo_df

    def prepare_modul_report_df(self, components_from_modules_df):
        """

        :return:
        """

        components_from_modules_dict = DictMaker().make_dict_from_df(
            components_from_modules_df,
            'Артикул',
            'sum_components'
        )

        res_compo_dict = components_from_modules_dict

        compo_data = defaultdict(list)
        [compo_data['Артикул'].append(k) for k in res_compo_dict.keys()]
        [compo_data['quantity'].append(v) for v in res_compo_dict.values()]
        res_compo_df = pd.DataFrame.from_dict(compo_data)

        return res_compo_df

    def calculate_price(self, res_compo_df, info_text):
        """

        :param components_from_modules_df: DF
        :param info_text: str
        :return: report_stock_df: DF
        """
        print('calculate_price')
        if res_compo_df.empty:
            report_stock_df = pd.DataFrame()
        else:

            if self.stock_df is None:
                self.prepare_stock_df()

            report_stock_df, info_text = ReportMaker(self.stock_df).calculate_price(res_compo_df, info_text)

        self.report_info_label_text = info_text

        self.report_info_label.setText(self.report_info_label_text)
        print('END calculate_price')
        self.progress_bar.setValue(95)
        return report_stock_df

    def compose_report_5(self):

        if not self.cache_reports_dict[self.report_3_name]:
            self.compose_report_3()

        components_from_modules_df, info_text = self.cache_reports_dict[self.report_3_name]
        report_df = self.prepare_block_report_df(components_from_modules_df)

        report_stock_df = self.calculate_price(report_df, info_text)

        if report_stock_df is None or report_stock_df.empty:
            info_text += 'БОМ пуст!'
            self.cache_reports_dict[self.report_5_name] = (components_from_modules_df, info_text)
            return None

        info_text = self.report_info_label_text

        self.cache_reports_dict[self.report_5_name] = (report_stock_df, info_text)

    def compose_report_6(self):

        if not self.cache_reports_dict[self.report_5_name]:
            self.compose_report_5()

        report_stock_df, info_text = self.cache_reports_dict[self.report_5_name]

        report_stock_df = report_stock_df[report_stock_df['balance'] < 0]

        if report_stock_df is None or report_stock_df.empty:
            info_text += 'По БОМ нет недостающих компонентов'
            self.cache_reports_dict[self.report_6_name] = (report_stock_df, info_text)
            return None

        info_text = self.report_info_label_text

        self.cache_reports_dict[self.report_6_name] = (report_stock_df, info_text)

    def compose_report_7(self):

        if not self.cache_reports_dict[self.report_2_name]:
            self.compose_report_2()

        components_from_modules_df, info_text = self.cache_reports_dict[self.report_2_name]

        report_df = self.prepare_modul_report_df(components_from_modules_df)

        report_stock_df = self.calculate_price(report_df, info_text)

        report_stock_df = report_stock_df[report_stock_df['balance'] < 0]

        if report_stock_df is None or report_stock_df.empty:
            info_text += 'Нет недостающих компонентов в недостающих модулях'
            self.cache_reports_dict[self.report_7_name] = (components_from_modules_df, info_text)
            return None

        info_text = self.report_info_label_text

        self.cache_reports_dict[self.report_7_name] = (report_stock_df, info_text)

    def compose_report_8(self):
        # read stock with comments
        if self.stock_df is None:
            self.prepare_stock_df()
        self.cache_reports_dict[self.report_8_name] = (None, self.report_8_name)
        print('FINISH compose_report_8')

    def compose_report_9(self):
        if self.stock_dev_df is None:
            # read stock with comments
            print('Чтение названий столбцов склада разработки...')
            self.progress_bar.setValue(5)

            sheet_name = 'Скл.Р(компоненты)'
            column_names = DataReader(PATH_TO_FILE_STOCK, FILE_STOCK).get_column_names_by_openpyxl(sheet_name)
            # print(column_names)
            indexes = [i for i in range(0, len(column_names) - 1)]
            cols_dict = {k: v for k, v in zip(indexes, column_names) if v}
            # print(cols_dict)
            # print(cols_dict.keys())

            self.progress_bar.setValue(20)

            stock_dev_df, msg, color = DataReader(
                PATH_TO_FILE_STOCK, FILE_STOCK).read_data_from_stock_file(sheet_name, cols_dict.keys())
            # print(stock_dev_df.head())
            init_index = stock_dev_df.index
            init_columns = stock_dev_df.columns
            stock_dev_df = stock_dev_df.dropna(how='all')
            # print(stock_dev_df.head())
            # print(list(cols_dict.values())[6:])
            ## list(cols_dict.values())[6:] ===> ['Цена, $', 'LDD......]
            dev_body_cols = list(cols_dict.values())[6:]
            stock_dev_df = stock_dev_df.dropna(how='all', subset=dev_body_cols)
            # print(stock_dev_df.head())
            # print(stock_dev_df[dev_body_cols].head())
            self.progress_bar.setValue(30)

            comments_df = DataReader(
                PATH_TO_FILE_STOCK, FILE_STOCK).get_comments_df_by_openpyxl(
                sheet_name,
                stock_dev_df[dev_body_cols],
                init_index,
                init_columns
            )
            comments_df = comments_df.fillna('')
            # print(comments_df[['LDD  Щербич ', 'RFPS Горбатов']].tail())

            self.progress_bar.setValue(60)

            # col_names_of_comments = dev_body_cols
            for col_name in dev_body_cols:
                stock_dev_df[f'comment_({col_name})'] = comments_df[col_name]
                stock_dev_df = FuncLibrary().fill_comments_column_with_data(stock_dev_df, f'comment_({col_name})')
                stock_dev_df[f'date_({col_name})'] = pd.to_datetime(
                    stock_dev_df[f'comment_({col_name})'], format='%d.%m.%Y', errors='coerce'
                )
            dates_col_list = [f'date_({col_name})' for col_name in dev_body_cols]
            stock_dev_df[f'date_max'] = stock_dev_df[dates_col_list].max(axis=1)

            stock_dev_df[f'q-ty'] = stock_dev_df[dev_body_cols[1:]].sum(axis=1)

            stock_dev_df = stock_dev_df.astype({'Артикул': int})

            self.stock_dev_df = stock_dev_df

        self.progress_bar.setValue(80)

        self.cache_reports_dict[self.report_9_name] = (None, self.report_9_name)
        print('FINISH compose_report_9')

    def get_report(self):

        if self.w is not None:
            self.w.close()
            self.w = None  # Discard reference to ReportWindow

        self.progress_bar.reset()
        self.color = 'blue'
        self.report_info_label.setStyleSheet(f'color:{self.color};')
        self.report_info_label.setText('.....')

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
            self.checkBox_report_8: self.compose_report_8,
            self.checkBox_report_9: self.compose_report_9,
                          }

        report_name = self.report_name_dict.get(self.checkBox_group.checkedButton())
        info_text = ''

        if self.checkBox_group.checkedButton() is not None:
            if self.block_list_dict is not None:
                if input_str != '{}' and not (self.old_dict_for_report.keys() and self.old_dict_for_report[input_str][report_name]):

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

                if input_str != '{}':
                    res_df, info_text = self.old_dict_for_report[input_str][report_name]
                else:
                    res_df = None
                    info_text = 'Блоки не заданы! ДОБАВЬТЕ В СПИСОК БЛОК!'
                    self.color = 'red'

                if res_df is None:
                    if info_text == self.report_8_name:
                        res_df = self.stock_df

                    if info_text == self.report_9_name:
                        res_df = self.stock_dev_df

                    self.msg = info_text

                elif not res_df.shape[0]:

                    if input_str == '{}':
                        self.msg = 'Блоки не заданы! ДОБАВЬТЕ В СПИСОК БЛОК!'
                        self.color = 'red'
                    else:
                        info_text = 'НЕТ ДАННЫХ ДЛЯ ОТЧЕТА'
                    res_df = None

            else:
                self.msg = 'ОШИБКА. Блоки не заданы.'
                self.color = 'red'
                res_df = None

        else:
            self.msg = 'Отчет не выбран'
            self.color = 'red'
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

    def get_stock(self):
        print('GET STOCK')
        report_name = 'Склад'

        # close self.w if opened
        if self.w is not None:
            self.w.close()
            self.w = None  # Discard reference to ReportWindow

        self.compose_report_8()
        self.compose_report_9()

        print(self.stock_df.columns)

        big_stock_df = self.stock_df.merge(self.stock_dev_df[['Артикул', 'date_max', 'q-ty']], how='left', on='Артикул')

        big_stock_df[f'date_max_total'] = big_stock_df[['date', 'date_max']].max(axis=1)

        big_stock_df[f'q-ty_total'] = big_stock_df[['Склад основной', 'q-ty']].sum(axis=1)

        max_dt_group_df = big_stock_df[
            ['Артикул осн.', 'date_max_total']
        ].groupby('Артикул осн.').agg({'date_max_total': ['max']})
        max_dt_group_df.columns = max_dt_group_df.columns.map('_'.join)
        max_dt_group_df = max_dt_group_df.rename_axis(None, axis=1)
        max_dt_group_df.rename(columns={'date_max_total_max': 'date_max_total_zam', }, inplace=True)

        big_stock_df = big_stock_df.merge(max_dt_group_df, how='left', on='Артикул осн.')
        big_stock_df['date_max_total_zam'] = big_stock_df[['date_max_total', 'date_max_total_zam']].max(axis=1)

        res_df = big_stock_df

        self.progress_bar.setValue(100)

        # REPORT WINDOW
        if res_df is not None and not res_df.empty and report_name:
            self.w = ReportWindow(report_name, res_df)
            self.w.show()
        info_text = 'СКЛАД готов'
        self.report_info_label.setText(info_text)
        pass

    def get_stock_mod(selfself):
        print('GET STOCK MOD')
        pass

    def exit_app(self):
        sys.exit()

# -------------------------------------------------------------------------
# !!!!!!!   RUN  !!!!!!
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = MyApp()
#     #     ex.show()
#     sys.exit(app.exec_())
