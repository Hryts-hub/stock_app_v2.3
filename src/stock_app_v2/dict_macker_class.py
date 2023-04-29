
class DictMaker:
    def __init__(self, combobox_dict):
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
        all_block = [self._moduls_in_block(v[0], v[1]) for v in
                     self.combobox_dict.values()]  # list of moduls dicts and q-ties
        dict_of_moduls_for_report = self._moduls_in_all_block(all_block)
        return dict(sorted(dict_of_moduls_for_report.items()))
