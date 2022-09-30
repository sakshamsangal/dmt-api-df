import re

import pandas as pd


def remove_processed_record(df, df_new):
    rows = df.loc[pd.isnull(df['comp']) == False, :]
    df_new = pd.concat([df_new, pd.DataFrame.from_records(rows)])
    df.drop(rows.index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df, df_new


def remove_processed_record1(df, df_new, ls):
    temp = {
        'comp': 'Component',
        'style': 'Styling'
    }
    cond = []
    for item in ls:
        cond.append(df[item] != df[temp[item]])
    rows = df.loc[all(cond), :]
    df_new = pd.concat([df_new, pd.DataFrame.from_records(rows)])
    df.drop(rows.index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df, df_new


def update_df(df, short_str, comp, style, feat):
    for index, row in df.iterrows():
        if row['m_xpath'].endswith(short_str):
            df.iat[index, 1] = comp  # comp
            df.iat[index, 2] = style  # style
            if pd.isnull(df.iloc[index, 3]):
                df.iat[index, 3] = feat  # feat
    return df


def my_ends_with(loc, ct, df, df_new):
    # ls = rd.get_comp_style(loc)
    # ls = rd.get_patt_to_be_replaced(loc, ct)
    df_foo = pd.read_excel(f'{loc}/{ct}/excel/{ct}.xlsx', sheet_name='comp_style')
    df_foo.set_index("id", drop=True, inplace=True)
    dictionary = df_foo.to_dict(orient="index")
    # ls = rd.get_patt_to_be_replaced(loc, ct)

    # id comp=1 h1=2 h2=3 text=4 feat=5
    for key, val in dictionary.items():
        df = update_df(df, f'/text', val['comp'], val['text_style'], val['feat'])
        df, df_new = remove_processed_record(df, df_new)

    for key, val in dictionary.items():
        df = update_df(df, f'/{key}', val['comp'], val['text_style'], val['feat'])
        df = update_df(df, f'/{key}/h1', val['comp'], val['h1_style'], val['feat'])
        df = update_df(df, f'/{key}/h2', val['comp'],val['h2_style'], val['feat'])
        df, df_new = remove_processed_record(df, df_new)

    return df, df_new


def fill_exception(loc, ct, df, df_new):
    # ls = rd.get_patt_to_be_replaced(loc, ct)
    df_foo = pd.read_excel(f'{loc}/{ct}/excel/{ct}.xlsx', sheet_name='exception')
    df_foo.set_index("pat", drop=True, inplace=True)
    dictionary = df_foo.to_dict(orient="index")
    # ls = rd.get_patt_to_be_replaced(loc, ct)

    for key, val in dictionary.items():
        pat = re.compile(key)
        for index, row in df.iterrows():
            if re.fullmatch(pat, row[val['pat_col']]):
                df.iat[index, 1] = val['comp']  # comp
                df.iat[index, 2] = val['styling']  # styling
                if val['overwrite_feat'] == 1:
                    df.iat[index, 3] = val['feat']  # feat
                else:
                    if pd.isnull(df.iloc[index, 3]):
                        df.iat[index, 3] = val['feat']  # feat
                df.iat[index, 4] = val['comm']  # comm

        df, df_new = remove_processed_record(df, df_new)
    return df, df_new


def fill_comp_style(loc, ct, fn, ls):
    df = pd.read_excel(f'{loc}/{ct}/excel/dm_sheet/{ct}_feat.xlsx', sheet_name='Sheet1')
    df_new = pd.DataFrame(columns=df.columns)
    df, df_new = fill_exception(loc, ct, df, df_new)
    df, df_new = my_ends_with(loc, ct, df, df_new)

    df_new.to_excel(f'{loc}/{ct}/excel/dm_sheet/{ct}_dm.xlsx', index=False)
    df.to_excel(f'{loc}/{ct}/excel/dm_sheet/{ct}_feat.xlsx', index=False)
    c = df.shape[0]

    df_new1 = pd.DataFrame(columns=df.columns)
    df, df_new = remove_processed_record1(df_new, df_new1, ls)
    df_new.drop(df_new.columns[0:6], axis=1, inplace=True)
    df_new.to_excel(f'{loc}/{ct}/excel/{fn}.xlsx', index=False)

    return c, df_new.shape[0]