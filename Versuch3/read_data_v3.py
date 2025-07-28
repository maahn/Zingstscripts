import pandas as pd
import numpy as np
import xarray as xr
import re


def main():
    ifile = '20190718_Boden.txt'
    ds, complete_days = read_raw_data(ifile)
    print(ds)

def read_raw_data(ifile):
    f_in = open(ifile, 'rb')
    df_out = pd.DataFrame()
    day, month, year = np.nan, np.nan, np.nan
    for nl, line_byte in enumerate(f_in):
        if nl == 0:
            continue
        line = str(line_byte.strip()).replace(r'\xf8C', 'C').lstrip("b'").rstrip("'")
        if line.startswith('DATUM:'):
            day, month, year = line.split(':')[1].strip().strip("'").split('.')[:]
        else:
            try:
                hour, minute, second = line.split(' ')[0].split(':')
            except ValueError:
                continue
            string_split_values = re.split(r' 0[0-9]: ', line)[1::]
            values = []
            for column in string_split_values:
                try:
                    values.append(float(column.split(' ')[0]))
                except ValueError:
                    values.append(np.nan)
            data_line_dict = {'year': 2000 + int(year), 'month': int(month), 'day': int(day), 'hour': int(hour),
                              'minute': int(minute), 'second': int(second)}
            for nv, val in enumerate(values):
                data_line_dict[f'val_{nv}'] = float(val)
            new_row = pd.DataFrame(data_line_dict, index=[0])
            df_out = pd.concat([new_row, df_out.loc[:]]).reset_index(drop=True)
    df_out = df_out.iloc[::-1]
    date_new = pd.to_datetime(df_out.loc[:, ['year', 'month', 'day', 'hour', 'minute', 'second']]).dt.round('10min')
    df_out.drop(['year', 'month', 'day', 'hour', 'minute', 'second'], axis=1, inplace=True)
    df_out.insert(0, 'date', date_new.values)
    df_out = df_out.set_index('date')

    # !!!!!!!!!
    # ADD CALIBRATION HERE
    # !!!!!!!!!

    # Group by date and count time steps
    dates = df_out.index.date
    counts = pd.Series(dates).value_counts().sort_index()
    complete_days = counts[counts == 144].index
    incomplete_days = counts[counts != 144].index
    print(f'Days droped: {incomplete_days}')

    # Create a boolean mask using vectorized .isin()
    # mask_dates = pd.Series(dates).isin(complete_days).values

    # Filter dataframe
    # df_out = df_out[mask_dates].copy()
    ds_out = df_out.to_xarray()

    return ds_out, complete_days

if __name__ == '__main__':
    main()
    