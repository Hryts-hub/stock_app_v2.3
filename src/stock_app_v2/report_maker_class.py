from math import fabs

import numpy as np
import pandas as pd

# to disable warnings
from stock_app_v2.data_reader_class import DataReader

from stock_app_v2.dict_macker_class import DictMaker

pd.options.mode.chained_assignment = None  # default='warn'


class ReportMaker:
    def __init__(self, df_from_file):

        self.df_from_file = df_from_file

    def make_report_0(self, report_dict):
        # clean df with modules --> existing block modules DF + not existing (null_df)
        if report_dict.items():
            report_dict_df = pd.DataFrame(np.array(list(report_dict.items())),
                                          columns=['Артикул', 'q-ty'])

            filtered_modul_df = report_dict_df.merge(self.df_from_file, on='Артикул', how='left')

            filtered_modul_df = filtered_modul_df.astype({'Артикул': int})

            null_df = filtered_modul_df[filtered_modul_df[
                'Узлы (электронные модули, радиаторные, трансформаторные, кабельные и др. сборки)'].isnull()]

            filtered_modul_df = filtered_modul_df.dropna(
                subset=['Узлы (электронные модули, радиаторные, трансформаторные, кабельные и др. сборки)'])
            # not existing moduls removed from filtered_modul_df

            filtered_modul_df = filtered_modul_df.fillna(0)
            # NA values filled with 0
            filtered_modul_df['Штук можно изготовить'] = (
                    filtered_modul_df['Количество (в примечаниях история приходов и уходов)'] //
                    filtered_modul_df['q-ty'])

            filtered_modul_df = filtered_modul_df.astype({'Штук можно изготовить': int})
            if filtered_modul_df.empty:
                quantity_min = 0
            else:
                quantity_min = filtered_modul_df['Штук можно изготовить'].min()

            filtered_modul_df['balance'] = (
                    filtered_modul_df['Количество (в примечаниях история приходов и уходов)'] -
                    filtered_modul_df['q-ty'])
        else:
            filtered_modul_df = pd.DataFrame(columns=['Артикул', 'q-ty',
       'Узлы (электронные модули, радиаторные, трансформаторные, кабельные и др. сборки)',
       'Количество (в примечаниях история приходов и уходов)',
       'Штук можно изготовить', 'balance'])
            null_df = filtered_modul_df
            quantity_min = 0
        return (
            filtered_modul_df,
            null_df,
            int(quantity_min),
            )

    def make_report_1(self):

        # bad balance for existing moduls, and not found moduls
        filtered_modul_df = self.df_from_file

        bad_balance_df = filtered_modul_df[filtered_modul_df['balance'] < 0]

        bad_balance_dict = DictMaker().make_dict_from_df(bad_balance_df, 'Артикул', 'balance')

        good_balance_df = filtered_modul_df[filtered_modul_df['balance'] >= 0]
        good_balance_dict = DictMaker().make_dict_from_df(good_balance_df, 'Артикул', 'balance')

        # quantity_min = filtered_modul_df['Штук можно изготовить'].min()
        return (
            bad_balance_dict,
            # bad_balance_df[['Артикул', 'q-ty', 'balance']],
            bad_balance_df[['Артикул', 'q-ty',
                            'Узлы (электронные модули, радиаторные, трансформаторные, кабельные и др. сборки)',
                            'Количество (в примечаниях история приходов и уходов)',
                            'balance']],
            # int(quantity_min),
            good_balance_dict.keys()
        )

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

    def make_report_2(self, col_moduls_dict):
        # returns components in moduls for all given blocks. Initial dict of components not included
        # moduls is existing moduls

        col_names = self.df_from_file.columns
        self._filter_components_in_columns(col_names)

        self.df_from_file = self.df_from_file.fillna(0)

        for k, v in col_moduls_dict.items():

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

        df_quantity = pd.DataFrame({'Штук можно изготовить': quantity})
        filtered_df['Штук можно изготовить'] = df_quantity['Штук можно изготовить'].astype(int)

        filtered_df.loc[:, 'balance'] = filtered_df['Склад основной'] - filtered_df['sum_components']

        return filtered_df


