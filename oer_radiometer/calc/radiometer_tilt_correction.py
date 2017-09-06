#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 07:01:14 2017

@author: bell
"""

import numpy as np
import pandas as pd
import ephem


def solar_zenith(timestr='2016-01-01 00:00:00', lat='47.6', lon='-122.32'):
    '''
    Time needs to be a string in UTC
    using subroutine ephem for solar positions

    Todo: Can this be vectorized?
    '''
    location = ephem.Observer()
    location.lon, location.lat, location.date = lon,lat,timestr
    sun = ephem.Sun()
    sun.compute(location)
    
    sun_string = True
    if sun_string: 
        sun_az = str(sun.az).split(':')
        sun_el = str(sun.alt).split(':')
        sun_az = float(sun_az[0]) + float(sun_az[1])/60. + float(sun_az[2])/3600.
        sun_el = float(sun_el[0]) + float(sun_el[1])/60. + float(sun_el[2])/3600.
    else:
        sun_az = ephem.degrees(sun.az)
        sun_el = ephem.degrees(sun.alt)
        
    return (90. - sun_el, sun_az)
				
def prh2za(pitch,roll,heading):
    '''
    from Fortran/IDL subroutine by Paul Ricchiazzi, 25 Feb 97 paul@icess.ucsb.edu

    all angles in degrees
    pitch  : positive values indicate nose up
    roll   : positive values indicate right wing down
    azimuth: positive values clockwise, w.r.t. NORTH
    assume aircraft heading north: rotate around roll

    Input: Either Pandas Series or Numpy Array
    
    '''
    
    if isinstance(pitch, pd.Series):
        ### pandas series
        roll_rad = np.deg2rad(roll)
        pitch_rad = np.deg2rad(pitch)
        heading_rad = np.deg2rad(heading)

        uz = np.cos(roll_rad)*np.cos(pitch_rad)
        ux = np.sin(roll_rad)
        uy = -1.0 * np.cos(roll_rad) * np.sin(pitch_rad)

        vz = uz
        vx = ux * np.cos(heading_rad) + uy * np.sin(heading_rad)
        vy = uy * np.cos(heading_rad) - uy * np.sin(heading_rad)

        zenith = np.rad2deg(np.arccos(vz))
        vy.loc[ vy == 0.0 ] = 0.00000001
        azimuth = np.rad2deg(np.arctan2(vx,vy))
        
        return (zenith.values, azimuth.values)

    else:
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

    Input: Either Pandas Series or Numpy Array

    '''


    zs = np.cos(np.deg2rad(sunzen))
    ys = np.sin(np.deg2rad(sunzen))*np.cos(np.deg2rad(sunaz))
    xs = np.sin(np.deg2rad(sunzen))*np.sin(np.deg2rad(sunaz))
    zv = np.cos(np.deg2rad(nrmzen))
    yv = np.sin(np.deg2rad(nrmzen))*np.cos(np.deg2rad(nrmaz))
    xv = np.sin(np.deg2rad(nrmzen))*np.sin(np.deg2rad(nrmaz))
    
    muslope = xs*xv + ys*yv + zs*zv
 
    if isinstance(sunzen, pd.Series):
        ### pandas series    
        return muslope.values
    else:
        return muslope
