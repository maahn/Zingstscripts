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

filename='output_data/20120605_mean_values_Coras.nc'
rawdata_mean=xr.open_dataset(filename)

"""
to select a value (e.g. the 10th mean of pixel nr 500):
rawdata_mean.sel(pixnr=500,date=rawdata_mean.date[9])
please pay attention: in the terminal output it will be rounded, otherwise use:
rawdata_mean.sel(pixnr=500,date=rawdata_mean.date[9]).counts.values
"""
