"""
Created on Thu Jul 21 2022
Last update: Wed Jul 12 2023

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


##################################################
print('Before you start: check, if your last data point in the input file is complete, else copy the missing part manually from following input file! AND Create two directories named input_data and output_data and in output_data you need a directory mean_values!')
print('--------')
print('Did you check your input file and create directories? (yes/no)')
x=input()
if x!='yes':
    sys.exit()

##################################################
if len(sys.argv)==1:
    print('Usage python datenauslesen_USA_LICOR.py filename date')
    print('type the name of your file with ending where written filename')
    print('type the date of your datafile in YYYYMMDD')
    sys.exit()

filename=str(sys.argv[1])
Datum=str(sys.argv[2])


#### read whole file
datei=open('input_data/'+filename,'r')
array=datei.readlines()

llstring1=20
llstring23=42

Zeile1=[]
Zeile2=[]
Zeile3=[]
dummy=[]
dummyind=[]

start=False
end=False
i=0
while start==False:
    if array[i][0]=='T':
        start=True
        startind=i
    else:
        i=i+1

i=0
while end==False:
    if array[len(array)-1-i][0]=='T':
        end=True
        endind=len(array)-1-i-3
    else:
        i=i+1

for i in range(startind,endind+1):
    if (array[i][0]=='T') & (len(array[i])==llstring1):
        if (array[i+1][0:3]=='M:x') & (array[i+2][0:3]=='M:e') & (len(array[i+1])==len(array[i+2])==llstring23) & (array[i+3][0:2]!='E:'):
            Zeile1.append(array[i])
            Zeile2.append(array[i+1])
            Zeile3.append(array[i+2])
            i=i+3
    elif array[i][0]=='M':
            continue
    else:
        dummy.append(array[i])
        dummyind.append(i)
    
#sys.exit()
#### define empty lists
date=[]
x=[]
y=[]
z=[]
T=[]
e1=[]
e2=[]
e3=[]
e4=[]
        
#### fill lists with data
for i in range(len(Zeile1)):
  
    date.append(parser.parse(Zeile1[i][2:19]))
        
    Z2split=Zeile2[i].split(' ')
    x.append(Z2split[Z2split.index('y')-1])
    y.append(Z2split[Z2split.index('z')-1])
    z.append(Z2split[Z2split.index('t')-1])
    T.append(Z2split[len(Z2split)-1])
    
    Z3split=Zeile3[i].split('=')
    e1i=Z3split[1].split(' ')
    e2i=Z3split[2].split(' ')
    e3i=Z3split[3].split(' ')
    e1.append(e1i[len(e1i)-2])
    e2.append(e2i[len(e2i)-2])
    e3.append(e3i[len(e3i)-2])
    e4.append(Z3split[len(Z3split)-1])

#### convert lists to np arrays   
x=np.array(x,dtype=float)
y=np.array(y,dtype=float)
z=np.array(z,dtype=float)
T=np.array(T,dtype=float)
e1=np.array(e1,dtype=float)
e2=np.array(e2,dtype=float)
e3=np.array(e3,dtype=float)
e4=np.array(e4,dtype=float)

Datensatz=xr.Dataset(
    data_vars=dict(
        x=(['date'], x,),
        y=(['date'], y,),
        z=(['date'], z,),
        T=(['date'], T,),
        e1=(['date'], e1),
        e2=(['date'], e2),
        e3=(['date'], e3),
        e4=(['date'], e4),
    ),
    coords=dict(
        date=date,
    ),
    attrs=dict(description='USA and LICOR raw data'),
)

Datensatz['x'].attrs={'units':'cm/s', 'long_name':'wind_velocity in x direction'}
Datensatz['y'].attrs={'units':'cm/s', 'long_name':'wind_velocity in y direction'}
Datensatz['z'].attrs={'units':'cm/s', 'long_name':'wind_velocity in z direction'}
Datensatz['T'].attrs={'units':'1/100°C', 'long_name':'acustic air temperature'}
Datensatz['e1'].attrs={'units':' ', 'long_name':'empty channel'}
Datensatz['e2'].attrs={'units':' ', 'long_name':'empty channel'}
Datensatz['e3'].attrs={'units':'50000=20mMol/(m^3) ', 'long_name':'CO2-content'}
Datensatz['e4'].attrs={'units':'50000=1000mMol/(m^3) ', 'long_name':'H2O-content'}

print(Datensatz)

Datensatz.to_netcdf('output_data/'+Datum+'_rawdata-USA_LICOR.nc',format='NETCDF4')

#print('---------')
#print('Errors in the following measurement points')
#print(dummy)
