import os
import urllib3
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import numpy as np

OPAHT_RS = 'data/radiosonde_lrt'
http = urllib3.PoolManager()


def main():

    # Station identifier (10184 is Greifswald)
    station = '10184'

    # Chose time of radiosonde
    year, month, day, time = '2023', '08', '01', '00'

    # Download and prepare radiosonde data
    download_process_radiosonde(year, month, day, time, station)


def download_process_radiosonde(year, month, day, time, station):

    # T
    alt_levels_intp = [20000., 19000., 18000., 17000., 16000., 15000., 14000., 13000., 12000.0, 11000.0, 10000.0,
                       9000.0, 8000.0, 7000.0, 6000.0, 5500.0, 5000.0, 4500.0, 4000.0, 3500.0, 3000.0, 2500.0, 2000.0,
                       1800.0, 1600.0, 1400.0, 1200.0, 1000.0, 800.0, 600.0, 400.0, 200.0, 0.0]

    # Load radiosonde http into memory
    url_radiosonde = f'http://weather.uwyo.edu/cgi-bin/sounding?region=europe&TYPE=TEXT%3ALIST' \
                     f'&YEAR={year}&MONTH={month}&FROM={day}{time}&TO={day}{time}&STNM={station}'

    # Query radiosonde http (will use up to 100 tries) if necessary
    for n in range(100):
        html_resp = http.request("GET", url_radiosonde)
        soup = BeautifulSoup(html_resp.data, "lxml")
        try:
            str(soup.find_all("pre")[0].contents[0])
        except IndexError:
            continue
        else:
            radiosonde_data_raw = str(soup.find_all("pre")[0].contents[0])
            break

    # Convert radiosonde http into pandas dataframe
    header_names = [s.strip() for s in radiosonde_data_raw.split('\n')[2].split('  ')[1::]]
    df = pd.read_csv(StringIO(radiosonde_data_raw), skiprows=5, header=None, sep='\s+', names=header_names).dropna()

    # Celsius to Kelvin
    df['TEMP'] = df['TEMP'] + 273.15

    # Interpolate radiosonde data to distinct vertical levels to speed up the libRadTran simulations
    var_new = {}
    for var in ['PRES', 'TEMP', 'RELH']:
        var_new[var] = np.interp(alt_levels_intp, df['HGHT'].values, df[var].values)

    # Write interpolated radiosonde data into libRadTran format
    df_out = pd.DataFrame(var_new)
    if not os.path.isfile(f'{OPAHT_RS}/lib_RS_{station}_{year}{month}{day}_{time}.dat'):
        df_out.to_csv(f'{OPAHT_RS}/lib_RS_{station}_{year}{month}{day}_{time}.dat', index=False, header=False, sep='\t')


if __name__ == "__main__":
    main()
