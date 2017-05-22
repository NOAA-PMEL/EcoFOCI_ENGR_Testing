#!/usr/bin/env python

"""
oer_rudix_processing.py
 

"""

#System Stack
import datetime
import argparse


#Science Stack
import numpy as np

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
parser.add_argument('DataPath', metavar='DataPath', type=str, help='full path to file')
parser.add_argument('channel', metavar='channel', type=str, help='fluor,turb,press')

args = parser.parse_args()

#read in CTD data file
data_in = args.DataPath

#### data readin
index = 0
new_data = True

timestamp, fluor, turb = {},{},{}
wetlabs = False
CTD = False

with open(data_in) as f:

    for k, line in enumerate(f.readlines()):
        try:
            line_array = line.strip().split()
        except:
            continue
        
        if not line_array:
            wetlabs = False
            continue
        
        if line_array[0] == 'CTD': #start of wetlabs record
            CTD = True
            time_start = datetime.datetime.strptime(line_array[1]+' '+line_array[2],'%m/%d/%Y %H:%M:%S')
            #print time_start
            continue
        elif line_array[0] == 'AADI': #end CTD record
            CTD = False

            
        if (line_array) and (CTD == True):
            if args.channel == 'press':
                for i in line_array[0::3]: #every other even
                    print "{0},{1}".format(time_start.strftime('%m/%d/%Y %H:%M:%S'), int(i)/100.)
            continue

        if line_array[0] == 'WETL': #start of wetlabs record
            wetlabs = True
            time_start = datetime.datetime.strptime(line_array[1]+' '+line_array[2],'%m/%d/%Y %H:%M:%S')
            #print time_start
            continue
        
        if (line_array) and (wetlabs == True):
            if args.channel == 'fluor':
                for i in line_array[0::2]: #every other even
                    time_start = time_start + datetime.timedelta(8./(24.*60.*60.))
                    print "{0},{1}".format(time_start.strftime('%m/%d/%Y %H:%M:%S'), (int(i) - 61.) * 0.0251)
            if args.channel == 'turb':
                for i in line_array[1::2]: #every other even
                    time_start = time_start + datetime.timedelta(8./(24.*60.*60.))
                    print "{0},{1}".format(time_start.strftime('%m/%d/%Y %H:%M:%S'), (int(i) - 51.) * 0.2109)
            continue




