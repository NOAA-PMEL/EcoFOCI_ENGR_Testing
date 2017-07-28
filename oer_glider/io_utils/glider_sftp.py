#!/usr/bin/env python

"""
 Background:
 --------
 glider_sftp.py
 
 
 Purpose:
 --------
 retrieve updated glider data from APL sftp site

 must have approved of the host:key process once before (so connect via command line sftp prior to using this program)

 History:
 --------


"""


import datetime
import pysftp

import ConfigParserLocal

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2017, 07, 26)
__modified__ = datetime.datetime(2017, 07, 26)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'sftp','get data'


## build list of 1000 potential files of form p401xxxx.nc
base_id = 'p401'
ncfile_list = [base_id + str(item).zfill(4) for item in range(1,1000,1)]

sftp_config_file = '/Users/bell/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/EcoFOCI_config/sftp_config/apl_sftp_oculus.pyini'
sftp_config = ConfigParserLocal.get_config(sftp_config_file)

with pysftp.Connection(sftp_config['host'], username=sftp_config['user'], password=sftp_config['password']) as sftp:
    badfile = 0
    sftp.chdir(sftp_config['path'])       # chdir to path in config file
    for ncfile in ncfile_list:
        if sftp.exists('{0}.nc'.format(ncfile)):
            print("Grabbing {0}.nc".format(ncfile)) 
            sftp.get('{0}.nc'.format(ncfile))         # get a remote file
        else:
            print("File {0}.nc does not exist".format(ncfile))
            badfile +=1

        if badfile > 2:
            break