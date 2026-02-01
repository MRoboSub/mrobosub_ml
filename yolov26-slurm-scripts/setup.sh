#!/bin/bash
USAGE="USAGE: ./setup.sh"
if [ "$1" == "usage" ] || [ "$1" == "Usage" ] || [ "$1" == "USAGE" ]
then
    echo $USAGE
    exit
fi

unset SSH_ASKPASS
chmod +x ./*.sh
git config core.filemode false

echo
echo "---Setting up ultralytics repo---"
if [ ! -d 'ultralytics/.git' ]
then
    git clone https://github.com/ultralytics/ultralytics
else
    cd ultralytics
    git pull --no-rebase
    cd ..
fi
echo

echo "---Setting up virtual environment---"
NAME=training_env
cd ..
if [ ! -d 'training_env/lib/python3.9' ]
then
    if [ -d 'training_env' ]
    then
        rm -rf training_env
    fi
    echo CREATING venv $NAME
    python3 -m venv $NAME
else
    echo "virtual environment already exists"
fi
python3 -m venv --upgrade training_env/
cd yolov26n-slurm-scripts
echo
