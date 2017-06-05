#!/usr/bin/env python

"""
RadTiltCorr.py

Tilt Correction Routines from AAF_G1_TiltCorr.fort

Example Usage:
--------------

python RadTiltCorr.py data/2016_spn1_sample.dat --LatLon 56.868 -164.053 > outfile.dat

(Location above is M2 ITAE location during 2016)

### Input file expected format:

Time,Total,Diffuse,Sunshine,Heading,Pitch,Role
05/01/2016 18:04:55,152.0,116.3,0.0,273.6,80.3,12.3
05/01/2016 18:05:00,152.0,116.3,0.0,273.0,80.3,11.6
05/01/2016 18:05:05,152.2,118.0,0.0,272.5,80.3,10.7
...

### Output
Date, GtDt, Heading, Pitch, Role, instzen, instaz, sunzen, sunaz, corr_sza, k_ratio, G_corr_factor, SPN Total
...
GtDt = Global - Diffuse

Important data is "Date,G_corr_factor,SPN Total"
G_corr_factor - is the correction to be applied (multiplied) to the Total to get the tilt corrected total

"""

#System Stack
import datetime
import argparse
import csv

#Science Stack
import numpy as np
import ephem
import pandas as pd

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 06, 07)
__modified__ = datetime.datetime(2016, 03, 07)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'mooring','csv','timeseries'


""" ---------------------------------- Data Read --------------------------------------"""

def CSV2Dic(filein):
    reader = csv.DictReader(open(filein))

    result = {}
    for row in reader:
        for column, value in row.iteritems():
            result.setdefault(column, []).append(value)

    return result        

"""--------------------------------solar zenith---------------------------------------"""

def solar_zenith(timestr='2016-01-01 00:00:00', lat='47.6', lon='-122.32'):
    '''
    Time needs to be a string in UTC
    using subroutine ephem for solar positions
    '''
    location = ephem.Observer()
    location.lon, location.lat, location.date = lon,lat,timestr
    sun = ephem.Sun()
    sun.compute(location)
    sun_az = str(sun.az).split(':')
    sun_el = str(sun.alt).split(':')
    sun_az = float(sun_az[0]) + float(sun_az[1])/60. + float(sun_az[2])/3600.
    sun_el = float(sun_el[0]) + float(sun_el[1])/60. + float(sun_el[2])/3600.

    return (90. - sun_el, sun_az)
    
def rph2za(pitch,roll,heading):
    '''
    from Fortran/IDL subroutine by Paul Ricchiazzi, 25 Feb 97 paul@icess.ucsb.edu

    all angles in degrees
    pitch  : positive values indicate nose up
    roll   : positive values indicate right wing down
    azimuth: positive values clockwise, w.r.t. NORTH
    assume aircraft heading north: rotate around roll
    
    '''
    
    roll_rad = np.deg2rad(np.float(roll))
    pitch_rad = np.deg2rad(np.float(pitch))
    heading_rad = np.deg2rad(np.float(heading))

    uz = np.cos(roll_rad)*np.cos(pitch_rad)
    ux = np.sin(roll_rad)
    uy = -1.0 * np.cos(roll_rad) * np.sin(pitch_rad)
    
    vz = uz
    vx = ux * np.cos(heading_rad) + uy * np.sin(heading_rad)
    vy = uy * np.cos(heading_rad) - uy * np.sin(heading_rad)
    
    zenith = np.rad2deg(np.arccos(vz))
    if (vy == 0.0):
        vy = 0.00000001
    azimuth = np.rad2deg(np.arctan2(vx,vy))
    
    return (zenith, azimuth)
    
def muslope(sunzen,sunaz,nrmzen,nrmaz):
    '''
    C ROUTINE:  muslope
    C
    C PURPOSE:  compute dot product of surface normal to incomming solar ray
    C
    C USEAGE:   result=muslope(sunzen,sunaz,nrmzen,nrmaz)
    C
    C INPUT:    
    C   sunzen  solar zenith angle (degrees)
    C
    C   sunaz   solar azimuth angle (clockwise from due north, degrees) 
    C
    C   nrmzen  zenith angle of surface normal vector
    C           (nrmzen=0 for a horizontal surface)
    C
    C   nrmaz   azimuth angle of surface normal vector (nrmaz=45 degrees
    C           for a surface that slopes down in the north-east direction)
    C
    C OUTPUT:
    C   result  cosine of angle between sun and instrument 
    C           = cos(sza) if instrument pointing to zenith
    C
    C AUTHOR:   Yan Shi, PNNL, 10/2/2008 
    C           converted from IDL code by Paul Ricchiazzi
    C           Institute for Computational Earth System Science
    C           University of California, Santa Barbara
    C           paul@icess.ucsb.edu
    '''
    zs = np.cos(np.deg2rad(sunzen))
    ys = np.sin(np.deg2rad(sunzen))*np.cos(np.deg2rad(sunaz))
    xs = np.sin(np.deg2rad(sunzen))*np.sin(np.deg2rad(sunaz))
    zv = np.cos(np.deg2rad(nrmzen))
    yv = np.sin(np.deg2rad(nrmzen))*np.cos(np.deg2rad(nrmaz))
    xv = np.sin(np.deg2rad(nrmzen))*np.sin(np.deg2rad(nrmaz))
    
    muslope = xs*xv + ys*yv + zs*zv
    
    return muslope

"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(description='OER Radiometric averaging')
parser.add_argument('DataPath', metavar='DataPath', type=str, help='full path to SPN1 file with tilts')
parser.add_argument('--LatLon', nargs='+', type=str, help='lat(decimal degN) lon(decimal degE)')

args = parser.parse_args()

unaveraged_data = CSV2Dic(args.DataPath)

print("{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}").format('Date','GtDt','Heading', 'Pitch', 'Role', 'instzen', 'instaz', 'sunzen', 'sunaz', 'corr_sza', 'k_ratio', 'G_corr_factor','SPN Total')

for k,v in enumerate(unaveraged_data['Time']):
    
    GtDt = np.float(unaveraged_data['Total'][k]) - np.float(unaveraged_data['Diffuse'][k])

    ### Convert time into a datetime object - account for local2UTC conversion if necessary
    time_f = datetime.datetime.strptime(v,'%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') 
    #time_f = (datetime.datetime.strptime(v,'%m/%d/%Y %H:%M:%S') + datetime.timedelta(8./24.)).strftime('%Y-%m-%d %H:%M:%S') 
    if not args.LatLon:
        sunzen, sunaz = solar_zenith(time_f)
    else:
        sunzen, sunaz = solar_zenith(time_f, lat=args.LatLon[0], lon=args.LatLon[1])
    instzen, instaz = rph2za(unaveraged_data['Pitch'][k], unaveraged_data['Role'][k], unaveraged_data['Heading'][k])
    if instaz <0:
        instaz = (180+instaz)+180
    cos_sza = muslope(sunzen,sunaz,instzen,instaz)
    corr_sza = np.rad2deg(np.arccos(cos_sza))

    if (corr_sza >= 80.):
        k_ratio = 1e35
        G_corr_factor = 1
    elif (GtDt < 5):
        k_ratio = 1e35
        G_corr_factor = 1           
    else:
        k_ratio = ( np.float(unaveraged_data['Diffuse'][k]) * cos_sza ) / (GtDt)
        G_corr_factor = (np.cos(np.deg2rad(sunzen)) + k_ratio)/(cos_sza + k_ratio) 

            
    print "{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}".format(time_f,GtDt,
             unaveraged_data['Heading'][k], unaveraged_data['Pitch'][k], unaveraged_data['Role'][k], instzen, instaz, sunzen, sunaz, corr_sza, k_ratio, G_corr_factor,np.float(unaveraged_data['Total'][k]))
