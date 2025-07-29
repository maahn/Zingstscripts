import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq, irfft


def main():
    ipath = 'data/'

    # Read data
    df = read_raw_data(ipath)

    # Apply calibration
    df = apply_calibration(df)
    ds = df.to_xarray()
    data = ds['s_16'].sel(time=slice('2023-07-19', '2023-07-19'))

    #an, bn, cn = calculate_fourier_coeff(np.array(data))
    an, bn = dft(np.array(data))

    pn = an**2 + bn**2
    nday = int(len(data)/144)
    n_omega = (2 * np.pi / (nday*24)) * np.arange(len(an))
    noise = n_omega**(-5/3)

    plt.scatter(n_omega, pn/pn[0])
    plt.scatter(n_omega, noise/noise[1])
    plt.yscale('log')
    plt.xscale('log')
    plt.show()


    mask = n_omega > 8
    an[mask], bn[mask] = 0, 0

    y_rec = inverse_dft(an, bn, len(data))
    t = data.time.values
    plt.plot(t, y_rec)
    plt.plot(t, data)
    plt.show()


def calculate_fourier_coeff(val_in):
    # Calculate coefficients
    coeff_fourier = rfft(val_in)

    # Normalize coefficients
    coeff_fourier = (1 / len(coeff_fourier)) * coeff_fourier

    return np.real(coeff_fourier), np.imag(coeff_fourier), coeff_fourier


def test_signal():

    # Create a simple signal: a sum of two sine waves
    Fs = 144  # Sampling rate
    T = 24 / Fs  # Sampling interval
    t = np.arange(0, 24+T/2, T)  # Time vector (1 second)
    f1, f2 = 10/24, 30/24  # Frequencies in Hz

    # Create a simple signal: a sum of two sine waves
    Fs = 144  # Sampling rate
    T = 24 / Fs  # Sampling interval
    t = np.arange(0, 24+T/2, T)  # Time vector (1 second)
    f1, f2 = 10/24, 30/24  # Frequencies in Hz

    # Composite signal
    y = (np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(2 * np.pi * f2 * t))
    return t, y


def inverse_dft(a_n, b_n, N):
    dt = 24 / N
    t = (np.arange(N) * dt)
    f_reconstructed = np.zeros(N)

    omega0 = 2 * np.pi / 24  # fundamental frequency for 24-hour period

    n_half = len(a_n)
    for n in range(0, n_half):
        f_reconstructed += a_n[n] * np.cos(omega0 * n * t) + b_n[n] * np.sin(omega0 * n * t)

    return f_reconstructed


def dft(signal):
    N = len(signal)
    dt = 24 / N
    omega = 2 * np.pi / (N * dt)

    n_half = N // 2 + 1
    a_n = np.zeros(n_half)
    b_n = np.zeros(n_half)

    for n in range(n_half):
        t = np.arange(N) * dt
        cos_term = np.cos(omega * n * t)
        sin_term = np.sin(omega * n * t)

        a = np.dot(signal, cos_term)
        b = np.dot(signal, sin_term)

        scale = 2 / N
        a_n[n] = a * scale
        b_n[n] = b * scale

    a_n[0] /= 2
    b_n[0] = 0
    if N % 2 == 0:
        a_n[-1] /= 2
        b_n[-1] = 0

    return a_n, b_n


def apply_calibration(df_out):

    # Dictionary to rename variables
    rename_dict = {
        'val_0': 's_10',
        'val_1': 's_16',
        'val_2': 'f_lw_dn',
        'val_3': 'f_lw_up',
        'val_4': 'f_dn',
        'val_5': 'f_up',
        'val_6': 'T',
        'val_7': 'f_sw_up',
        'val_8': 'f_sw_dn'
    }
    df_out.rename(columns=rename_dict, inplace=True)

    # Apply calibration
    df_out['s_16'], df_out['s_10'] = df_out['s_16'] * 16.0823, df_out['s_10'] * 16.3265
    df_out['f_dn'] = df_out['f_dn'] * 51.3 + (5.68 * 10 ** -8 * (273.15 + df_out['T']) ** 4) - 0.7
    df_out['f_up'] = df_out['f_up'] * 38.3 + (5.68 * 10 ** -8 * (273.15 + df_out['T']) ** 4) - 0.7

    # Calculate down from net-up
    df_out['f_lw_dn'] = df_out['f_dn'] - df_out['f_sw_dn']
    df_out['f_lw_up'] = df_out['f_up'] - df_out['f_sw_up']

    # Remove not need column
    df_out.drop(['val_9'], axis=1, inplace=True)

    return df_out


def read_raw_data(ipath):

    # Initialize empty dataframe and variables containing data information
    df_out = pd.DataFrame()
    day, month, year = np.nan, np.nan, np.nan

    # Read file in ipath
    file_list = sorted(os.listdir(ipath))

    for file in file_list:

        if not file.endswith('.TXT'):
            continue

        with open(os.path.join(ipath, file), 'rb') as f_in:
            for nl, line_byte in enumerate(f_in):
                # Skip first line
                if nl == 0:
                    continue

                # Replace øC with C
                try:
                    line = line_byte.decode('latin1').strip().replace('øC', 'C')
                except UnicodeDecodeError:
                    continue  # skip unreadable lines

                # Find date of lines below
                if line.startswith('DATUM:'):
                    day, month, year = line.split(':')[1].strip().strip("'").split('.')[:]
                # Read actual fata
                else:
                    # Read time
                    hour, minute, second = line.split(' ')[0].split(':')
                    # Split data
                    string_split_values = re.split(r' 0[0-9]: ', line)[1::]

                    # Split columns of each line and add nan if entry not convertible to float
                    values = []
                    for column in string_split_values:
                        try:
                            values.append(float(column.split(' ')[0]))
                        except ValueError:
                            values.append(np.nan)

                    # Create timestamp
                    data_line_dict = {'year': 2000 + int(year), 'month': int(month), 'day': int(day), 'hour': int(hour),
                                      'minute': int(minute), 'second': int(second)}

                    # Write values into dict
                    for nv, val in enumerate(values):
                        data_line_dict[f'val_{nv}'] = float(val)

                    # Create new dataset with one row
                    new_row = pd.DataFrame(data_line_dict, index=[0])

                    # Append row to existing dataframe
                    df_out = pd.concat([new_row, df_out.loc[:]]).reset_index(drop=True)

    # Revers order of variables in dataframe
    df_out = df_out.iloc[::-1]

    # Create proper pandas timestamp
    date_new = pd.to_datetime(df_out.loc[:, ['year', 'month', 'day', 'hour', 'minute', 'second']]).dt.round('S')

    # Drop old and insert new time information
    df_out.drop(['year', 'month', 'day', 'hour', 'minute', 'second'], axis=1, inplace=True)
    df_out.insert(0, 'time', date_new.values)
    df_out = df_out.set_index('time')

    # Remove data that contains invalid data
    df_out.dropna(inplace=True)

    # Check for full days, i.e. 144 timesteps per day
    counts_per_day = df_out.groupby(df_out.index.date).size()
    valid_days = counts_per_day[counts_per_day == 144].index
    df_out = df_out[df_out.index.normalize().isin(valid_days)]

    return df_out


if __name__ == "__main__":
    main()
