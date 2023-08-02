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
from scipy.signal


########################################################################################################
############### read in netCDF files with raw data  ###########
########################################################################################################
print('!!!!!Before you start: please check if calibration is already complete!!!!!')
print('###########################################################################')
print('read in netCDF files with raw data')
all_files=sorted(glob.glob('output_data/'+'/2020*nc'))
print(all_files)

assert len(all_files) >= 1, 'output_data/'+'/2020*nc'
rawdata_app=[]

# if you don't want to use all files -> comment out this part
for filename in all_files:
    rawdata_file=xr.open_dataset(filename)
    rawdata_app.append(rawdata_file)
rawdata_complete=xr.concat(rawdata_app, dim='date')
#
# and use this part
#filename='output_data/... .nc'
#rawdata_file=xr.open_dataset(filename)
#

date=rawdata_complete.date

#### calibration to physical properties
rawdata_complete['v']=rawdata_complete.x*0.01
v=rawdata_complete.v
rawdata_complete['u']=rawdata_complete.y*0.01
u=rawdata_complete.u
rawdata_complete['w']=rawdata_complete.z*0.01
w=rawdata_complete.w
rawdata_complete['Temp']=rawdata_complete.T*0.01+273.15
Temp=rawdata_complete.Temp
#rawdata_complete['rho']=
#rho=rawdata_complete.rho
#rawdata_complete['q']=...rawdata_complete.e4
#q=
#rawdata_complete['CO2']=...rawdata_complete.e3
#CO2=


########################################################################################################
############### Fast Fourier transformation  ###########
########################################################################################################
print('##### Fourier transformation #####')
print('----------------------------------')
lfft=int(input('insert length of FFT (integer, n**2): '))
starttime=input('insert your start time in format YYYY-MM-DDTHH:MM (T is a capital letter): ')
endtime=input('insert your end time in the same format: ')
Datum=starttime[0:10]

sampling_freq=int(input('insert sampling frequency (hz): '))


FFT_data=rawdata_complete.sel(date=slice(starttime,endtime))

print('--------------------------------------------------------')
print('select two data arrays, for which the FFT should be done')
print('--------------------------------------------------------')
input_x=input('first data array, e.g. x=FFT_data.u: ')
input_y=input('second data array, e.g. y=FFT_data.v: ')
exec(input_x)
exec(input_y)

x=FFT_data.u
y=FFT_data.v

print('length of data array: ', len(x), 'divided by length of window:', lfft, 'should be > 10: ',len(x)/lfft)

"""
- Es werden zwei Datenreihen x und y für die FFT verwendet
- Die FFT wird für verschiedene Teilabschnitte von x und y durchgeführt, die jeweils die Länge LFFT haben.
- Dazu wird das Fenster schrittweise um LFFT/8 Stellen verschoben.
- Die Länge von x bwz. y sollte > 10 * LFFT sein.
- Pro Fenster wird erst der Mittelwert über den Fensterabschnitt gebildet.
- Dieser wird von den einzelnen Datenwerten abgezogen, dann Multiplikation mit Hanning Fenster. Wird auf den geraden Stellen eines neuen arrays (xx, yy) gespeichert. (reelle Datenwerte)
- Alle ungeraden stellen werden 0 gesetzt. (komplexe Datenwerte, hier 0)
"""

    fstep, lx = scipy.signal.welch(x, nperseg=LFFT, fs=sampling_freq, detrend=scipy.signal.detrend)
    fstep, ly = scipy.signal.welch(y, nperseg=LFFT, fs=sampling_freq, detrend=scipy.signal.detrend)

    fstep,s = scipy.signal.csd(x,y, fs=sampling_freq, nperseg=LFFT, 
                    detrend=scipy.signal.detrend)
    #nur der Realteil wird fürs Leistungsspektrum gebraucht (siehe auch scipy welch source code)
    #Das Vorzeichen liegt an der Eingangsreihgenfolge (va1 var2 oder var2 var1), ist als irrelevant
    co = np.abs(np.real((s)))


Datensatz=xr.Dataset(
    data_vars=dict(
        lx=(['fstep'],lx),
        ly=(['fstep'],ly),
        co=(['fstep'],co),
    ),
    coords=dict(
        fstep=fstep,
    ),
    attrs=dict(description='FFT USA and LICOR')
)

Datensatz.to_netcdf('output_data/FFT_output/'+Datum+'_FFT_USA_LICOR.nc',format='NETCDF4')
