"""
Created on Thu Jul 21 2022
Latest update: Mon Jul 17 2023

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
print('Before you start: please put your input files into a directory called input_data and create a directory called output_files')
print('##################')

###############################################################
if len(sys.argv)==1:
    print('Usage python mitteln_Coras.py date')
    print('type the recent date in YYYYMMDD')

Datum=str(sys.argv[1])   

#### read in all rawdata files and combine to 1 large dataset
print('Start reading files')
print('-------')

all_files=sorted(glob.glob('input_data/'+'/*dat'))

rawdata_app=[]

for filename in all_files:
    print(filename)
    datei=open(filename,'r')
    data=datei.readlines()

    counts=np.zeros(shape=(len(data),1024))
    inttime=np.zeros(len(data))
    date=[]
    pixnr=np.arange(1,1025,1)
    for i in range(len(data)):
        measpoint=data[i].split(' ')
        date.append(parser.parse(measpoint[2]+'.'+measpoint[1]+'.'+measpoint[0]+' '+measpoint[6]+':'+measpoint[7]+':'+measpoint[8],dayfirst=True))
        #inttime[i]=int(measpoint[12]) ### here 11, in other files 12; you have to try it out
        n=0
        for k in range(13,len(measpoint)):
            if measpoint[k]!='':
                counts[i,n]=int(measpoint[k])
                n=n+1
            else:
                continue
              
    Datensatz=xr.Dataset(
        data_vars=dict(
            counts=(['date','pixnr'],counts),
            inttime=(['date'],inttime),
        ),
        coords=dict(
            date=date,
            pixnr=pixnr,
        ),
        attrs=dict(description='CORAS raw data'),
    )

    Datensatz['counts'].attrs={'units':' ', 'long_name':'pixel counts'}
    Datensatz['inttime'].attrs={'units':'ms', 'long_name':'integrated time'}

    rawdata_app.append(Datensatz)

print('-------')
print('End of reading files')


rawdata_complete=xr.concat(rawdata_app, dim='date')

#### average over selected time period (10T=10Min)
print('-------')
print('Calculate 10 minute averages')

rawdata_mean=rawdata_complete.resample(date='10T',closed='left',label='right').mean()
rawdata_mean.to_netcdf('output_data/'+Datum+'_mean_values_Coras.nc',format='NETCDF4')

"""
to select a value (e.g. the 10th mean of pixel nr 500):
rawdata_mean.sel(pixnr=500,date=rawdata_mean.date[9])
please pay attention: in the terminal output it will be rounded, otherwise use:
rawdata_mean.sel(pixnr=500,date=rawdata_mean.date[9]).counts.values
"""

testdata_mean=rawdata_mean.sel(pixnr=500,date=slice('2012-06-05T17:00','2012-06-05T18:00'))
testdata_mean.to_netcdf('output_data/'+Datum+'_mean_values_Coras_500nm.nc',format='NETCDF4')
