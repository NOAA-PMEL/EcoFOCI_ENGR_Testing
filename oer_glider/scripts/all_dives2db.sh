#!/bin/bash

root_path="/home/pavlof/bell"
data_dir="/home/ecoraid/data/2017/Profilers/OculusGliders/bering_sea_fall17/sg401/p4010*.nc"
prog_dir="${root_path}/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/"
cal_file="${root_path}/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/inst_config/spring_test_2017.yaml"

for data_file in $data_dir
do
    echo ${data_file}
    python ${prog_dir}oer_glider_dbload.py ${data_file}
done


