#!/usr/bin/env python

"""
saildrone_processing.py
 
parse saildrone data feed from oer individual ascii csv
    files for further display and processing.

 Using Anaconda packaged Python 
"""

#System Stack
import datetime
import argparse
import sys

#Science Stack
import numpy as np



__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 06, 07)
__modified__ = datetime.datetime(2014, 06, 07)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'saildrone','csv','timeseries', 'dygraphs'

""" ---------------------------------- Data Read --------------------------------------"""

def ATRH_READ(filein, subsample=True):
    data_parsed = {}
    
    with open(filein) as f:
        for k, line in enumerate(f.readlines()):
            line = line.strip()
            if k==0: #build dictionary of header info
                headers = line.split(',')
                continue
                
            if subsample:
                if (line.split(',')[2]):  #Get ATRH lines
                    temp_line = line.split(',')
                    data_parsed[k] = [temp_line[headers.index('ISO Time')],\
                                      temp_line[headers.index('time')],\
                                      temp_line[headers.index('atrh_at_filtered (degrees_c)')],\
                                      temp_line[headers.index('atrh_rh_filtered (percent)')],\
                                      temp_line[headers.index('baro_pressure_filtered (hPa)')],\
                                      temp_line[headers.index('wind_direction_filtered (degrees)')],\
                                      temp_line[headers.index('wind_gust_filtered (knots)')],\
                                      temp_line[headers.index('wind_speed_filtered (knots)')],\
                                      temp_line[headers.index('par_air_filtered (mmqpspm2)')]]
            else:
                temp_line = line.split(',')
                data_parsed[k] = [temp_line[headers.index('ISO Time')],\
                                  temp_line[headers.index('time')],\
                                  temp_line[headers.index('atrh_at_filtered (degrees_c)')],\
                                  temp_line[headers.index('atrh_rh_filtered (percent)')],\
                                  temp_line[headers.index('baro_pressure_filtered (hPa)')],\
                                  temp_line[headers.index('wind_direction_filtered (degrees)')],\
                                  temp_line[headers.index('wind_gust_filtered (knots)')],\
                                  temp_line[headers.index('wind_speed_filtered (knots)')],\
                                  temp_line[headers.index('par_air_filtered (mmqpspm2)')]]
                
    return data_parsed

def CTD_READ(filein, subsample=True):
    data_parsed = {}
    
    with open(filein) as f:
        for k, line in enumerate(f.readlines()):
            line = line.strip()
            if k==0: #build dictionary of header info
                headers = line.split(',')
                continue
                
            if subsample:
                if (line.split(',')[2]):  #Get ATRH lines only
                    temp_line = line.split(',')
                    data_parsed[k] = [temp_line[headers.index('ISO Time')],\
                                      temp_line[headers.index('time')],\
                                      temp_line[headers.index('ctd_salinity_filtered (salinity)')],\
                                      temp_line[headers.index('ctd_temperature_filtered (degrees_c)')],\
                                      temp_line[headers.index('do2_concentration_filtered (micromolar)')],\
                                      temp_line[headers.index('fluoro_CDOM_ppb_filtered (ppb)')],\
                                      temp_line[headers.index('fluoro_chlorophyll_ug_per_l_filtered (ugpl)')],\
                                      temp_line[headers.index('ir_thermo_temperature_filtered (degrees_c)')],\
                                      temp_line[headers.index('tide_direction_filtered (degrees)')],\
                                      temp_line[headers.index('tide_speed_filtered (knots)')]]
            else:
                temp_line = line.split(',')
                data_parsed[k] = [temp_line[headers.index('ISO Time')],\
                                  temp_line[headers.index('time')],\
                                  temp_line[headers.index('ctd_salinity_filtered (salinity)')],\
                                  temp_line[headers.index('ctd_temperature_filtered (degrees_c)')],\
                                  temp_line[headers.index('do2_concentration_filtered (micromolar)')],\
                                  temp_line[headers.index('do2_temperature_filtered (degrees_c)')],\
                                  temp_line[headers.index('fluoro_CDOM_ppb_filtered (ppb)')],\
                                  temp_line[headers.index('fluoro_chlorophyll_ug_per_l_filtered (ugpl)')],\
                                  temp_line[headers.index('ir_thermo_temperature_filtered (degrees_c)')],\
                                  temp_line[headers.index('tide_direction_filtered (degrees)')],\
                                  temp_line[headers.index('tide_speed_filtered (knots)')],\
                                  temp_line[headers.index('fluoro_signal_strength_460_nm_filtered (counts)')],\
                                  temp_line[headers.index('fluoro_signal_strength_650_nm_filtered (counts)')],\
                                  temp_line[headers.index('fluoro_signal_strength_695_nm_filtered (counts)')]]

    return data_parsed

def GPS_READ(filein, subsample=True):
    data_parsed = {}
    
    with open(filein) as f:
        for k, line in enumerate(f.readlines()):
            line = line.strip()
            if k==0: #build dictionary of header info
                headers = line.split(',')
                continue
                
            if subsample:
                if (line.split(',')[2]):  #Get ATRH lines only
                    temp_line = line.split(',')
                    data_parsed[k] = [temp_line[headers.index('ISO Time')],\
                                      temp_line[headers.index('time')],\
                                      temp_line[headers.index('gps_lat (gps_coord)')],\
                                      temp_line[headers.index('gps_lng (gps_coord)')],\
                                      temp_line[headers.index('gps_time (None)')]]
            else:
                temp_line = line.split(',')
                data_parsed[k] = [temp_line[headers.index('ISO Time')],\
                                  temp_line[headers.index('time')],\
                                  temp_line[headers.index('gps_lat (gps_coord)')],\
                                  temp_line[headers.index('gps_lng (gps_coord)')],\
                                  temp_line[headers.index('gps_time (None)')]]
                
    return data_parsed
"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(description='OER SailDrone processing')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('--cal_coeffs', nargs='+', type=float, help='a b c')
parser.add_argument('--var_list', action='store_true', help='list out all parameters available')
parser.add_argument('--ATRH', action='store_true', help='generate ATRH output only (to standard out)')
parser.add_argument('--CTD', action='store_true', help='generate CTD output only (to standard out)')
parser.add_argument('--GPS', action='store_true', help='generate geoJSON output (to standard out)')
parser.add_argument('--subsample', action='store_true', help='use only hourly data from when ATRH reports')

args = parser.parse_args()

if args.var_list:
    header_vars = ['ISO Time',
                    'time',
                    'atrh_at_filtered',
                    'atrh_at_rms',
                    'atrh_num_samples',
                    'atrh_rh_filtered',
                    'atrh_rh_rms',
                    'baro_num_samples',
                    'baro_pressure_filtered',
                    'baro_pressure_rms',
                    'ctd_conductivity_filtered',
                    'ctd_conductivity_rms',
                    'ctd_num_samples',
                    'ctd_salinity_filtered',
                    'ctd_salinity_rms',
                    'ctd_temperature_filtered',
                    'ctd_temperature_rms',
                    'do2_air_saturation_filtered',
                    'do2_air_saturation_rms',
                    'do2_concentration_filtered',
                    'do2_concentration_rms',
                    'do2_num_samples',
                    'do2_temperature_filtered',
                    'do2_temperature_rms',
                    'fluoro_CDOM_ppb_filtered',
                    'fluoro_CDOM_ppb_rms',
                    'fluoro_chlorophyll_ug_per_l_filtered',
                    'fluoro_chlorophyll_ug_per_l_rms',
                    'fluoro_num_samples',
                    'fluoro_scattering_s_per_mr_filtered',
                    'fluoro_scattering_s_per_mr_rms',
                    'fluoro_signal_strength_460_nm_filtered',
                    'fluoro_signal_strength_460_nm_rms',
                    'fluoro_signal_strength_650_nm_filtered',
                    'fluoro_signal_strength_650_nm_rms',
                    'fluoro_signal_strength_695_nm_filtered',
                    'fluoro_signal_strength_695_nm_rms',
                    'gps_lat',
                    'gps_lng',
                    'gps_time',
                    'ir_thermo_num_samples',
                    'ir_thermo_temperature_filtered',
                    'ir_thermo_temperature_rms',
                    'mag_num_samples',
                    'mag_strength_filtered',
                    'mag_strength_rms',
                    'par_air_filtered',
                    'par_air_num_samples',
                    'par_air_rms',
                    'speed_num_samples',
                    'tide_direction_filtered',
                    'tide_direction_rms',
                    'tide_speed_filtered',
                    'tide_speed_rms',
                    'wind_direction_filtered',
                    'wind_direction_rms',
                    'wind_gust_filtered',
                    'wind_gust_rms',
                    'wind_num_samples',
                    'wind_speed_filtered',
                    'wind_speed_rms']
    print "The following are valid vars to keep"
    for a,i in enumerate(header_vars):
        print i
    
    sys.exit()
    
if args.ATRH:
    data_parsed = ATRH_READ(args.DataPath, args.subsample)

    print "Time, Temp, RH, Press, Wind Dir, Wind Gust, Wind Spd, PAR\n"
    for k,v in sorted(data_parsed.items()):
        print "{0} {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format(v[0].split('T')[0], v[0].split('UT')[0].split('T')[-1], v[2], v[3], v[4], v[5], v[6], v[7], v[8])


if args.CTD:
    data_parsed = CTD_READ(args.DataPath, args.subsample)

    print "Time, Salinity, Temp, DO2, DO2 Temp, CDOM, Chlorophyll, IR Temp, Tide Dir, Tide Speed, Fl 460nm, Fl 495nm, Fl650nm\n"
    for k,v in sorted(data_parsed.items()):
        print "{0} {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}".format(
            v[0].split('T')[0], v[0].split('UT')[0].split('T')[-1], 
            v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10],
            v[11], v[12], v[13])

if args.GPS:

    data_parsed = GPS_READ(args.DataPath, args.subsample)

    ### "Generating .geojson"
    geojson_header = (
        '{\n'
        '"type": "FeatureCollection",\n'
        '"features": [\n'
        '{\n'
        '"type": "Feature",\n'
        '"geometry": {\n'
        '"type": "MultiPoint",\n'
        '"coordinates": [ '
        )
    geojson_point_coords = ''

    for k,value in sorted(data_parsed.items()):
        isempty = False
        if value[2] == '':
            #skip if empty lons
            value[2] = 0.0
            value[3] = 0.0
        
        geojson_point_coords = geojson_point_coords + ('[{1},{0}]').format(value[2],value[3])
            
        if (k is not sorted(data_parsed.keys())[-1]):
            geojson_point_coords = geojson_point_coords + ', '
    geojson_tail = (
        ']\n'
        '},\n'
        '"properties": {\n'
        '"prop0": "value0"\n'
        '}\n'
        '}\n'
        ']\n'
        '}\n'
        )
        
    print geojson_header + geojson_point_coords + geojson_tail 