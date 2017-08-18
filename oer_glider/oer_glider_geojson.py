#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_geojson.py
 
 
 Purpose:
 --------
 dump glider locations to geojson file

 History:
 --------


"""
import argparse, os

from io_utils.EcoFOCI_db_io import EcoFOCI_db_oculus
from io_utils import ConfigParserLocal

parser = argparse.ArgumentParser(description='Load Glider NetCDF data into MySQL database')
parser.add_argument('-ini','--ini_file', type=str,
               help='complete path to yaml instrument ini (state) file')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing
state_config = ConfigParserLocal.get_config_yaml(args.ini_file)

###
#
# load database
config_file = 'EcoFOCI_config/db_config/db_config_oculus_root.pyini'
EcoFOCI_db = EcoFOCI_db_oculus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

data = EcoFOCI_db.position2geojson(table=state_config['db_table'],verbose=False)

header = '{"type": "FeatureCollection","features": ['
geojson = []
for value in data.values():
	geojson =geojson + ['{{"type": "Feature","geometry": {{"type": "Point", "coordinates":  [ {lon},{lat} ]}},"properties": {{"divenum":"{dive}"}}}}'.format(lat=value['latitude'],lon=value['longitude'],dive=str(value['divenum']).zfill(4))]

geojson = ",".join(geojson)
geojson = header + geojson + ']}'

print geojson