#!/bin/bash
USAGE="USAGE: ./setup.sh [training data git url] [test data git url]"
if [ "$1" == "usage" ] || [ "$1" == "Usage" ] || [ "$1" == "USAGE" ]
then
    echo $USAGE
    exit
fi

unset SSH_ASKPASS
chmod +x ./*.sh
git config core.filemode false

echo
echo "---Setting up yolov5 repo---"
if [ ! -d 'yolov5/.git' ]
then
    git clone https://github.com/ultralytics/yolov5
else
    cd yolov5
    git pull --no-rebase
    cd ..
fi
echo

echo
echo "---Setting up dataset repo---"
 if [ ! -d 'mrobosub_datasets/.git' ]
then
    git clone https://gitlab.eecs.umich.edu/mrobosub/mrobosub_dataset_2023.git
    cd mrobosub_dataset_2023
    git pull --no-rebase
    cd ..
fi
echo

echo "---Setting up virtual environment---"
NAME=training_env
cd ..
if [ ! -d 'training_env/lib/python3.9' ]
then
    if [ -d 'traning_env' ]
    then
        rm -rf training_env
    fi
    echo CREATING venv $NAME
    python3 -m venv $NAME
else
    echo "virtual environment already exists"
fi
python3 -m venv --upgrade training_env/
cd hpc-cluster-slurm-submission-scripts
echo
