#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_dbload.py
 
 
 Purpose:
 --------
 load glider netcdf data into mysql database

 History:
 --------


"""
import argparse, os

from io_utils import ConfigParserLocal
import numpy as np

import calc.aanderaa_corrO2_sal as optode_O2_corr
from plots.profile_plot import CTDProfilePlot
import io_utils.EcoFOCI_netCDF_read as eFOCI_ncread
from io_utils.EcoFOCI_db_io import EcoFOCI_db_oculus

# Visual Stack
import matplotlib as mpl
import matplotlib.pyplot as plt


def castdirection(depth):
    """determin index of upcast and downcast"""
    downcast = [0,np.argmax(np.diff(depth)<0)+1]
    upcast = [np.argmax(np.diff(depth)<0)+1,len(depth)]

    return (downcast,upcast)

"""-------------------------------- Main -----------------------------------------------"""

parser = argparse.ArgumentParser(description='Load Glider NetCDF data into MySQL database')
parser.add_argument('sourcefile', metavar='sourcefile', type=str,
               help='complete path to netcdf file')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing


filein = args.sourcefile
diveNum = filein.split('/')[-1].split('.nc')[0].split('p4010')[-1]

df = eFOCI_ncread.EcoFOCI_netCDF(file_name=filein)
vars_dic = df.get_vars()
ncdata = df.ncreadfile_dic()
data_time = df.epochtime2date()
df.close()


pressure = ncdata['ctd_pressure']
SBE_Temperature = ncdata['temperature']
SBE_Salinity = ncdata['salinity']

Wetlabs_CDOM = ncdata['wlbb2fl_sig470nm_adjusted']
Wetlabs_CHL  = ncdata['wlbb2fl_sig695nm_adjusted']
Wetlabs_NTU  = ncdata['wlbb2fl_sig700nm_adjusted']

Aand_Temp = ncdata['eng_aa4330_Temp']
Aand_O2_corr = ncdata['aanderaa4330_dissolved_oxygen']
Aand_DO_Sat  = ncdata['eng_aa4330_AirSat']
Aand_DO_Sat_calc = optode_O2_corr.O2PercentSat(oxygen_conc=Aand_O2_corr, 
                                     salinity=SBE_Salinity,
                                     temperature=SBE_Temperature,
                                     pressure=pressure)  

PAR_satu = ncdata['eng_satu_PARuV'] 
PAR_satd = ncdata['eng_satd_PARuV'] 

lat = ncdata['latitude']
lon = ncdata['longitude']

downInd,upInd = castdirection(pressure)
castdir = np.chararray((np.shape(pressure)[0]+1))
castdir[downInd[0]:downInd[1]] = 'd'
castdir[upInd[0]:upInd[1]] = 'u'


###
#
# load database
config_file = 'EcoFOCI_config/db_config/db_config_oculus_root.pyini'
EcoFOCI_db = EcoFOCI_db_oculus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

for i,inst_time in enumerate(data_time):
  if np.isnan(SBE_Salinity[i]):
    EcoFOCI_db.add_to_DB(table='2017_Fall_SG401',divenum=diveNum,time=data_time[i],
    latitude=lat[i],longitude=lon[i],depth=pressure[i],castdirection=castdir[i],
    temperature=SBE_Temperature[i],
    do_sat=Aand_DO_Sat[i],
    sig470nm=Wetlabs_CDOM[i],sig695nm=Wetlabs_CHL[i],sig700nm=Wetlabs_NTU[i],
    up_par=PAR_satu[i],down_par=PAR_satd[i])
  else:
    EcoFOCI_db.add_to_DB(table='2017_Fall_SG401',divenum=diveNum,time=data_time[i],
    latitude=lat[i],longitude=lon[i],depth=pressure[i],castdirection=castdir[i],
    salinity=SBE_Salinity[i],temperature=SBE_Temperature[i],
    do_sat=Aand_DO_Sat[i],do_conc=Aand_O2_corr[i],
    sig470nm=Wetlabs_CDOM[i],sig695nm=Wetlabs_CHL[i],sig700nm=Wetlabs_NTU[i],
    up_par=PAR_satu[i],down_par=PAR_satd[i])

EcoFOCI_db.close()