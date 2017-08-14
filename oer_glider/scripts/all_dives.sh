#!/bin/bash

: '
#Spring 2017 Deployment
data_dir="/Volumes/WDC_internal/Users/bell/in_and_outbox/2017/Oculus_Glider/bering_sea/p40106[456]*.nc"
prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/"
cal_file="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/inst_config/spring_test_2017.yaml"

for data_file in $data_dir
do
    echo ${data_file}
    python ${prog_dir}oer_glider_ncplot.py ${data_file}
done
'

#Fall 2017 Deployment
root_path="/home/pavlof/bell"
data_dir="/home/ecoraid/data/2017/Profilers/OculusGliders/bering_sea_fall17/sg401/p401*.nc"
prog_dir="${root_path}/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/"
cal_file="${root_path}/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/inst_config/spring_test_2017.yaml"

for data_file in $data_dir
do
    echo ${data_file}
    python ${prog_dir}oer_glider_ncplot.py ${data_file}
done
