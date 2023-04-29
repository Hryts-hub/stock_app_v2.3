from math import fabs

import numpy as np
import pandas as pd

# to disable warnings
from stock_app_v2.data_reader_class import DataReader

# from stock_app_v2.stock_app import PATH_TO_FILE_STOCK, FILE_STOCK
FILE_STOCK = 'Склад 14.01.16.xlsx'
# FILE_STOCK = 'Z:/Склад/Склад 14.01.16.xlsx'
PATH_TO_FILE_STOCK = 'D:/OEMTECH/Projects/FILE_STOCK_FOLDER/'

pd.options.mode.chained_assignment = None  # default='warn'


class ReportMaker:
    def __init__(self,
                 # report_name,
                 # report_option,
                 report_dict, df_from_file):
        # self.report_name = report_name  # self.checkBox_report_1 (names written near ceck boxes)
        # self.report_option = report_option  # self.checkBox_group.checkedButton() (selected option)

        # sorted dict from combo box
        self.report_dict = report_dict
        self.old_report_dict = {}

        # modul_df = pd.read_excel('Z:/Склад/Склад 14.01.16.xlsx', sheet_name='Склад модулей(узлов)', usecols='C,F,G')
        self.df_from_file = df_from_file
        self.bad_balance_dict = {}

    def make_report_1(self):
        report_dict_df = pd.DataFrame(np.array(list(self.report_dict.items())),
                                      columns=['Артикул', 'q-ty'])

        filtered_modul_df = report_dict_df.merge(self.df_from_file, on='Артикул', how='left')
        try:
            filtered_modul_df['moduls_in_order'] = self.report_dict.values()
        except Exception as e:
            print(f'ОШИБКА {type(e)}: {e}')
        filtered_modul_df = filtered_modul_df.dropna(
            subset=['Узлы (электронные модули, радиаторные, трансформаторные, кабельные и др. сборки)'])
        # not existing moduls removed from filtered_modul_df
        filtered_modul_df = filtered_modul_df.fillna(0)

        filtered_modul_df['q-ty of orders from moduls'] = (
                filtered_modul_df['Количество (в примечаниях история приходов и уходов)'] //
                filtered_modul_df['moduls_in_order'])

        filtered_modul_df['balance'] = (
                filtered_modul_df['Количество (в примечаниях история приходов и уходов)'] -
                filtered_modul_df['moduls_in_order'])

        bad_balance_df = filtered_modul_df[filtered_modul_df['balance'] < 0]
        for kv in bad_balance_df[['Артикул', 'balance']].values:
            self.bad_balance_dict.update({int(kv[0]): fabs(kv[1])})
        self.old_report_dict = self.report_dict

        quantity_min = filtered_modul_df['q-ty of orders from moduls'].min()
        return self.bad_balance_dict, bad_balance_df[['Артикул', 'balance']], quantity_min

    def _filter_components_in_columns(self, col_names):
        # column with OR-condition for any number of columns (all elements in device)
        # this func filters components - only components from our moduls stays
        cond_str = ''
        for col in col_names[8:]:
            col_str = f"self.df_from_file['{col}'].notnull()"
            cond_str += (col_str + '|')
        filter_str = f"self.df_from_file[{cond_str[:-1]}][{list(col_names)}]"
        mycode = f"self.df_from_file = {filter_str}"
        try:
            exec(mycode)
        except Exception as e:
            print(f'ОШИБКА {type(e)}: {e}')

    def make_report_2(self):
        col_names = self.df_from_file.columns
        self._filter_components_in_columns(col_names)

        self.df_from_file = self.df_from_file.fillna(0)

        for k, v in self.report_dict.items():

            self.df_from_file[f'Unnamed: {k}'] = self.df_from_file[f'Unnamed: {k}'] * v

        self.df_from_file['sum_components'] = 0

        for col in col_names[8:]:
            try:
                self.df_from_file['sum_components'] += self.df_from_file[col]
            except Exception as e:
                print(f'ОШИБКА {type(e)}: {e}')

        self.df_from_file.rename(columns={'Unnamed: 2': 'Артикул', }, inplace=True)
        self.df_from_file.rename(columns={'Unnamed: 8': 'Склад основной', }, inplace=True)

        filtered_df = self.df_from_file[self.df_from_file['sum_components'] != 0]

        for val in filtered_df['Склад основной'].values:
            filtered_df.loc[filtered_df['Склад основной'] == val, 'Склад основной'] = 0 if str(val).isspace() else val

        quantity = filtered_df['Склад основной'].astype(float) // filtered_df['sum_components']

        df_quantity = pd.DataFrame({'quantity': quantity})
        filtered_df['quantity'] = df_quantity['quantity'].astype(int)

        filtered_df.loc[:, 'balance'] = filtered_df['Склад основной'] - filtered_df['sum_components']

        return None, filtered_df


