#!/bin/bash

data_dir="/Users/bell/Downloads/saildrone_data/sd-128/*.csv"
prog_dir="/Users/bell/Programs/Python/MooringDataProcessing/oer_radiometer/"
output_dir="/Users/bell/sites/bell/experimental/2015_Saildrone/"

for data_file in $data_dir
do
    names=(${data_file//\// })
    python ${prog_dir}saildrone_processing.py ${data_file} --GPS >> ${output_dir}test_128.geo.json 
    python ${prog_dir}saildrone_processing.py ${data_file} --GPS --subsample >> ${output_dir}sd_thin_128.geo.json
    python ${prog_dir}saildrone_processing.py ${data_file} --ATRH >> ${output_dir}Saildrone_current_ATRH_128.csv
    python ${prog_dir}saildrone_processing.py ${data_file} --CTD >> ${output_dir}Saildrone_current_CTD_128.csv
done


data_dir="/Users/bell/Downloads/saildrone_data/sd-126/*.csv"
prog_dir="/Users/bell/Programs/Python/MooringDataProcessing/oer_radiometer/"
output_dir="/Users/bell/sites/bell/experimental/2015_Saildrone/"

for data_file in $data_dir
do
    names=(${data_file//\// })
    python ${prog_dir}saildrone_processing.py ${data_file} --GPS >> ${output_dir}test_126.geo.json 
    python ${prog_dir}saildrone_processing.py ${data_file} --GPS --subsample >> ${output_dir}sd_thin_126.geo.json
    python ${prog_dir}saildrone_processing.py ${data_file} --ATRH >> ${output_dir}Saildrone_current_ATRH_126.csv
    python ${prog_dir}saildrone_processing.py ${data_file} --CTD >> ${output_dir}Saildrone_current_CTD_126.csv
done
