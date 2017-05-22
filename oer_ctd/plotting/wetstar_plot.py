#!/usr/bin/env

"""
wetstar_plot.py


"""
#System Stack
import datetime, sys
import argparse

#Science Stack
from netCDF4 import Dataset
import numpy as np

# Visual Stack
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, DateFormatter

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 9, 11)
__modified__ = datetime.datetime(2014, 9, 11)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'SeaWater', 'Cruise', 'derivations'

"""--------------------------------netcdf Routines---------------------------------------"""

def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables

def get_var_atts(nchandle, var_name):
    return nchandle.variables[var_name]

def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params): 
        if v in nchandle.variables.keys(): #check for nc variable
                data[v] = nchandle.variables[v][:]

        else: #if parameter doesn't exist fill the array with zeros
            data[v] = None
    return (data)

def repl_var(nchandle, var_name, val=1e35):
    if len(val) == 1:
        nchandle.variables[var_name][:] = np.ones_like(nchandle.variables[var_name][:]) * val
    else:
        nchandle.variables[var_name][:] = val
    return

"""--------------------------------time Routines---------------------------------------"""

def date2pydate(file_time, file_time2=None, file_flag='EPIC'):


    if file_flag == 'EPIC':
        ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
        ref_time_epic = 2440000
    
        offset = ref_time_epic - ref_time_py
    
       
        try: #if input is an array
            python_time = [None] * len(file_time)

            for i, val in enumerate(file_time):
                pyday = file_time[i] - offset 
                pyfrac = file_time2[i] / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
                python_time[i] = (pyday + pyfrac)

        except:
    
            pyday = file_time - offset 
            pyfrac = file_time2 / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
            python_time = (pyday + pyfrac)
        
    else:
        print "time flag not recognized"
        sys.exit()
        
    return np.array(python_time)
"""--------------------------------main Routines---------------------------------------"""

parser = argparse.ArgumentParser(description='WetStar plotting')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument("-fp",'--full_path', action="store_true", help='provides full path to program: used if run as script')
parser.add_argument("-turb",'--turbidity', action="store_true", help='flag to plot turbidity')
          
args = parser.parse_args()

#read in wetstar data file
ncfile1 = args.DataPath

nchandle = Dataset(ncfile1,'a')
global_atts = get_global_atts(nchandle)
vars_dic = get_vars(nchandle)
data1 = ncreadfile_dic(nchandle,vars_dic.keys())
nchandle.close()
time1 = date2pydate(data1['time'],data1['time2'])

### Single Depth Value (from mooring logs and records)
#### Plot T, S, C on one page
ptitle = ("Plotted on: {0} \n from {1} "
          "Lat: {2:3.3f}  Lon: {3:3.3f} Depth: {4}\n : ecofluor").format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), 
                                          global_atts['MOORING'], data1['lat'][0], data1['lon'][0], data1['depth'][0] )

if args.turbidity:
    fig = plt.figure(2)
    ax1 = plt.subplot2grid((3, 1), (0, 0), colspan=1, rowspan=1)
    p1 = ax1.plot(time1, data1['fluor_3031'][:,0,0,0],'k.', markersize=2)
    ax1.set_ylim([data1['fluor_3031'][data1['fluor_3031'] != 1e35].min(),data1['fluor_3031'][data1['fluor_3031'] != 1e35].max()])
    ax1.set_xlim([time1.min(),time1.max()])
    plt.ylabel('fluor_3031')
    ax1.xaxis.set_major_locator(MonthLocator(interval=2))
    ax1.xaxis.set_minor_locator(MonthLocator())
    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax1.tick_params(axis='x',which='both',bottom='off',labelbottom='off')
    ax1.spines['bottom'].set_visible(False)

    ax2 = plt.subplot2grid((3, 1), (1, 0), colspan=1, rowspan=1)
    p2 = ax2.plot(time1, data1['Fch_906'][:,0,0,0],'k.', markersize=2)
    ax2.set_ylim([data1['Fch_906'][data1['Fch_906'] != 1e35].min()-0.5,data1['Fch_906'][data1['Fch_906'] != 1e35].max()+0.5])
    ax2.set_xlim([time1.min(),time1.max()])
    plt.ylabel('Fch_906')
    ax2.xaxis.set_major_locator(MonthLocator(interval=2))
    ax2.xaxis.set_minor_locator(MonthLocator())
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax2.tick_params(axis='x',which='both', top='off')
    ax2.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)

    ax3 = plt.subplot2grid((3, 1), (2, 0), colspan=1, rowspan=1)
    p2 = ax3.plot(time1, data1['Trb_980'][:,0,0,0],'k.', markersize=2)
    ax3.set_ylim([data1['Trb_980'][data1['Trb_980'] != 1e35].min()-0.5,data1['Trb_980'][data1['Trb_980'] != 1e35].max()+0.5])
    ax3.set_xlim([time1.min(),time1.max()])
    plt.ylabel('Trb_980')
    ax3.xaxis.set_major_locator(MonthLocator(interval=2))
    ax3.xaxis.set_minor_locator(MonthLocator())
    ax3.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax3.tick_params(axis='x',which='both', top='off')
    ax3.spines['top'].set_visible(False)
    
    t = fig.suptitle(ptitle)
    t.set_y(0.06)

    fig.autofmt_xdate()
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )
    if not args.full_path:
        plt.savefig('images/'+ ncfile1.split('/')[-1] + '_eco.png', bbox_inches='tight', dpi = (300))
    else:
        fullpath = '/Users/bell/Programs/Python/MooringDataProcessing/wetstar/plotting/'
        plt.savefig(fullpath + 'images/'+ ncfile1.split('/')[-1] + '_eco.png', bbox_inches='tight', dpi = (300))

    plt.close()
else:
    fig = plt.figure(2)
    ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
    p1 = ax1.plot(time1, data1['fluor_3031'][:,0,0,0],'k.', markersize=2)
    ax1.set_ylim([data1['fluor_3031'][data1['fluor_3031'] != 1e35].min(),data1['fluor_3031'][data1['fluor_3031'] != 1e35].max()])
    ax1.set_xlim([time1.min(),time1.max()])
    plt.ylabel('fluor_3031')
    ax1.xaxis.set_major_locator(MonthLocator(interval=2))
    ax1.xaxis.set_minor_locator(MonthLocator())
    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax1.tick_params(axis='x',which='both',bottom='off',labelbottom='off')
    ax1.spines['bottom'].set_visible(False)

    ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
    p2 = ax2.plot(time1, data1['Fch_906'][:,0,0,0],'k.', markersize=2)
    ax2.set_ylim([data1['Fch_906'][data1['Fch_906'] != 1e35].min()-0.5,data1['Fch_906'][data1['Fch_906'] != 1e35].max()+0.5])
    ax2.set_xlim([time1.min(),time1.max()])
    plt.ylabel('Fch_906')
    ax2.xaxis.set_major_locator(MonthLocator(interval=2))
    ax2.xaxis.set_minor_locator(MonthLocator())
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax2.tick_params(axis='x',which='both', top='off')
    ax2.spines['top'].set_visible(False)


    t = fig.suptitle(ptitle)
    t.set_y(0.06)

    fig.autofmt_xdate()
    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0]*2, DefaultSize[1]) )
    if not args.full_path:
        plt.savefig('images/'+ ncfile1.split('/')[-1] + '_eco.png', bbox_inches='tight', dpi = (300))
    else:
        fullpath = '/Users/bell/Programs/Python/MooringDataProcessing/wetstar/plotting/'
        plt.savefig(fullpath + 'images/'+ ncfile1.split('/')[-1] + '_eco.png', bbox_inches='tight', dpi = (300))

    plt.close()