#!/usr/bin/env python

"""
 Background:
 --------
 oer_glider_postprocess.py
 
 
 Purpose:
 --------
 post mission analyis of glider data from db format

 History:
 --------


"""
import argparse, os

import pandas as pd

from io_utils.EcoFOCI_db_io import EcoFOCI_db_oculus
from io_utils import ConfigParserLocal

parser = argparse.ArgumentParser(description='Load Glider NetCDF data into MySQL database')
parser.add_argument('-ini','--ini_file', type=str,
			   help='complete path to yaml instrument ini (state) file')
parser.add_argument('-geojson','--geojson', action="store_true",
			   help='output chosen profile locations as GeoJson file')
parser.add_argument('-dtdz','--dtdz', action="store_true",
			   help='calculate dtdz and add to database')
parser.add_argument('-dtdz_max','--dtdz_max', action="store_true",
			   help='calculate max(dtdz) and add to database')
args = parser.parse_args()



#######################
#
# Data Ingest and Processing
state_config = ConfigParserLocal.get_config(args.ini_file,ftype='yaml')

###
#
# load database
config_file = 'EcoFOCI_config/db_config/db_config_oculus_root.pyini'
EcoFOCI_db = EcoFOCI_db_oculus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)


### Dump location into GeoJson format
if args.geojson:
	data = EcoFOCI_db.position2geojson(table=state_config['db_table'],verbose=False)

	header = '{"type": "FeatureCollection","features": ['
	geojson = []
	for value in data.values():
		geojson =geojson + ['{{"type": "Feature","geometry": {{"type": "Point", "coordinates":  [ {lon},{lat} ]}},"properties": {{"divenum":"{dive}"}}}}'.format(lat=value['latitude'],lon=value['longitude'],dive=str(value['divenum']).zfill(4))]

	geojson = ",".join(geojson)
	geojson = header + geojson + ']}'

	print geojson

### From dt/dp and dsig/dp find max and pressure value
if args.dtdz_max:
	config_file = 'EcoFOCI_config/db_config/db_config_oculus_root.pyini'
	EcoFOCI_db = EcoFOCI_db_oculus()
	(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)
	for divenum in range(state_config['startnum'],state_config['endnum'],1):
		for i, castdirection in enumerate(['d','u']):
			### Determine Thermal boundary depth by looking for max dt/dz in each direction.
			# dt/dz is a three point difference so that the depth it is at is a measured depth
			upper_boundary = pd.read_sql("""SELECT id, time, divenum, castdirection, depth, dtemp_dpress FROM `{table}` 
				WHERE divenum = '{divenum}' AND 
				castdirection = '{castdirection}' ORDER BY dtemp_dpress ASC LIMIT 1""".format(table=state_config['db_table'],divenum=divenum,castdirection=castdirection),db)
			
			print_boundary = True
			update_db = True
			if not upper_boundary.empty and print_boundary:
				print upper_boundary

			#### Keep downcast until upper part of boundary
			if not upper_boundary.empty and update_db and castdirection == 'd':
				sql = """update `{table}` a,
							(select id, depth, temperature, salinity, ddens_dpress,castdirection,divenum FROM `{table}` 
							where divenum = '{divenum}' and castdirection='{castdirection}' and depth < '{depth}') b
							set a.`TwoLayer_merged_temp` = b.temperature,  a.`TwoLayer_merged_sal` = b.salinity
							where a.id = b.id""".format(table=state_config['db_table'],depth=upper_boundary.depth[0],divenum=divenum,castdirection=castdirection)
				EcoFOCI_db.to_sql(sql)
			elif not upper_boundary.empty and update_db and castdirection == 'u':
				sql = """update `{table}` a,
							(select id, depth, temperature, salinity, ddens_dpress,castdirection,divenum FROM `{table}` 
							where divenum = '{divenum}' and castdirection='{castdirection}' and depth > '{depth}') b
							set a.`TwoLayer_merged_temp` = b.temperature,  a.`TwoLayer_merged_sal` = b.salinity
							where a.id = b.id""".format(table=state_config['db_table'],depth=upper_boundary.depth[0],divenum=divenum,castdirection=castdirection)
				EcoFOCI_db.to_sql(sql)

EcoFOCI_db.close()