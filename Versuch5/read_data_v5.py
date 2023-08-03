import pandas as pd
import os


def main():

    ipath_data = 'data/processed'

    # Read data from instruments into pandas dataframes
    df_read_dict = {'pyr': read_pyrgeometer(ipath_data),
                    'ir': read_ir(ipath_data),
                    'kt19': read_kt19(ipath_data)}

    # Join datasets and remove duplicates from 'intersect'
    df_read_all = df_read_dict['kt19'].join(df_read_dict['ir'],
                                            how='outer').join(df_read_dict['pyr'], how='outer').drop_duplicates()

    # Convert to xarray dataset
    ds_read_all = df_read_all.to_xarray()


def read_kt19(ipath_in):
    """
    Function to read KT19 data and put them into a pandas dataframe

    :param ipath_in: input path where IR thermometer data is located
    :return df_ir_out: pandas dataframe with IR thermometer data
    """

    # Read data
    file_kt19 = os.path.join(ipath_in, 'kt19_data_all.dat')
    df_kt19_out = pd.read_csv(file_kt19, sep='\s+', header=None, engine='c',
                              names=['date', 'hour', 'minute', 'second', 'Tb', 'em', 'dt', 'Ts'])
    df_kt19_out.drop_duplicates(inplace=True)

    # Split column with date information and transform to datetime index
    df_kt19_out['year'] = [int(str(day)[0:4]) for day in df_kt19_out.date]
    df_kt19_out['month'] = [int(str(day)[4:6]) for day in df_kt19_out.date]
    df_kt19_out['day'] = [int(str(day)[6:8]) for day in df_kt19_out.date]
    date_new = pd.to_datetime(df_kt19_out.loc[:, ['year', 'month', 'day', 'hour', 'minute', 'second']]).dt.round('S')

    # Rename variables and drop not needed columns
    df_kt19_out['T_kt'], df_kt19_out['Tb_kt'] = df_kt19_out['Ts'], df_kt19_out['Tb']
    df_kt19_out.drop(['year', 'month', 'day', 'hour', 'minute', 'second', 'date', 'dt', 'em', 'Ts', 'Tb'], axis=1,
                     inplace=True)

    # Insert datetime index
    df_kt19_out.insert(0, 'date', date_new.values)
    df_kt19_out = df_kt19_out.set_index('date')

    return df_kt19_out


def read_ir(ipath_in):
    """
    Function to read IR Thermometer data and put them into a pandas dataframe

    :param ipath_in: input path where IR thermometer data is located
    :return df_ir_out: pandas dataframe with IR thermometer data
    """

    # Read data
    file_ir = os.path.join(ipath_in, 'ir_data_all.dat')
    df_ir_out = pd.read_csv(file_ir, sep='\t+', header=None, names=['No', 'IR', 'TK', 'date'], engine='python')
    df_ir_out.drop_duplicates(inplace=True)

    # We don't need the number columns
    df_ir_out = pd.DataFrame(df_ir_out[1:])
    df_ir_out.drop(['No'], axis=1, inplace=True)

    # Remove 'C' from values and change data type into float and some renaming
    df_ir_out['Tb_ir'] = pd.to_numeric(df_ir_out['IR'].str.replace('C', ''))
    df_ir_out['T_ir'] = pd.to_numeric(df_ir_out['TK'].str.replace('C', ''))
    df_ir_out.drop(['IR', 'TK'], axis=1, inplace=True)

    # Set up datetime index
    df_ir_out['date'] = pd.to_datetime(df_ir_out['date']).dt.round('S')
    df_ir_out = df_ir_out.set_index('date')

    return df_ir_out


def read_pyrgeometer(ipath_in):
    """
    Function to read pyranometer data and put them into a pandas dataframe

    :param ipath_in: input path where IR thermometer data is located
    :return df_pyr_out: pandas dataframe with IR thermometer data
    """

    # Read data
    file_pyr = os.path.join(ipath_in, 'pyr_data_all.dat')
    col_name = ['year', 'month', 'day', 'hour', 'minute', 'second', 'freq', 'num_sample', 'U1', 'U2', 'T1', 'T2']
    df_pyr_out = pd.read_csv(file_pyr, header=None, sep='\s+', on_bad_lines='skip', skip_blank_lines=True,
                             usecols=range(12), names=col_name)
    df_pyr_out.drop_duplicates(inplace=True)

    # Set up datetime index
    date_new = pd.to_datetime(df_pyr_out.loc[:, ['year', 'month', 'day', 'hour', 'minute', 'second']]).dt.round('S')
    df_pyr_out.drop(['year', 'month', 'day', 'hour', 'minute', 'second'], axis=1, inplace=True)
    df_pyr_out.insert(0, 'date', date_new.values)
    df_pyr_out = df_pyr_out.set_index('date')

    # Drop not need variables from dataframe
    df_pyr_out.drop(['freq', 'num_sample'], axis=1, inplace=True)
    df_pyr_out.rename(columns={'U1': 'U1_pyr', 'T1': 'T1_pyr', 'U2': 'U2_pyr', 'T2': 'T2_pyr'})

    return df_pyr_out


if __name__ == "__main__":
    main()
