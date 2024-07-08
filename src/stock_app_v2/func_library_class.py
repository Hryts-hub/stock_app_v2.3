class FuncLibrary:
    def __init__(self):
        pass

    @staticmethod
    def extract_date_string_from_comment(comment_text):
        # print('extract_date_string_from_comment')
        i = comment_text.split('\n')
        date_string = ''

        if i:
            s = [[x for x in aa.split(' ') if x != ''] for aa in i if aa != '']
            ss = []
            for x in s:
                if len(x) > 1 and x[0][-1].isdigit() and x[1][0].isalpha():
                    elem = x[0][-8:]
                    ss.append(elem)
            date_string = [x.replace('/', '.') for x in ss]
            date_string = [x.replace('-', '0') for x in date_string]
            date_string = [x[:6] + '20' + x[6:8] for x in date_string]

        return date_string

    @staticmethod
    def fill_comments_column_with_data(df, col_name):
        k = 0  # index of the row
        for i in df[:][col_name]:
            date_string = FuncLibrary().extract_date_string_from_comment(i)
            if date_string:
                df[col_name].values[k] = date_string[-1]
            else:
                df[col_name].values[k] = ''
            k += 1
        return df

