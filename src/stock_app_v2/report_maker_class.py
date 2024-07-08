import numpy as np
import pandas as pd

# to disable warnings
from stock_app_v2.data_reader_class import DataReader

from stock_app_v2.dict_macker_class import DictMaker
from stock_app_v2.func_library_class import FuncLibrary


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

    # @staticmethod
    # def fill_comments_column_with_data(df, col_name):
    #     k = 0  # index of the row
    #     for i in df[:][col_name]:
    #         date_string = FuncLibrary().extract_date_string_from_comment(i)
    #         if date_string:
    #             df[col_name].values[k] = date_string[-1]
    #         else:
    #             df[col_name].values[k] = ''
    #         k += 1
    #     return df

    def prepare_stock_df(self, sheet_name, file_path, file_name):

        stock_df = self.df_from_file
        stock_df = stock_df.dropna(subset=['Артикул'])

        stock_df = stock_df.astype({'Артикул': int})

        stock_df[['Склад основной', 'Цена, $']] = stock_df[['Склад основной', 'Цена, $']].fillna(0)

        for val in stock_df['Склад основной'].values:
            stock_df.loc[stock_df['Склад основной'] == val, 'Склад основной'] = 0 if (
                not str(val).replace('.', '').isdigit()) else val

        for val in stock_df['Цена, $'].values:
            stock_df.loc[stock_df['Цена, $'] == val, 'Цена, $'] = 0 if (
                    str(val).isspace() or str(val) == '') else val

        stock_df['Цена, EURO'] = 0  # None

        for val in stock_df['Цена, $'].values:
            if str(val).lower().find('e') != -1 or str(val).lower().find('е') != -1:
                stock_df.loc[stock_df['Цена, $'] == val, 'Цена, $'] = 0
                stock_df.loc[stock_df['Цена, $'] == val, 'Цена, EURO'] = str(val).replace(',', '.').strip()[:-1]

        stock_df[['Склад основной', 'Цена, $', 'Цена, EURO']] = stock_df[[
            'Склад основной', 'Цена, $', 'Цена, EURO']].astype(float)

        stock_df['Статус замены'] = ''
        stock_df['Статус замены'].loc[stock_df['Артикул осн.'].notnull()] = 'Состав по док.'
        stock_df['Статус замены'].loc[stock_df['Артикул осн.'].isnull()] = 'Нет замены'

        # *------------
        offset = 2
        cell_names_dict = {'I1': ['I' + str(x) for x in range(offset, len(stock_df)+1)]}

        comment_dict = DataReader(
            file_path, file_name).read_comments_from_stock_file_by_openpyxl(
            sheet_name, cell_names_dict)

        res_data = {'comments': comment_dict['Склад основной']}

        df = pd.DataFrame(res_data)

        stock_df['comments'] = df[['comments']]

        stock_df['comments'] = stock_df['comments'].fillna('')

        col_name = 'comments'
        stock_df = FuncLibrary().fill_comments_column_with_data(stock_df, col_name)

        # k = 0  # index of the row
        # for i in stock_df[:]['comments']:
        #     date_string = FuncLibrary().extract_date_string_from_comment(i)
        #     if date_string:
        #         stock_df['comments'].values[k] = date_string[-1]
        #     else:
        #         stock_df['comments'].values[k] = ''
        #     k += 1

        stock_df['date'] = pd.to_datetime(stock_df['comments'], format='%d.%m.%Y', errors='coerce')

        #--------------
        print(f"Тип столбца с датой: {stock_df['date'].dtype}")
        #--------------+

        return stock_df

    def calculate_price(self, res_compo_df, info_text):
        """

        :param components_from_modules_df: DF
        :param info_text: str
        :return: report_stock_df: DF
        """
        print('calculate_price')
        stock_df = self.df_from_file
        # if res_compo_df.empty:
        #     report_stock_df = pd.DataFrame()
        # else:
        #
        #     if stock_df is None:
        #         self.prepare_stock_df()

        report_stock_df = res_compo_df.merge(stock_df, how='left', on='Артикул')
        report_stock_df['quantity'] = round(report_stock_df['quantity'], 4)


        report_stock_df['Артикул без замен'] = report_stock_df['Артикул']

        doc_report_stock_df = report_stock_df.loc[report_stock_df['Статус замены'] == 'Состав по док.']

        # --------------------

        main_res_report_stock_df = report_stock_df[['Артикул', 'quantity']].loc[
            report_stock_df['Статус замены'] == 'Состав по док.']

        main_res_report_stock_df['Артикул'] = (
            report_stock_df['Артикул осн.'].loc[
                report_stock_df['Статус замены'] == 'Состав по док.'].astype('int32')
        )

        main_res_report_stock_df = main_res_report_stock_df[['Артикул', 'quantity']]

        main_replace_df = main_res_report_stock_df.merge(stock_df, how='left', on='Артикул')

        main_replace_df['Артикул без замен'] = main_replace_df['Артикул']

        main_replace_df['Артикул'] = main_replace_df['Артикул осн.']
        main_report_stock_df = main_replace_df.sort_values('Артикул')
        main_report_stock_df['Статус замены'] = 'Состав по артикулу "осн."'

        #--------------------
        main_stock_df = stock_df.copy(deep=True)
        main_stock_df['Артикул без замен'] = main_stock_df['Артикул']
        main_stock_df['Артикул'].loc[main_stock_df['Артикул осн.'].notnull()] = (
            main_stock_df['Артикул осн.'].loc[main_stock_df['Артикул осн.'].notnull()].astype('int32')
        )

        max_report_stock_df = main_report_stock_df[[
            'Артикул', 'quantity']].merge(main_stock_df, how='left', on='Артикул')
        # print('max_report_stock_df')
        # print(max_report_stock_df)

        max_group_df = max_report_stock_df.groupby('Артикул осн.').agg({'Цена, $': ['max']})  #
        # print(max_group_df)
        min_group_df = max_report_stock_df.groupby('Артикул осн.').agg({'Цена, $': ['min']})  #
        # print(min_group_df)

        max_group_df.columns = max_group_df.columns.map('_'.join)
        min_group_df.columns = min_group_df.columns.map('_'.join)
        # print(max_group_df)

        max_group_df = max_group_df.rename_axis(None, axis=1)  # ?
        min_group_df = min_group_df.rename_axis(None, axis=1)  # ?
        max_p_report_stock_df = max_report_stock_df.merge(
            max_group_df, how='left', on='Артикул осн.')
        # print('max')

        max_p_report_stock_df = max_p_report_stock_df.loc[
            max_p_report_stock_df['Цена, $'] == max_p_report_stock_df['Цена, $_max']]
        max_p_report_stock_df['Статус замены'] = 'Состав, МАХ цена'
        max_p_report_stock_df = max_p_report_stock_df.drop(columns=['Цена, $_max'])
        max_p_report_stock_df['Артикул'] = max_p_report_stock_df['Артикул без замен']
        # print(max_p_report_stock_df)


        min_pm_report_stock_df = max_report_stock_df.merge(
            min_group_df, how='left', on='Артикул осн.')
        # print('min')

        min_pm_report_stock_df = min_pm_report_stock_df.loc[
            min_pm_report_stock_df['Цена, $'] == min_pm_report_stock_df['Цена, $_min']]
        min_pm_report_stock_df['Статус замены'] = 'Состав, MIN цена'
        min_pm_report_stock_df = min_pm_report_stock_df.drop(columns=['Цена, $_min'])

        min_pm_report_stock_df['Артикул'] = min_pm_report_stock_df['Артикул без замен']
        # print(min_pm_report_stock_df)

        # --------------------
        max_dt_group_df = max_report_stock_df.groupby('Артикул осн.').agg({'date': ['max']})

        max_dt_group_df.columns = max_dt_group_df.columns.map('_'.join)

        max_dt_group_df = max_dt_group_df.rename_axis(None, axis=1)

        max_dt_report_stock_df = max_report_stock_df.merge(max_dt_group_df, how='left', on='Артикул осн.')

        max_dt_report_stock_df = max_dt_report_stock_df.loc[
            max_dt_report_stock_df['date'] == max_dt_report_stock_df['date_max']]
        gr = max_dt_report_stock_df.groupby(['Артикул']).size().reset_index(name='counts')
        gr_dupl = gr.loc[gr['counts'] > 1]
        # print('------------')
        date_dupl_df = max_dt_report_stock_df.loc[max_dt_report_stock_df['Артикул'].isin(gr_dupl['Артикул'])]
        # print(date_dupl_df)
        date_dedupl_df = date_dupl_df.loc[date_dupl_df['Артикул'] == date_dupl_df['Артикул без замен']]
        # print(date_dedupl_df)
        date_not_dupl_df = max_dt_report_stock_df.loc[~max_dt_report_stock_df['Артикул'].isin(gr_dupl['Артикул'])]
        # print(date_not_dupl_df)
        max_dt_report_stock_df = pd.concat([
            date_not_dupl_df,
            date_dedupl_df,
        ], ignore_index=True)

        max_dt_report_stock_df['Статус замены'] = 'Состав, ДАТА'
        max_dt_report_stock_df = max_dt_report_stock_df.drop(columns=['date_max'])
        max_dt_report_stock_df['Артикул'] = max_dt_report_stock_df['Артикул без замен']
        # --------------------

        report_stock_df = pd.concat([
            report_stock_df,
            main_report_stock_df,
            max_p_report_stock_df,
            min_pm_report_stock_df,
            max_dt_report_stock_df,
        ], ignore_index=True)
        # --------------------

        not_found_df = report_stock_df[report_stock_df['Название\n(Комплектующие склада)'].isnull()]
        not_found_dict = DictMaker().make_dict_from_df(not_found_df, 'Артикул', 'quantity')

        not_found = list(not_found_dict.keys())

        if not_found:
            info_text += f'НЕТ ИНФОРМАЦИИ по артикулам этих компонентов: {not_found} \n'
        else:
            info_text += 'Все компоненты указаны корректно. \n'

        report_stock_df['total $'] = round(report_stock_df['quantity'] * report_stock_df['Цена, $'], 4)
        dollar_price = round(report_stock_df['total $'].loc[(
                report_stock_df['Статус замены'] == 'Состав по док.') | (
                report_stock_df['Статус замены'] == 'Нет замены')].sum(), 2)

        max_dollar_price = round(report_stock_df['total $'].loc[(
                report_stock_df['Статус замены'] == 'Состав, МАХ цена') | (
                report_stock_df['Статус замены'] == 'Нет замены')].sum(), 2)
        #-----
        report_stock_df['% Доля\nстоимости компонента\nв стоимости известного состава'] = np.nan
        report_stock_df[
            '% Доля\nстоимости компонента\nв стоимости известного состава'
        ].loc[
            (report_stock_df['total $'] > 0)
        ] = round((100 * report_stock_df['total $'].loc[report_stock_df['total $'] > 0] / dollar_price), 2)

        report_stock_df['total EURO'] = report_stock_df['quantity'] * report_stock_df['Цена, EURO']

        euro_price = round(report_stock_df['total EURO'].loc[(
                report_stock_df['Статус замены'] == 'Состав по док.') | (
                report_stock_df['Статус замены'] == 'Нет замены')].sum(), 2)

        info_text += f'Цена (состав по док. по комп. с известной ценой) = {dollar_price} $ + {euro_price} euro\n'
        info_text += f'MAX Цена = {max_dollar_price} $ \n'

        null_df = report_stock_df[(report_stock_df['Цена, $'] == 0) & (report_stock_df['Цена, EURO'] == 0)]
        null_price_list = list(null_df['Артикул'])
        if null_price_list:
            info_text += f'НЕТ ЦЕНЫ для этих компонентов (артикулы): {null_price_list} \n'

        report_stock_df.loc[:, 'balance'] = report_stock_df['Склад основной'] - report_stock_df['quantity']
        report_stock_df['balance'] = round(report_stock_df['balance'], 4)

        report_stock_df['Артикул'] = report_stock_df['Артикул'].astype('int32')
        report_stock_df['Артикул без замен'] = report_stock_df['Артикул без замен'].astype('int32')

        if not euro_price:
            report_stock_df = report_stock_df.drop(['Цена, EURO', 'total EURO'], axis=1)

        # self.report_info_label_text = info_text
        #
        # self.report_info_label.setText(self.report_info_label_text)
        # print('END calculate_price')
        # self.progress_bar.setValue(95)
        return report_stock_df, info_text


