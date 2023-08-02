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
from scipy.fft import fft, ifft

########################################################################################################
############### definition of functions ###########
########################################################################################################

########################################################################################################
# Fourier Transformation
########################################################################################################

"""
def fouriercoeff_Olli(datain):
    a=[]
    f_total=0
    b=[]
    for i1 in range(len(datain)):
        f_total=f_total+datain[i1]
    a.append(1/len(datain)*f_total)
    b.append(0)
    print('loop1 done')
    for i in np.arange(1,(len(datain)/2)):
        print(i)
        a_sum=0
        b_sum=0
        for i2 in range(len(datain)):
            a_sum=a_sum+datain[i2]*np.cos(i*2*(np.pi/len(datain))*i2) #2pi/24h
            b_sum=b_sum+datain[i2]*np.sin(i*2*(np.pi/len(datain))*i2)
        a.append(2/len(datain) * a_sum)
        b.append(2/len(datain) * b_sum)
    f_a_n_2=0
    print('loop2 done')
    for i4 in range(len(datain)):
        f_a_n_2=f_a_n_2+datain[i4]*np.cos(len(datain)/2*(2*np.pi/len(datain))*i4)
    a.append(1/len(datain)*f_a_n_2)
    b.append(0)
    print('loop3 done')
    return a,b
"""

# discrete fourier transformation
def fouriercoeff(datain,deltat):
    ncoeff=int(0.5*len(datain)+1)
    print('nr of fourier coefficients: ',ncoeff)
    print('nr of measurement points: ',len(datain))
    Fcoeff=np.zeros(shape=(ncoeff,2))
    ti=np.arange(1,len(datain)+1,1)*deltat
    omega=2*np.pi/(len(datain)*deltat)
    
    Fcoeff[0,0]=np.nanmean(datain)
    Fcoeff[0,1]=0
    for j in range(1,ncoeff):
        print(j,' of ',ncoeff-1)
        arr=np.zeros(len(datain))
        brr=np.zeros(len(datain))
        for i in range(len(datain)):
            arr[i]=datain[i]*np.cos(j*omega*ti[i])
            brr[i]=datain[i]*np.sin(j*omega*ti[i])
        if j==ncoeff-1:
            Fcoeff[j,0]=np.nanmean(arr)
            Fcoeff[j,1]=0
        else:
            Fcoeff[j,0]=2*np.nanmean(arr)
            Fcoeff[j,1]=2*np.nanmean(brr)
            continue
  
        return Fcoeff

########################################################################################################
# Backward Fourier Transformation
########################################################################################################
def fourierback(a,b,datain):
    x=[]
    for i in range(len(datain)):
        f_n_2=0
        for i5 in range(int(len(datain)/2 + 1)):
            f_n_2=f_n_2+(a[i5]*np.cos(i5*2*np.pi/len(datain)*i)+b[i5]*np.sin(i5*2*np.pi/len(datain)*i))
        x.append(f_n_2)
    return x


########################################################################################################
# Soubroutine four1 from fortran script for FFT
########################################################################################################
def four1(data,nn,isign):
    n=2*nn
    j=0
    for i in range(0,n,2):
        if j>i:
            j=int(j)
            tempr=data[j-1]
            tempi=data[j]
            data[j-1]=data[i-1]
            data[j]=data[i]
            data[i-1]=tempr
            data[i]=tempi

        m=nn

        while m>=2 and j+1>m:
            j=j-m
            m=m/2
        j=j+m

    mmax=2

    while n>mmax:
        istep=2*mmax
        wr=1
        wi=0

        for m in range(0,mmax,2):
            for i in range(m,n,istep):
                j=i+mmax
                tempr=wr*data[j]-wi*data[j+1]
                tempi=wr*data[j+1]+wi*data[j]
                data[j]=data[i]-tempr
                data[j+1]=data[i+1]-tempi
                data[i]=data[i]+tempr
                data[i+1]=data[i+1]+tempi
            wtemp=wr
            wr=wr*np.cos(2*np.pi/mmax)-wi*np.sin(2*np.pi/mmax)
            wi=wi*np.cos(2*np.pi/mmax)+wtemp*np.sin(2*np.pi/mmax)
        mmax=istep
    return data





########################################################################################################
############### read in netCDF files with raw data  ###########
########################################################################################################
print('read in netCDF files with raw data')
all_files=sorted(glob.glob('output_data/'+'/2011*calibrated_rawdata*nc'))

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


########################################################################################################
############### Fast Fourier transformation  ###########
########################################################################################################
print('##### Fourier transformation #####')
print('----------------------------------')
lfft=int(input('insert length of FFT (integer, n**2): '))
starttime=input('insert your start time in format YYYY-MM-DDTHH:MM (T is a capital letter): ')
endtime=input('insert your end time in the same format: ')
Datum=starttime[0:10]

FFT_data=rawdata_complete.sel(date=slice(starttime,endtime))

print('--------------------------------------------------------')
print('select two data arrays, for which the FFT should be done')
print('--------------------------------------------------------')
input_x=input('first data array, e.g. x=FFT_data.anem1: ')
input_y=input('second data array, e.g. y=FFT_data.anem2: ')
exec(input_x)
exec(input_y)


#### Definition of window function (Hanning Fenster)
"""
Zur Verbesserung der Ergebnisse der FFT wird jeder Teilabschnitt
mit einem Fenster gewichtet (Ränder weniger gewichtet als Mitte).
Hier wird ein Hanning Fenster verwendet. Die Breite ist lfft.
"""
Han=np.zeros(lfft)
for i in range(lfft):
    Han[i]=np.sqrt(2/3)*(1-np.cos(2*np.pi*i/lfft))


"""
- Es werden zwei Datenreihen x und y für die FFT verwendet
- Die FFT wird für verschiedene Teilabschnitte von x und y durchgeführt, die jeweils die Länge LFFT haben.
- Dazu wird das Fenster schrittweise um LFFT/8 Stellen verschoben.
- Die Länge von x bwz. y sollte > 10 * LFFT sein.
- Pro Fenster wird erst der Mittelwert über den Fensterabschnitt gebildet.
- Dieser wird von den einzelnen Datenwerten abgezogen, dann Multiplikation mit Hanning Fenster. Wird auf den geraden Stellen eines neuen arrays (xx, yy) gespeichert. (reelle Datenwerte)
- Alle ungeraden stellen werden 0 gesetzt. (komplexe Datenwerte, hier 0)
"""

print('length of data array: ', len(x), 'divided by length of window:', lfft, 'should be > 10: ',len(x)/lfft)
nr_counts=int((len(x)-lfft)/(lfft/8)+1)

xx=np.zeros(2*lfft)
yy=np.zeros(2*lfft)

lx=np.zeros(int(lfft/2))
ly=np.zeros(int(lfft/2))
co=np.zeros(int(lfft/2))
qu=np.zeros(int(lfft/2))


#### outer loop over each window
count=0
for k in range(0,len(x)-lfft,int(lfft/8)):
    count=count+1
    print(count,' of ',nr_counts)
    xmean=np.nanmean(x[k:k+lfft])
    ymean=np.nanmean(y[k:k+lfft])
    ii=0
    for i in range(0,lfft):
        xx[ii]=(x[k+i]-xmean)*Han[i]
        yy[ii]=(y[k+i]-xmean)*Han[i]
        ii=ii+1
        xx[ii]=0
        yy[ii]=0
        ii=ii+1

    
    """
    calculation fourier coefficients with four1
    """
    xx=four1(xx,lfft,1)
    yy=four1(yy,lfft,1)

    xx=xx/lfft
    yy=yy/lfft

    ### standard deviation of fourier coefficients
    sx=np.sqrt(np.sum(xx[2:2*lfft]**2))
    sy=np.sqrt(np.sum(yy[2:2*lfft]**2))

    """
    calculate Leistungsspektrum & Kreuzspektrum (co=real part, qu=imaginary part)
    """
    kk=0
    for i in range(2,lfft+2,2):
        lx[kk]=lx[kk]+(xx[i]**2+xx[i+1]**2)
        ly[kk]=ly[kk]+(yy[i]**2+yy[i+1]**2)
        co[kk]=co[kk]+(xx[i]*yy[i]+xx[i+1]*yy[i+1])
        qu[kk]=qu[kk]+(xx[i+1]*yy[i]-xx[i]*yy[i+1])
        kk=kk+1

"""
average over all window sections
"""
lx=lx/count
ly=ly/count
co=co/count
qu=qu/count
std_lx=np.sqrt(2*np.sum(lx))
std_ly=np.sqrt(2*np.sum(ly))



#### theoretical e⁻5/3
theo=[]
fstep=[]
for i in range(1,int(lfft/2+1)):
    theo.append(i**(-5/3))
    fstep.append(i)

#### coherence and phase
phi=[]
coherence=[]
for i in range(int(lfft/2)):
    if co[i]!=0:
        phi.append(180*np.arctan(qu[i]/co[i])/np.pi)
    else:
        phi.append(0)
    coherence.append((co[i]**2+qu[i]**2)/(lx[i]*ly[i]))

#sys.exit()  
########################################################
# write to Dataset and save as netcdf

Datensatz=xr.Dataset(
    data_vars=dict(
        theo=(['fstep'],theo),
        lx=(['fstep'],lx),
        ly=(['fstep'],ly),
        co=(['fstep'],co),
        qu=(['fstep'],qu),
        phi=(['fstep'],phi),
        coherence=(['fstep'],coherence),
    ),
    coords=dict(
        fstep=fstep,
    ),
    attrs=dict(description='FFT Windmast')
)

Datensatz.to_netcdf('output_data/'+Datum+'_FFT_Windmast.nc',format='NETCDF4')
