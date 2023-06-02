from math import fabs


class DictMaker:
    def __init__(self, combobox_dict=None):
        self.combobox_dict = combobox_dict

    @staticmethod
    def _modules_in_block(moduls_dict, q_blocks):
        return {k: v * q_blocks for k, v in moduls_dict.items()}

    @staticmethod
    def modules_in_all_block(list_of_dicts):
        res_dict = {}
        for d in list_of_dicts:
            for k, v in d.items():
                res_dict.update({k: v}) if k not in res_dict.keys() else res_dict.update(
                    {k: v + res_dict.get(k)})
        return res_dict

    def make_report_dict(self):
        all_block = [
            self._modules_in_block(v[0], v[2]) for v in self.combobox_dict.values()]  # list of moduls dicts and q-ties
        dict_of_modules_for_report = self.modules_in_all_block(all_block)
        return dict(sorted(dict_of_modules_for_report.items()))

    # ?????
    def make_component_report_dict(self):
        all_components = [
            self._modules_in_block(v[1], v[2]) for v in self.combobox_dict.values()]  # list of components and q-ties
        dict_of_components_from_blocks = self.modules_in_all_block(all_components)
        return dict(sorted(dict_of_components_from_blocks.items()))

    # ?????
    def make_big_report_dict(self, dict_components_from_moduls, dict_components_from_blocks):
        all_components = [
            dict_components_from_moduls, dict_components_from_blocks]  # list of dicts and q-ties
        dict_of_all_components = self.modules_in_all_block(all_components)
        return dict(sorted(dict_of_all_components.items()))

    @staticmethod
    def make_dict_from_df(modul_df, col_name1, col_name2):
        modul_dict = {}
        if not modul_df.empty:
            for kv in modul_df[[col_name1, col_name2]].values:
                modul_dict.update({int(kv[0]): fabs(kv[1])})
        return modul_dict
