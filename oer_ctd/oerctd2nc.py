#!/usr/bin/env python

"""
 wetstar2nc.py
 
  
 Built using Anaconda packaged Python:
 

"""

# Standard library.
import datetime, os

# Scientific stack.
from netCDF4 import Dataset

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 13)
__modified__ = datetime.datetime(2014, 01, 29)
__version__  = "0.2.0"
__status__   = "Development"

"""------------------------- Routines (from utilites) --------------------------------"""
class DataTimes(object):
    """
    Purpose
    -------
    
    Convert a string time of the form 'mmm dd yyyy hh:mm:ss' to python ordinal date or 
    EPIC time (two time keys)

    Example
    -------
    >>>import ctd
    >>>timeinstance = ctd.DataTimes(time_str='jan 01 2013 12:00:00')
    >>> EPIC_Day, EPIC_time = timeinstance.get_EPIC_date()
      
    Reference
    ---------
    PMEL-EPIC Conventions (misprint) says 2400000
    http://www.epic.noaa.gov/epic/eps-manual/epslib_ch5.html#SEC57 says:
    May 23 1968 is 2440000 and July4, 1994 is 2449538
              
    """
    ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
    ref_time_epic = 2440000.
    offset = ref_time_epic - ref_time_py
    
    def __init__(self, time_str='01 jan 0001 00:00:00', isdatetime=False, ismmddyy=False):
        self.time_str = time_str
        if isdatetime == False and ismmddyy==False:
            self.date_time = datetime.datetime.strptime(time_str, '%d %b %Y %H:%M:%S')
        elif isdatetime == True and ismmddyy==False:
            self.date_time = time_str
        elif isdatetime == False and ismmddyy == True:
            self.date_time = datetime.datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')

                        
    def get_python_date(self):
        intday = self.date_time.toordinal()
        fracday = (self.date_time.hour / (24.)) + (self.date_time.minute / (24. * 60.)) +\
                    (self.date_time.second / (24. * 60. * 60.))
        return(intday + fracday)
        
    def get_EPIC_date(self):
        time1 = self.date_time.toordinal() + DataTimes.offset
        fracday = (self.date_time.hour * (60. * 60. * 1000.)) + (self.date_time.minute * (60. * 1000.)) +\
                    (self.date_time.second * (1000.))
        time2 = fracday 
        
        return(time1, int(round(time2)) )

"""-------------------------------NCFile Creation--------------------------------------"""

class OERCTD_NC(object):
    """ Class instance to generate a NetCDF file.  
    Assumes data format and information ingested is a dataframe object from ctd.py 

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = OERCTD_NC()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc'):
        """data is a numpy array of temperature values"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, OERCTD_NC.nc_read, format=OERCTD_NC.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='B', Water_Depth=9999, Prog_Cmnt='',\
                        Experiment='', Edit_Cmnt='', Station_Name=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.INST_TYPE = ''
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = 'oerctd2nc.py V' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
                        
        
    def dimension_init(self, time_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], time_len ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], 1 ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self):
        """
        """
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []
        
        #temp
        rec_vars.append('T_20')
        rec_var_name.append( 'T' )
        rec_var_longname.append( 'TEMPERATURE (C)' )
        rec_var_generic_name.append( 'temp' )
        rec_var_units.append( 'C' )
        rec_var_FORTRAN.append( 'f10.2' )
        rec_var_epic.append( 20 )

        #pres
        rec_vars.append('P_1')
        rec_var_name.append( 'P' )
        rec_var_longname.append( 'PRESSURE (db)' )
        rec_var_generic_name.append( 'pres' )
        rec_var_units.append( 'db' )
        rec_var_FORTRAN.append( 'f10.1' )
        rec_var_epic.append( 1 )

        #cond
        rec_vars.append('C_50')
        rec_var_name.append( 'C' )
        rec_var_longname.append( 'CONDUCTIVITY' )
        rec_var_generic_name.append( 'con' )
        rec_var_units.append( 'mmho/cm' )
        rec_var_FORTRAN.append( ' ' )
        rec_var_epic.append( 50 )

        #sal
        rec_vars.append('S_41')
        rec_var_name.append( 'S' )
        rec_var_longname.append( 'Salinity (psu)' )
        rec_var_generic_name.append( 'sal' )
        rec_var_units.append( 'PSU' )
        rec_var_FORTRAN.append( ' ' )
        rec_var_epic.append( 41 )

        
        rec_vars = ['time','time2','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', '', ''] + rec_var_FORTRAN
        rec_var_units = ['True Julian Day', 'msec since 0:00 GMT','dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['i4', 'i4'] + ['f4' for spot in rec_vars[2:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[5:]]
        rec_epic_code = [624, 624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[0]))#time2
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[4], rec_var_type[4], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[5:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+5], rec_var_type[i+5], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time1=None, time2=None, CastLog=False):
        """ """
        self.var_class[0][:] = time1
        self.var_class[1][:] = time2
        self.var_class[2][:] = depth
        self.var_class[3][:] = latitude
        self.var_class[4][:] = longitude #PMEL standard direction

    def add_data(self, data=None):
        """ """
        di = self.rec_vars.index('T_20')
        self.var_class[di][:] = data[0]
        
        di = self.rec_vars.index('P_1')
        self.var_class[di][:] = data[1]
        
        di = self.rec_vars.index('C_50')
        self.var_class[di][:] = data[2]
        
        di = self.rec_vars.index('S_41')
        self.var_class[di][:] = data[3]
        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.History = self.History + ' ' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()

