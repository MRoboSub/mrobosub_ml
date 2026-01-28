#!/bin/bash

# this script runs job_submission.sh on slurm compute node and collects logs
# job_submission.sh in turn runs Yolov5s.sh

while getopts r flag
do
    case "$flag" in
         r)
            NUM=$(ls | grep log | wc -l)
            NUM=$(($NUM+1))
            echo "Reset log number counter and start anew in new folder: './log_files_$NUM"
            mkdir log_files_$NUM
    esac
done

sbatch ./job_submission.sh

NUM=$(ls | grep log | wc -l)

DIR="./log_files_$NUM"
if [ -d "$DIR" ]; then 
    :
else 
    NUM=$(($NUM+1))
    mkdir log_files_$NUM
    DIR="./log_files_$NUM"
    echo "Made directory '$DIR'"
fi

cd ./log_files_$NUM

LOG_NUM=$(ls | grep log | wc -l)
LOG_NUM=$(($LOG_NUM+1))

mkdir log_set_$LOG_NUM

mkdir log_set_$LOG_NUM/error_files
mkdir log_set_$LOG_NUM/output_files

cd ..

var=0
while [ $var -le 0 ]
do
    var=$(ls | grep err | wc -l)
    sleep 0.2
done

mv ./*.err ./log_files_$NUM/log_set_$LOG_NUM/error_files
mv ./*.out ./log_files_$NUM/log_set_$LOG_NUM/output_files