#!/usr/bin/env python

"""
oerctd_processing.py
 
generate netcdf files (EPIC flavored) from CTD's used by OER (mostly on wavegliders)

5 samples spread over 30 seconds - take mean and create statitistics
Data is along track so lat/lon are also variable

"""

#System Stack
import datetime
import argparse
import pymysql

#Science Stack
from netCDF4 import Dataset 
import numpy as np
import seawater as sw

#User Stack
import utilities.ConfigParserLocal as ConfigParserLocal
import oerctd2nc 

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 06, 07)
__modified__ = datetime.datetime(2014, 06, 07)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'along track','csv','timeseries','wavegliders'


"""------------------------------- lat/lon ----------------------------------------"""

def latlon_convert(Mooring_Lat, Mooring_Lon):
    
    tlat = Mooring_Lat.strip().split() #deg min dir
    lat = float(tlat[0]) + float(tlat[1]) / 60.
    if tlat[2] == 'S':
        lat = -1 * lat
        
    tlon = Mooring_Lon.strip().split() #deg min dir
    lon = float(tlon[0]) + float(tlon[1]) / 60.
    if tlon[2] == 'E':
        lon = -1 * lon
        
    return (lat, lon)
"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(description='EcoFluor processing')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')

args = parser.parse_args()

#read in CTD data file
data_in = args.DataPath

data_out = data_in.split('/')[-1].split('.')[0] + '.unqcd.nc'

#### data readin
index = 0
new_data = True
time_threshold = (30.) / 86400. #maximum number of seconds between sequential measurements.  Most are 5 within 10 seconds

press_ave,temp_ave,cond_ave,time1_ave,time2_ave = {},{},{},{},{}


with open(data_in) as f:

    for k, line in enumerate(f.readlines()):
        try:
            line_array = line.strip().split()
        except:
            continue
            
        #once data is read from file, it needs to be averaged.  
        #There are 5 associated measurements every hour                    
        if (new_data == True): #intial data 

            if len( line_array ) == 5: #fls: date, time, wavelength, counts, thermistor
                date = line_array[0]+ ' '
                time = line_array[1]
                dtime = oerctd2nc.DataTimes(date+time, ismmddyy=True).get_EPIC_date()
                
                time1 = dtime[0]
                time2 = dtime[1]

                press = np.float(line_array[2])
                temp = np.float(line_array[3])
                cond = np.float(line_array[4])
                prev_time = dtime[0]+(dtime[1] / (86400. *1000.))
                new_data = False

                
        elif (new_data == False):

            if len( line_array ) == 5: #fls: date, time, wavelength, counts, thermistor
                
                date = line_array[0]+ ' '
                time = line_array[1]
                dtime = oerctd2nc.DataTimes(date+time, ismmddyy=True).get_EPIC_date()
                sample_time = dtime[0]+(dtime[1] / (86400. *1000.))
                if (sample_time - prev_time) > time_threshold: #average and start again
                    press_ave[index] = press.mean()
                    temp_ave[index] = temp.mean()
                    cond_ave[index] = cond.mean()
                    if time2.max() - time2.min() > 50000:
                        #time overlaps a day change
                        #force it to be at midnight
                        print "{0} is a time step that overlaps a day change".format(k)
                        print "Forcing this record to be stamped at 00:00"
                        time2_ave[index] = 0
                        time1_ave[index] = time1.max()
                    else:
                        time2_ave[index] = time2.mean()
                        time1_ave[index] = time1.mean()
                    index += 1
                    new_data = True
                time1 = np.vstack((time1,dtime[0]))
                time2 = np.vstack((time2,dtime[1] ))

                press = np.vstack((press,np.float(line_array[2])))
                temp = np.vstack((temp,np.float(line_array[3])))
                cond = np.vstack((cond,np.float(line_array[4])))

#cycle through and build data arrays
press = np.array(press_ave.values(), dtype='f8')
temp = np.array(temp_ave.values(), dtype='f8')
cond = np.array(cond_ave.values(), dtype='f8')
time1 = np.array(time1_ave.values(), dtype='f8')
time2 = np.array(time2_ave.values(), dtype='f8')

sal = np.ones_like(time1) * -9999

ncinstance = oerctd2nc.OERCTD_NC(savefile=data_out)
ncinstance.file_create()
ncinstance.sbeglobal_atts(raw_data_file=data_in.split('/')[-1], Station_Name = 'WaveGlider', Water_Depth='Tractor')
ncinstance.dimension_init(time_len=len(time1))
ncinstance.variable_init()
ncinstance.add_coord_data(depth=6, latitude=-9999, longitude=-9999, time1=time1, time2=time2)
ncinstance.add_data(data=[temp,press,cond,sal,])
ncinstance.close()