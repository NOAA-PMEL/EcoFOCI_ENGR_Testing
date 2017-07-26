#!/bin/bash

data_dir="/Volumes/WDC_internal/Users/bell/ecoraid/2017/Profilers/OculusGliders/sg401/p401*.nc"
prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/"
cal_file="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_ENGR_Testing/oer_glider/inst_config/spring_test_2017.yaml"

for data_file in $data_dir
do
    echo ${data_file}
    python ${prog_dir}oer_glider_dbload.py ${data_file}
done


