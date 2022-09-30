import pandas as pd


def map_tag(loc, ct):
    df = pd.read_excel(f'{loc}/{ct}/excel/dm_sheet/{ct}_xpath.xlsx', sheet_name='Sheet1')

    df_foo = pd.read_excel(f'{loc}/{ct}/excel/{ct}.xlsx', sheet_name='tag_master')
    df_foo.set_index("tag", drop=True, inplace=True)
    dictionary = df_foo.to_dict(orient="index")

    for key, val in dictionary.items():
        if val['map_tag'] == 'dual_nat':
            x = '/' + key
        else:
            x = '/' + val['map_tag']
        df['m_xpath'].replace(to_replace=r'/' + key + '\\b', value=x, regex=True, inplace=True)

    df_foo = pd.read_excel(f'{loc}/fixed.xlsx', sheet_name='xpath_map_fixed')
    df_foo.fillna('', inplace=True)
    df_foo.set_index("pat", drop=True, inplace=True)
    dictionary = df_foo.to_dict(orient="index")

    for key, val in dictionary.items():
        df['m_xpath'].replace(to_replace=key, value=val['map_tag'], regex=True, inplace=True)

    df.to_excel(f'{loc}/{ct}/excel/dm_sheet/{ct}_tag.xlsx', index=False)
    return True
