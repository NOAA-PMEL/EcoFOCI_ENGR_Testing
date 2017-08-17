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
from io_utils.EcoFOCI_db_io import EcoFOCI_db_oculus


###
#
# load database
config_file = 'EcoFOCI_config/db_config/db_config_oculus_root.pyini'
EcoFOCI_db = EcoFOCI_db_oculus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

data = EcoFOCI_db.position2geojson(table='2017_fall_sg401_northward',verbose=False)

header = '{"type": "FeatureCollection","features": ['
geojson = []
for value in data.values():
	geojson =geojson + ['{{"type": "Feature","geometry": {{"type": "Point", "coordinates":  [ {lon},{lat} ]}},"properties": {{"divenum":"{dive}"}}}}'.format(lat=value['latitude'],lon=value['longitude'],dive=str(value['divenum']).zfill(3))]

geojson = ",".join(geojson)
geojson = header + geojson + ']}'

print geojson