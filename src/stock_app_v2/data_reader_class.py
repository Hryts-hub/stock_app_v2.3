import os.path
import pandas as pd


class DataReader:
    def __init__(self, path_to_file, file_name):
        self.path_to_file = path_to_file
        self.file_name = file_name
        self.path = f'{self.path_to_file}{self.file_name}'
        self.data = None
        self.color = 'red'
        self.msg = ''

    # def check_file_existence(self):
    def read_csv_file(self, column_name):
        if self.path_to_file is not None and os.path.exists(self.path_to_file):
            if self.path is not None and os.path.exists(self.path):

                try:
                    self.data = pd.read_csv(self.path).sort_values(by=column_name)  #, ascending=False
                    self.color = 'blue'
                except Exception as e:
                    self.msg = f'ОШИБКА {type(e)}: {e}'
            else:
                self.msg = f'Файл {self.file_name} по пути {self.path_to_file} не найден.'
        else:
            self.msg = f'Путь {self.path_to_file} не найден.'

        return self.data, self.msg, self.color

    def add_to_file_csv(self, df):
        if os.path.exists(self.path_to_file):
            if os.path.exists(f'{self.path_to_file}{self.file_name}'):
                df.to_csv(f'{self.path_to_file}{self.file_name}', mode='a', index=False, header=None)
                self.msg = f'Запись добавлена в файл {self.file_name} !'
            else:
                df.to_csv(f'{self.path_to_file}{self.file_name}', mode='a', index=False)
                self.msg = f'Файл {self.file_name} создан! Запись добавлена!'
            self.color = 'blue'
        else:
            self.msg = f"Путь {self.path_to_file} не найден!"
        return self.msg, self.color

    def read_modul_from_stock_file(self, sheet_name, cols):
        if self.path_to_file is not None and os.path.exists(f'{self.path_to_file}{self.file_name}'):
            try:
                self.data = pd.read_excel(
                    f'{self.path_to_file}{self.file_name}',
                    sheet_name=sheet_name,
                    usecols=cols
                )
                self.data = self.data.iloc[2:]
                self.color = 'blue'
                self.msg = f'Склад модулей загружен'
            except Exception as e:
                self.color = 'red'
                self.msg = f'ОШИБКА modul {type(e)}: {e}'
        else:
            self.color = 'red'
            self.msg = f'{self.path_to_file}{self.file_name} -- не найден.'
        return self.data, self.msg, self.color

    def read_bom_from_stock_file(self, sheet_name, cols):
        if self.path_to_file is not None and os.path.exists(f'{self.path_to_file}{self.file_name}'):
            try:
                self.data = pd.read_excel(
                    f'{self.path_to_file}{self.file_name}',
                    sheet_name=sheet_name,
                    usecols=cols,
                    engine='openpyxl',
                    # skiprows=14
                )
                self.data = self.data.iloc[14:]
                self.data.rename(columns={'Спецификация плат': 'Unnamed: 4'}, inplace=True)
                self.color = 'blue'
                for col in range(8, self.data.shape[1]):

                    if self.data.iloc[:, col].sum() == 0:

                        # print(f'{col} is all 0')
                        # print(f'{self.data.iloc[:, [col]].columns} is all 0')
                        # print(f'Артикул {int(self.data.iloc[:, [col]].columns[0].split(":")[-1]) - 9} -- нет состава')
                        self.msg += f' {int(self.data.iloc[:, [col]].columns[0].split(":")[-1]) - 9} '
                # self.msg = f'Склад {sheet_name} загружен'
                # print(self.data.shape)
                # print(self.data.columns)
            except Exception as e:
                self.color = 'red'
                self.msg = f'ОШИБКА bom {type(e)}: {e}'
        else:
            self.color = 'red'
            self.msg = f'{self.path_to_file}{self.file_name} -- не найден.'
        return self.data, self.msg, self.color

