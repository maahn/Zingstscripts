"""
Created on Thu Jul 21 2022
Last update: Wed Jul 12 2023

@author: Henriette Gebauer (for questions write to henriette.gebauer@gmx.de)
"""

import numpy as np
from numpy import loadtxt
import matplotlib.pyplot as plt
import math
import sys
from io import StringIO
from datetime import datetime
from dateutil import parser
from netCDF4 import Dataset, num2date
import xarray as xr
import glob

###############################################################
if len(sys.argv)==1:
    print('Usage python Mittelung_10min_USA_LICOR.py date')
    print('type the recent date in YYYYMMDD')

Datum=str(sys.argv[1])


############### read in netCDF files with raw data  ###########
all_files=sorted(glob.glob('output_data/'+'/2020*nc'))

rawdata_app=[]

for filename in all_files:
    rawdata_file=xr.open_dataset(filename)
    rawdata_app.append(rawdata_file)
rawdata_complete=xr.concat(rawdata_app, dim='date')

date=rawdata_complete.date
x=rawdata_complete.x
y=rawdata_complete.y
z=rawdata_complete.z
T=rawdata_complete.T
e1=rawdata_complete.e1
e2=rawdata_complete.e2
e3=rawdata_complete.e3
e4=rawdata_complete.e4

#### calibration to physical properties
rawdata_complete['v']=x*0.01
v_all=rawdata_complete.v
rawdata_complete['u']=y*0.01
u_all=rawdata_complete.u
rawdata_complete['w']=z*0.01
w_all=rawdata_complete.w
rawdata_complete['Temp']=T*0.01+273.15
Temp_all=rawdata_complete.Temp
rawdata_complete['rho']=100000/(287.05*Temp_all)                  # Dichte=po/R*T
rho_all=rawdata_complete.rho
rawdata_complete['q']=rawdata_complete.e4*3.6/rho_all/10000       # spez.Feuchte in [g/kg]
q_all=rawdata_complete.q
rawdata_complete['CO2']=rawdata_complete.e3*176/rho_all/10000     # [mg/kg]
CO2_all=rawdata_complete.CO2


#### average over selected time period (10T=10Min)
rawdata_mean=rawdata_complete.resample(date='10T',closed='left', label='right').mean()
#datapoints=rawdata_file.resample(date='1T').count()

rawdata_mean['u'].attrs={'units':'m/s', 'long_name':'zonal wind component'}
rawdata_mean['v'].attrs={'units':'m/s', 'long_name':'meridional wind component'}
rawdata_mean['w'].attrs={'units':'m/s', 'long_name':'vertical wind component'}
rawdata_mean['Temp'].attrs={'units':'K', 'long_name':'acustic air temperature'}
rawdata_mean['rho'].attrs={'units':'g/m³', 'long_name':'air density'}
rawdata_mean['q'].attrs={'units':'g/kg', 'long_name':'specific humidity'}
rawdata_mean['CO2'].attrs={'units':'mg/kg', 'long_name':'CO2 content'}

u=rawdata_mean.u
v=rawdata_mean.v
w=rawdata_mean.w
Temp=rawdata_mean.Temp
rho=rawdata_mean.rho
q=rawdata_mean.q
CO2=rawdata_mean.CO2

rawdata_mean.to_netcdf('output_data/mean_values/'+Datum+'_mean_values-USA_LICOR.nc',format='NETCDF4')

print('----------------------------')
print('first date:')
print(date[0])
print('last date:')
print(date[len(date)-1])
print('----------------------------')
print('If minutes of first/last date not a multiple of 10 then neglect first/last mean value!')
print('############################')

#sys.exit()

#### Check if it looks realistic:
#Temp.plot()
#plt.show()

print('--------------------')
print('date')
print(rawdata_mean.date)
print('--------------------')
print('zonal wind component')
print(u)
print('--------------------')
print('meridional wind component')
print(v)
print('--------------------')
print('vertical wind component')
print(w)
print('--------------------')
print('air temperature')
print(Temp)
print('--------------------')
print('air density')
print(rho)
print('--------------------')
print('specific humidity')
print(q)
print('--------------------')
print('CO2 concentration')
print(CO2)

