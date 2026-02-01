#!/bin/bash

#default values for training model
IMAGE=640
BATCH=64
EPOCHS=256
DATA="../model.yaml" #file that says where to get training data
#make sure this and test data is downloaded before^

WEIGHTS="yolo26n.pt" #weights file (is likely the default that came with yolov5)
CACHE=""

#default image size for running inference
IMAGE2=672

# automatic weight folder detection: finds the most recent exp folder
# based on number of exp folders. The most recent is the next exp folder number
# based on chronological order. Then, this program uses that found best.pt for
# detect.py and export.py
DIR="ultralytics/runs/train"
#create numerical weights/results folder naming system for models trained with Yolov5.
#first folder = exp0
#second = exp1
#nth = expn
if [ -d "$DIR" ]; then
    cd ./ultralytics/runs/train
    exp_num=$(ls | grep exp | wc -l)
    echo
    echo "weights stored in base_dir/ultralytics/runs/train/exp$exp_num."
    echo
    cd ..
    cd ..
    cd .. #back in base folder
else
    #if just freshly cloned, then DIR will not exist, and neither will any 
    # exp folders in DIR since DIR only exists after at least one model has been trained
    # in yolov5.
    exp_num=0;
fi

#Name used for folder that will store the weights/results of the model that is going to be trained. 
#This folder is in yolov5/runs/train
#Also the name of the folder that will store inferencing files in ./yolov5/runs/detect
#This is passed as the --name flag name argument into train.py and detect.py
EXP="exp$exp_num"
WOUTPUT="./runs/train/$EXP/weights/best.pt" #output for weights
SOURCE="../test_data/" #test data for inferencing; this will be the path 
#when detect.py is called the base_directory/yolov5 directory

CONF=0.08 #default confidence threshold for inferencing


#detect optional arugments with flags and set respective variables equal to them
while getopts :i:b:e:d:w:s:l:o:f:c flag
do
    case "$flag" in
         i) #training model: image size
             IMAGE=${OPTARG}
             ;;
         b) #training model: batch size
             BATCH=${OPTARG}
             ;;
         e) #training model: number of epochs
             EPOCHS=${OPTARG}
             ;;
         d) #training model: path of file that get data from
             DATA=${OPTARG}
             ;;
         w) #training model: weights file
             WEIGHTS=${OPTARG}
             ;;
         s) #inferencing: source directory path
             SOURCE=${OPTARG}
             ;;
         l) #inferencing: image size
             IMAGE2=${OPTARG}
             ;;
         o) #inferencing and converting to weights: trained weights output file path
             WOUTPUT=${OPTARG}
             ;;
         f) #inferencing: confidence threshold
             CONF=${OPTARG}
             ;;
         c) #training model: binary option for cache
             CACHE="--cache"
             ;;    
             
    esac
done

#start virtual environment (should be installed in ~)
source ~/mrobosub_ml/training_env/bin/activate

#install dependencies 
cd ultralytics
pip3 install --upgrade pip
echo
echo "Upgraded pip3 as needed"
echo
pip3 install ipython
echo
echo "Installed IPython"
pip3 install .
touch installed.txt
pip3 freeze > ../installed.txt #installed.txt holds the installed libraries and packages
cd .. #in base folder
echo
python3 Yolov26n_setup.py #Setting up for inferencing after training the model
echo
echo "Finished installing YOLOv11n dependencies"
echo "See installed.txt for installed dependencies"
cd ultralytics
echo
echo
echo "Training the model:"
echo
echo "i:$IMAGE, b:$BATCH, e:$EPOCHS, d:$DATA, w:$WEIGHTS, $CACHE"
echo
#make sure path arguments are according to current location: yolov5, which is in base folder
yolo detect train data=$DATA  model=model.yaml pretrained=$WEIGHTS epochs=$EPOCHS imgsz=$IMAGE batch=$BATCH
echo
echo "Running model on test set:"
echo
yolo val weights=$WOUTPUT data=$DATA imgsz=$IMAGE
echo 
echo "Converting weights:"
echo
yolo export weights=$WOUTPUT format=onnx
echo 
echo "Finished ML Training"
deactivate
