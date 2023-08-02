"""
Created on Thu Jul 23 2022
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
import struct

##################################################
print('##################')
print('Before you start:')
print('please put your input files into a directory called input_data and create a directory output_data')
print('please check if the last row in the input file is empty -> if yes, delete it')
print('##################')

if len(sys.argv)==1:
    print('Usage python datenauslesen_Boden.py inputfile')
    print('type the name of your inputfile with ending')
    sys.exit()

inputfile=str(sys.argv[1])



#### read file
#-------------
datei=open('input_data/'+inputfile,'r',encoding='utf-8',errors='ignore')
datei.readline()
array=datei.readlines()

dayind=[]
date=[]
pyran_down=[]   #already calibrated
pyran_up=[]     #already calibrated
pyrad_down_raw=[]
pyrad_up_raw=[]
pt=[]
x10_raw=[]
x16_raw=[]

n=0

for i in range(len(array)):
    if array[i][0:5]=='DATUM':
        Datum=array[i][len(array[i])-9:len(array[i])+1]
        print(Datum)
        dayind.append(i-n)    #index where new day starts
        n=n+1
    else:
        splitarr=array[i].split(' ')
        date.append(parser.parse(str(Datum)+' '+splitarr[0]))
        #ädaystr.append(Datum)
        if splitarr[splitarr.index('00:')+1]=='':
            pyran_down.append('nan')
        else:
            pyran_down.append(splitarr[splitarr.index('00:')+1])
        if splitarr[splitarr.index('01:')+1]=='':
            pyran_up.append('nan')
        else:
            pyran_up.append(splitarr[splitarr.index('01:')+1])
        if splitarr[splitarr.index('02:')+1]=='':
            pyrad_down_raw.append('nan')
        else:
            pyrad_down_raw.append(splitarr[splitarr.index('02:')+1])
        if splitarr[splitarr.index('03:')+1]=='':
            pyrad_up_raw.append('nan')
        else:
            pyrad_up_raw.append(splitarr[splitarr.index('03:')+1])
        if splitarr[splitarr.index('04:')+1]=='':
            pt.append('nan')
        else:
            pt.append(splitarr[splitarr.index('04:')+1])
        if splitarr[splitarr.index('05:')+1]=='':
            x10_raw.append('nan')
        else:
            x10_raw.append(splitarr[splitarr.index('05:')+1])
        if splitarr[splitarr.index('06:')+1]=='':
            x16_raw.append('nan')
        else:
            x16_raw.append(splitarr[splitarr.index('06:')+1])
        ###### old surface flux plates
        #if splitarr[splitarr.index('07:')+1]=='':
        #    x10old_raw.append('nan')
        #else:
        #    x10old_raw.append(splitarr[splitarr.index('07:')+1])
        #if splitarr[splitarr.index('08:')+1]=='':
        #    x16old_raw.append('nan')
        #else:
        #    x16old_raw.append(splitarr[splitarr.index('08:')+1])

        
### neglect first and last day, because they probably are not complete -> for Fourier you need 144 data points
pyran_down=np.array(pyran_down[dayind[1]:dayind[len(dayind)-1]],dtype='float')
pyran_up=np.array(pyran_up[dayind[1]:dayind[len(dayind)-1]],dtype='float')
pyrad_down_raw=np.array(pyrad_down_raw[dayind[1]:dayind[len(dayind)-1]],dtype='float')
pyrad_up_raw=np.array(pyrad_up_raw[dayind[1]:dayind[len(dayind)-1]],dtype='float')
pt=np.array(pt[dayind[1]:dayind[len(dayind)-1]],dtype='float')
x10_raw=np.array(x10_raw[dayind[1]:dayind[len(dayind)-1]],dtype='float')
x16_raw=np.array(x16_raw[dayind[1]:dayind[len(dayind)-1]],dtype='float')
#x10old_raw=np.array(x1old0_raw[dayind[1]:dayind[len(dayind)-1]],dtype='float')
#x16old_raw=np.array(x16old_raw[dayind[1]:dayind[len(dayind)-1]],dtype='float')

ds=xr.Dataset(
    data_vars=dict(
        pyran_down=(['date'],pyran_down),
        pyran_up=(['date'],pyran_up),
        pyrad_down_raw=(['date'],pyrad_down_raw),
        pyrad_up_raw=(['date'],pyrad_up_raw),
        pt=(['date'],pt),
        x10_raw=(['date'],x10_raw),
        x16_raw=(['date'],x16_raw),
        #x10old_raw=(['date'],x10old_raw),
        #x16old_raw=(['date'],x16old_raw),
    ),
    coords=dict(
        date=date[dayind[1]:dayind[len(dayind)-1]],
    ),
    attrs=dict(description='rawdata and calibrated data of pyranometer, pyradiometer and surface flux'),
    )

ds['pyran_down'].attrs={'units':'W','long_name':'pyranometer downward radiation (already calibrated)'}
ds['pyran_up'].attrs={'units':'W','long_name':'pyranometer upward radiation (already calibrated)'}
ds['pyrad_down_raw'].attrs={'units':'mV','long_name':'pyradiometer downward radiation'}
ds['pyrad_up_raw'].attrs={'units':'mV','long_name':'pyradiometer upward radiation'}
ds['pt'].attrs={'units':'°C','long_name':'sensor temperature of pyradiometer'}
ds['x10_raw'].attrs={'units':'mV','long_name':'surface flux upper plate'}
ds['x16_raw'].attrs={'units':'mV','long_name':'surface flux lower plate'}
#ds['x10old_raw'].attrs={'units':'mV','long_name':'surface flux upper plate (old)'}
#ds['x16old_raw'].attrs={'units':'mV','long_name':'surface flux lower plate (old)'}

ds=ds.dropna('date',how='any')

#### check if the dataset is complete (all days should have 144 measurement points
nrperday=ds.resample(date='1D').count()
print(nrperday)

ds.to_netcdf('output_data/'+inputfile.split('_')[0]+'_rawdata_Boden.nc',format='NETCDF4')

#### calibration and add to dataset
#----------------------------------
# ds['pyrad_down']=ds.pyrad_down_raw*...+...




