#!/usr/bin/env python

"""
oer_processing.py
 
parse data feed from oer bouy with experimental SPN1 radiometer package into individual ascii csv
    files for further display and processing.

 Using Anaconda packaged Python 
"""

#System Stack
import datetime
import argparse
import pymysql
import sys

#Science Stack
import numpy as np



__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 06, 07)
__modified__ = datetime.datetime(2014, 06, 07)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'mooring','csv','timeseries', 'dygraphs'

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
    
""" ---------------------------------- Data Read --------------------------------------"""

def OER_READ(filein):
    spn,swr,lwr ={},{},{}
    
    spk, swk, lwk = 0, 0, 0
    with open(filein) as f:
        for k, line in enumerate(f.readlines()):

            #unknown shift in output provides this character which should be removed
            if ('\x00' in line):
                line = line.replace('\x00','')
            if ('S ' in line):
                line = line.replace('S ','')
                
            line = line.strip()
            
            if ('No compass reading' in line):
                line = line.replace('No compass reading', '-999, -999, -999')
            
            if ('SPN' in line):  #Get SPN lines
                spn[spk] = line.split(',')
                spk +=1
            elif ('SWR' in line):  #Get SWR lines.
                swr[swk] = line.split(',')
                swk +=1
            elif ('LWR' in line):  # Get end of file.
                lwr[lwk] = line.split(',')
                lwk +=1

    return spn,swr,lwr
    
def OER_ENG2SCI(data_dic, verbose=False):
    """ given a dictionary of values from text file """
    
    sample_num = 0
    spn,swr,lwr = {},{},{}

    of = open('2016_OER_SPN1.csv','w')
    
    print"Time,Total,Diffuse,Sunshine,Heading,Pitch,Role"
    of.write("Time,Total,Diffuse,Sunshine,Heading,Pitch,Role\n")

    for k,v in sorted(data_dic[0].items()):
        #spn data feed

        try:
            if verbose:
                print "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(v[1]+' '+v[2],float(v[3]),float(v[4]),float(v[5]),float(v[6]),float(v[7]),float(v[8]))
            of.write("{0},{1},{2},{3},{4},{5},{6}\n".format(v[1]+' '+v[2],float(v[3]),float(v[4]),float(v[5]),float(v[6]),float(v[7]),float(v[8])))
        except ValueError:
            if verbose:
                print "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(v[1]+' '+v[2],float(v[3]),float(v[4]),'',float(v[6]),float(v[7]),float(v[8]))
            of.write("{0},{1},{2},{3},{4},{5},{6}\n".format(v[1]+' '+v[2],float(v[3]),float(v[4]),'[]',float(v[6]),float(v[7]),float(v[8])))
        except IndexError:
            of.write("{0},,,,,,\n".format(v[1]+' '+v[2]))

    of.close()

    of = open('2016_OER_SWR.csv','w')
    print"Time,SWR -STD,SWR,SWR +STD"
    of.write("Time,SWR -STD,SWR,SWR +STD\n")

    coef1 = [0.00000768, 0.0000036316996, -0.0000010448401]
    for k,v in sorted(data_dic[1].items()):
        #swr data feed
        std_dev = ((np.sqrt((1/(float(v[5])-1)*(float(v[3])-(1/float(v[5]))*(float(v[4])**2)))) * coef1[1]) / coef1[0] )
        if verbose:
            print "{0}, {1}, {2}, {3}".format(v[1]+' '+v[2],
                ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] )-std_dev,
                ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] ),
                ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] )+std_dev)
        of.write("{0},{1},{2},{3}\n".format(v[1]+' '+v[2],
            ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] )-std_dev,
            ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] ),
            ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] )+std_dev))

    of.close()

    ### combine the SPN and SW data together (assumes consistent time stamps)
    of = open('2016_OER_SWR_SPN1.csv','w')

    print"Time,SPN Total,SPN Diffuse,SWR,Heading,Pitch,Role"
    of.write("Time,SPN Total,SPN Diffuse,SWR,Heading,Pitch,Role\n")

    coef1 = [0.00000768, 0.0000036316996, -0.0000010448401]
    tempspn1 = sorted(data_dic[0].items())
    for k,v in sorted(data_dic[1].items()):
        #both SWR and SPN1 datafeed (should have same time stamps)
        try:
            if verbose:
                print "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(v[1]+' '+v[2],
                    float(tempspn1[k][1][3]),float(tempspn1[k][1][4]),
                    ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] ),
                    float(v[6]),float(v[7]),float(v[8]))
            of.write("{0},{1},{2},{3},{4},{5},{6}\n".format(v[1]+' '+v[2],
                float(tempspn1[k][1][3]),float(tempspn1[k][1][4]),
                ((float(v[4])/float(v[5]) * coef1[1]) / coef1[0] ),
                float(v[6]),float(v[7]),float(v[8])))
        except:
            of.write("{0},,,,,,\n".format(v[1]+' '+v[2]))
    of.close()

    ### output LW data with temperature corrections
    of = open('2016_OER_LWR.csv','w')

    print "Time,LWR,LWR Temp Corrected,Heading,Pitch,Role,Case Temp,Dome Temp"
    of.write("Time,LWR,LWR Temp Corrected,Heading,Pitch,Role,Case Temp,Dome Temp\n")

    coef2 = [0.0000004073936, 0.000006002412, 0.00000304]
    coef3 = [1.028742e-03,5.508331e-04,1.906367e-06,-5.003222e4, 2.500801e8]
    coef4 = [1.028742e-03,5.508331e-04,1.906367e-06,-5.003222e4, 2.500801e8]
    for k,v in sorted(data_dic[2].items()):
        #lwr data feed dome/case temps
        ct = float(v[6])/float(v[7])
        cr = coef3[3] + (coef3[4]*(1. / (ct+2500)))
        cx = np.log10(cr)
        ct_sci = 1 / (coef3[0] + (coef3[1] * cx) + ( coef3[2] * cx * cx * cx )) 

        dt = float(v[8])/float(v[9])
        dr = coef4[3] + (coef4[4]*(1. / (dt+2500)))
        dx = np.log10(dr)
        dt_sci = 1.0 / (coef4[0] + (coef4[1] * dx) + ( coef4[2] * dx * dx * dx )) 

        sigma=5.6704e-8
        #lwr data feed
        PIR = ((float(v[4])/float(v[5]) * coef2[0] + coef2[1]) / coef2[2] )
        if verbose:
            print "{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}".format(v[1]+' '+v[2], PIR, 
                (sigma*(dt_sci**4)) + PIR - 3.5*sigma*((dt_sci**4)-(ct_sci**4)),
                float(v[10]),float(v[11]),float(v[12]),ct_sci,dt_sci)
        of.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(v[1]+' '+v[2], PIR, 
            (sigma*(dt_sci**4)) + PIR - 3.5*sigma*((dt_sci**4)-(ct_sci**4)),
            float(v[10]),float(v[11]),float(v[12]),ct_sci,dt_sci))

    of.close()
                    
    return
        
def steinhart_hart(resistance, mtr_coef):
    if resistance <= 0:
        shhh = 0
    else:
        shhh = 1.0 / (mtr_coef[0] + (mtr_coef[1] * np.log10(resistance)) + (mtr_coef[2] * np.log10(resistance)**3))

    return shhh
"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(description='OER Radiometric processing')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('--cal_coeffs', nargs='+', type=float, help='a b c')
parser.add_argument('-v','--verbose', action="store_true", help="output text")

args = parser.parse_args()

if args.verbose:
    verbose = True
else:
    verbose = False

data = OER_READ(args.DataPath)

OER_ENG2SCI(data, verbose)