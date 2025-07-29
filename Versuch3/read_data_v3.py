import pandas as pd
import numpy as np
import re
import os


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
        try:
            day, month, year = int(day), int(month), int(year)
        except ValueError:
            continue
        else:
            try:
                hour, minute, second = line.split(' ')[0].split(':')
                hour, minute, second = int(hour), int(minute), int(second)
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
    return df_out

# !!! Change path to directory with observations
ipath='/path/to/obs'
# !!! Change path to directory with observations

# Open all files a xarray dataset and out them in list
df_list = []
for file in os.listdir(ipath):
    if file.endswith('.txt'):
        df_list.append(read_raw_data(os.path.join(ipath, file)))

# Concatenate along date dimension and sort by time
df_combined = pd.concat(df_list)

# Find occurence of first unique date entry as for each new file, only the delta since the last output is added
_, index_unique = np.unique(df_combined.index, return_index=True)
df_combined = df_combined.iloc[index_unique]

# For all possible days, create 10 minute intervals and reindex data to full day intervals
days = df_combined.index.normalize().unique()
full_index = pd.DatetimeIndex([])
for day in days:
    full_day_index = pd.date_range(start=day, periods=144, freq='10min')
    full_index = full_index.append(full_day_index)
df_combined = df_combined.reindex(full_index)
df_combined.index.name = 'date'

# Interpolate gaps in timeseries. Limit interpolation to a maximum of 3 consecutive timesteps (i.e. 30 minutes)
df_combined = df_combined.interpolate(method='time', limit=3)

# Get list of all, complete and incomplete days
all_days, complete_days, incomplete_days = [], [], []
for day in days:
    day_str = day.strftime('%Y-%m-%d')
    all_days.append(day_str)
    if df_combined.loc[day_str].dropna().shape[0] == 144:
        complete_days.append(day_str)
    else:
        incomplete_days.append(day_str)

# Convert to xarray
ds_combined = df_combined.to_xarray()
    