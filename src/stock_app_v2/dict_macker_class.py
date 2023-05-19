from math import fabs


class DictMaker:
    def __init__(self, combobox_dict=None):
        self.combobox_dict = combobox_dict

    @staticmethod
    def _moduls_in_block(moduls_dict, q_blocks):
        # d = {k: v * q_blocks for k, v in moduls_dict.items()}
        return {k: v * q_blocks for k, v in moduls_dict.items()}

    @staticmethod
    def _moduls_in_all_block(all_block):
        moduls_dict = {}
        for d in all_block:
            for k, v in d.items():
                moduls_dict.update({k: v}) if k not in moduls_dict.keys() else moduls_dict.update(
                    {k: v + moduls_dict.get(k)})
        return moduls_dict

    def make_report_dict(self):
        print(self.combobox_dict)
        # all_block = [self._moduls_in_block(v[0], v[1]) for v in
        all_block = [self._moduls_in_block(v[0], v[2]) for v in
                     self.combobox_dict.values()]  # list of moduls dicts and q-ties
        dict_of_moduls_for_report = self._moduls_in_all_block(all_block)
        return dict(sorted(dict_of_moduls_for_report.items()))

    @staticmethod
    def make_dict_from_modul_df(modul_df, col_name1, col_name2):
        modul_dict = {}
        for kv in modul_df[[col_name1, col_name2]].values:
            modul_dict.update({int(kv[0]): fabs(kv[1])})
        print(f'Hi from make_dict_from_modul_df! modul_dict={modul_dict}')
        return modul_dict
