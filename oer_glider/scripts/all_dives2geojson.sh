#!/bin/bash

#Fall 2017 Deployment
root_path="/home/pavlof/bell"
prog_dir="${root_path}/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/"

state_file="EcoFOCI_config/2017_sg401_south.yaml"

python ${prog_dir}oer_glider_geojson.py -ini ${state_file} > 17Fall_SG401_southward.geojson


state_file="EcoFOCI_config/2017_sg401_north.yaml"

python ${prog_dir}oer_glider_geojson.py -ini ${state_file} > 17Fall_SG401_northward.geojson


