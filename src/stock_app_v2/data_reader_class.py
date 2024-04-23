import os.path

import openpyxl
import pandas as pd


class DataReader:
    def __init__(self, path_to_file, file_name):
        self.path_to_file = path_to_file
        self.file_name = file_name
        self.path = os.path.abspath(os.path.join(self.path_to_file, self.file_name))
        # self.path = f'{self.path_to_file}{self.file_name}'
        self.data = None
        self.color = 'red'
        self.msg = ''

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

    def read_data_from_stock_file(self, sheet_name, cols):
        if self.path_to_file is not None and os.path.exists(f'{self.path_to_file}{self.file_name}'):
            try:
                self.data = pd.read_excel(
                    f'{self.path_to_file}{self.file_name}',
                    sheet_name=sheet_name,
                    usecols=cols,
                    engine='openpyxl',
                )
                self.color = 'blue'
            except Exception as e:
                self.color = 'red'
                self.msg = f'ОШИБКА: {type(e)}: {e}'
        else:
            self.color = 'red'
            self.msg = f'{self.path_to_file}{self.file_name} -- не найден.'

        return self.data, self.msg, self.color

    def read_comments_from_stock_file_by_openpyxl(self, sheet_name, cell_names_dict):
        comment_dict = dict()

        if self.path_to_file is not None and os.path.exists(self.path):
            try:
                wb = openpyxl.load_workbook(self.path)
                sheet = wb[sheet_name]
                for cell_col_name, cell_names_list in cell_names_dict.items():
                    cell_names_list = [
    sheet[cell_name].comment.text if sheet[cell_name].comment else None for cell_name in cell_names_list
                    ]
                    comment_dict[sheet[cell_col_name].value] = cell_names_list
                wb.close()
            except Exception as e:
                print(f'ERROR: {type(e)}: {e}')
        else:
            self.msg = f'{self.path} -- not found.'
            print(self.msg)
        return comment_dict

