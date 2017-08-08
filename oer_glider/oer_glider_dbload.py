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
    downcast = [0,np.argmax(depth)+1]
    upcast = [np.argmax(depth)+1,len(depth)]

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

SBE_Conductivity_raw = ncdata['conductivity_raw']

SBE_Salinity_raw = ncdata['salinity_raw']
SBE_Salinity_raw_qc = ncdata['salinity_raw_qc']

density_insitu = ncdata['density_insitu']

Wetlabs_CDOM = ncdata['wlbb2fl_sig470nm_adjusted']
if Wetlabs_CDOM is np.ma.masked:
  Wetlabs_CDOM = Wetlabs_CDOM.data
Wetlabs_CHL  = ncdata['wlbb2fl_sig695nm_adjusted']
if Wetlabs_CHL is np.ma.masked:
  Wetlabs_CHL = Wetlabs_CHL.data
Wetlabs_NTU  = ncdata['wlbb2fl_sig700nm_adjusted']
if Wetlabs_NTU is np.ma.masked:
  Wetlabs_NTU = Wetlabs_NTU.data

Aand_Temp = ncdata['eng_aa4330_Temp']
Aand_O2_corr = ncdata['aanderaa4330_dissolved_oxygen'].data
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

SBE_Salinity = np.where(np.isnan(SBE_Salinity), None, SBE_Salinity)
SBE_Conductivity_raw = np.where(np.isnan(SBE_Conductivity_raw), None, SBE_Conductivity_raw)
PAR_satu = np.where(np.isnan(PAR_satu), None, PAR_satu)
Aand_O2_corr = np.where(np.isnan(Aand_O2_corr), None, Aand_O2_corr)
Aand_DO_Sat = np.where(Aand_DO_Sat<0, None, Aand_DO_Sat)
Aand_DO_Sat = np.where(Aand_DO_Sat>200, None, Aand_DO_Sat)
Wetlabs_CDOM = np.where(np.isnan(Wetlabs_CDOM), None, Wetlabs_CDOM)
Wetlabs_CHL = np.where(np.isnan(Wetlabs_CHL), None, Wetlabs_CHL)
Wetlabs_NTU = np.where(np.isnan(Wetlabs_NTU), None, Wetlabs_NTU)
density_insitu = np.where(np.isnan(density_insitu), None, density_insitu)

###
#
# load database
config_file = 'EcoFOCI_config/db_config/db_config_oculus_root.pyini'
EcoFOCI_db = EcoFOCI_db_oculus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

for i,inst_time in enumerate(data_time):
    EcoFOCI_db.add_to_DB(table='2017_Fall_SG401',divenum=diveNum,time=data_time[i],
    latitude=lat[i],longitude=lon[i],depth=pressure[i],castdirection=castdir[i], conductivity_raw=SBE_Conductivity_raw[i],
    salinity=SBE_Salinity[i],salinity_raw=SBE_Salinity_raw[i],temperature=SBE_Temperature[i],
    do_sat=Aand_DO_Sat[i],do_conc=Aand_O2_corr[i],
    sig470nm=Wetlabs_CDOM[i],sig695nm=Wetlabs_CHL[i],sig700nm=Wetlabs_NTU[i],
    up_par=PAR_satu[i],down_par=PAR_satd[i],density_insitu=density_insitu[i])

EcoFOCI_db.close()