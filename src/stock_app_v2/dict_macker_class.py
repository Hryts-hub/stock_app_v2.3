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

    @staticmethod
    def make_dicts_of_modul_compo_err(prepared_list):
        modul_dict = {}
        component_dict = {}
        error_dict = {}

        if prepared_list:
            for t in prepared_list:
                k = t[0].strip()
                v = t[1].strip() if len(t) == 2 else ''
                if (
                        k.endswith('c')
                        and k[:-1].strip().isdigit()
                        and v.replace('.', '').isdigit()
                ):

                    k = int(k[:-1].strip())
                    v = float(v)
                    if k not in modul_dict:
                        modul_dict.update({k: v})
                    else:
                        modul_dict.update({k: v + modul_dict.get(k)})
                elif (
                        k.startswith('c')
                        and k[1:].strip().isdigit()
                        and v.replace('.', '').isdigit()
                ):

                    k = int(k[1:].strip())
                    v = float(v)
                    if k not in modul_dict:
                        modul_dict.update({k: v})
                    else:
                        modul_dict.update({k: v + modul_dict.get(k)})
                elif k.isdigit() and v.replace('.', '').isdigit():

                    k = int(k)
                    v = float(v)
                    if k not in component_dict:
                        component_dict.update({k: v})
                    else:
                        component_dict.update({k: v + component_dict.get(k)})
                else:
                    error_dict[k] = v

        return modul_dict, component_dict, error_dict

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

    @staticmethod
    def remove_zero_values(input_dict):
        """
        Removes entries from a dictionary where the key is 0 or the value is 0.0 and returns the modified dictionary
        along with a dictionary of removed entries.

        Parameters:
        input_dict (dict): A dictionary where keys are integers and values are floats.

        Returns:
        tuple: A tuple containing two dictionaries:
            - output_dict: The input dictionary with entries removed where the key is 0 or the value is 0.0.
            - error_dict: A dictionary containing the entries removed from input_dict.
        """
        # Create a dictionary of entries to remove where the key is 0 or the value is 0.0
        error_dict = {k: v for k, v in input_dict.items() if k == 0 or v == 0.0}

        # Create the output dictionary by excluding keys from error_dict
        output_dict = {k: v for k, v in input_dict.items() if k not in error_dict}

        return output_dict, error_dict
