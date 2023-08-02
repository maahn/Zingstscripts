"""
Created on Thu Jul 11 2023

@author: Henriette Gebauer (for questions write to henriette.gebauer@gmx.de)
"""

import numpy as np
from numpy import loadtxt
import matplotlib.pyplot as plt
import sys
from io import StringIO
from datetime import datetime
from dateutil import parser
import pandas as pd
import xarray as xr
import glob

print('##################')
print('Before you start: please put your input files into a directory called input_data and create a directory called output_data')
print('##################')

###############################################################
if len(sys.argv)==1:
    print('Usage python auslesen_Windmast.py date')
    print('type the recent date in YYYYMMDD')

Datum=str(sys.argv[1])

#### read in all rawdata files and combine to 1 large dataset
print('Start reading files')
print('-------')

all_files=sorted(glob.glob('input_data/'+'/*log'))

rawdata_app=[]

for filename in all_files:
    print(filename)

    code=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(0))
    time=pd.to_datetime(np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(1), dtype=str))
    anemometer1=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(2))
    anemometer2=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(3))
    anemometer3=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(4))
    anemometer4=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(5))
    anemometer5=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(6))
    temp1=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(7))
    feuchte1=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(8))
    temp2=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(9))
    feuchte2=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(10))
    temp3=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(11))
    feuchte3=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(12))
    temp4=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(13))
    feuchte4=np.genfromtxt(filename, skip_header=6, delimiter=';', usecols=(14))

#### Calibration and convert numpy dataset to xarray dataset
        # insert calibration factors here
        # like in example:
        # anem1=(['date'],anemometer1*calibfactor+calibfactor),
    
    calibdata=xr.Dataset(
        data_vars=dict(
            anem1=(['date'],anemometer1),
            anem2=(['date'],anemometer2),
            anem3=(['date'],anemometer3),
            anem4=(['date'],anemometer4),
            anem5=(['date'],anemometer5),
            temp1=(['date'],temp1),
            temp2=(['date'],temp2),
            temp3=(['date'],temp3),
            temp4=(['date'],temp4),
            feuchte1=(['date'],feuchte1),
            feuchte2=(['date'],feuchte2),
            feuchte3=(['date'],feuchte3),
            feuchte4=(['date'],feuchte4),
        ),
        coords=dict(
            date=time,
        ),
        attrs=dict(description='windmast raw data'),
    )

    calibdata['anem1'].attrs={'units':'m/s', 'long_name':'windvelocity height 1'}
    calibdata['anem2'].attrs={'units':'m/s', 'long_name':'windvelocity height 2'}
    calibdata['anem3'].attrs={'units':'m/s', 'long_name':'windvelocity height 3'}
    calibdata['anem4'].attrs={'units':'m/s', 'long_name':'windvelocity height 4'}
    calibdata['anem5'].attrs={'units':'m/s', 'long_name':'windvelocity height 5'}
    calibdata['temp1'].attrs={'units':'K', 'long_name':'temperature height 2'}
    calibdata['temp2'].attrs={'units':'K', 'long_name':'temperature height 3'}
    calibdata['temp3'].attrs={'units':'K', 'long_name':'temperature height 4'}
    calibdata['temp4'].attrs={'units':'K', 'long_name':'temperature height 5'}
    calibdata['feuchte1'].attrs={'units':'%', 'long_name':'humidity height 2'}
    calibdata['feuchte2'].attrs={'units':'%', 'long_name':'humidity height 3'}
    calibdata['feuchte3'].attrs={'units':'%', 'long_name':'humidity height 4'}
    calibdata['feuchte4'].attrs={'units':'%', 'long_name':'humidity height 5'}

    rawdata_app.append(calibdata)
   
print('End of reading files')

calibdata_complete=xr.concat(rawdata_app,dim='date')
calibdata_complete.to_netcdf('output_data/'+Datum+'_calibrated_rawdata_windmast.nc',format='NETCDF4')

#### average over selected time period (10T=10Min)

print('Calculate 10 minute averages')
calibdata_mean=calibdata_complete.resample(date='10T',closed='left',label='right').mean()
calibdata_mean.to_netcdf('output_data/'+Datum+'_mean_values_windmast.nc',format='NETCDF4')



