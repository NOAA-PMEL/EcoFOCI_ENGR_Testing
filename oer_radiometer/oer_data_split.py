#!/usr/bin/env python

"""
oer_data_split.py
 
using files from oer_processing, and from RadTiltCorr, split files into daily and monthly files for 
    easier analysis.

"""

#System Stack
import datetime
import argparse
import csv

#Science Stack
import numpy as np
import ephem


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 06, 07)
__modified__ = datetime.datetime(2016, 03, 07)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'mooring','csv','timeseries', 'dygraphs'


""" ---------------------------------- Data Read --------------------------------------"""

def CSV2Dic(filein):
    reader = csv.DictReader(open(filein,'rU'))

    result = {}
    for row in reader:
        for column, value in row.iteritems():
            result.setdefault(column, []).append(value)

    return result        

"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(description='OER Radiometric subsetting')
parser.add_argument('DataPath', metavar='DataPath', type=str, help='full path to file')
parser.add_argument('TimeBase', metavar='TimeBase', type=str, help='choose "daily", "weekly" or "monthly"')

args = parser.parse_args()
root_path = "/".join(args.DataPath.split('/')[:-1])
file_name = args.DataPath.split('/')[-1].split('.')[0]

in_dat = CSV2Dic(args.DataPath)
temp_date = [datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in in_dat['Date']]

if args.TimeBase == "daily":
    pass
elif args.TimeBase == "weekly":
    for weeknum in range(1,53,1):
        with open(root_path + '/' + file_name + 'w' + str(weeknum) + '.csv', 'w' ) as outfile:
            print "Creating file for {0}".format(file_name + 'w' + str(weeknum) )
            for ind, v in enumerate(temp_date):
                if (v.isocalendar()[1] == weeknum):
                    #Date, GtDt, Heading, Pitch, Role, instzen, sunzen, sunaz, corr_sza, k_ratio, G_corr_factor, SPN Total
                    line = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}\n".format(in_dat['Date'][ind],in_dat[' GtDt'][ind],in_dat[' Heading'][ind],in_dat[' Pitch'][ind],in_dat[' Role'][ind],\
                    in_dat[' instzen'][ind], in_dat[' instaz'][ind],in_dat[' sunzen'][ind],in_dat[' sunaz'][ind],in_dat[' corr_sza'][ind],in_dat[' k_ratio'][ind],in_dat[' G_corr_factor'][ind],in_dat[' SPN Total'][ind])
                    outfile.write(line)
elif args.TimeBase == "monthly":
    for month in range(1,13,1):
        with open(root_path + '/' + file_name + datetime.datetime.strptime(str(month),'%m').strftime('%m')+'m', 'w' ) as outfile:
            print "Creating file for {0}".format(file_name + datetime.datetime.strptime(str(month),'%m').strftime('%m'))
            for ind, v in enumerate(temp_date):
                if (v.month == month):
                    #Date, GtDt, Heading, Pitch, Role, instzen, sunzen, sunaz, corr_sza, k_ratio, G_corr_factor, SPN Total
                    line = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}\n".format(in_dat['Date'][ind],in_dat[' GtDt'][ind],in_dat[' Heading'][ind],in_dat[' Pitch'][ind],in_dat[' Role'][ind],\
                    in_dat[' instzen'][ind], in_dat[' instaz'][ind],in_dat[' sunzen'][ind],in_dat[' sunaz'][ind],in_dat[' corr_sza'][ind],in_dat[' k_ratio'][ind],in_dat[' G_corr_factor'][ind],in_dat[' SPN Total'][ind])
                    outfile.write(line)
else:
    print "Choose either daily or monthly for the TimeBase flag"
