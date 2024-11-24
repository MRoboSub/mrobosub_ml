#!/bin/bash

#start virtual environment (should be installed in ~)
source ~/training_env/bin/activate

#install dependencies 
# cd yolov5
pip3 install --upgrade pip
echo
echo "Upgraded pip3 as needed"
echo
pip3 install ipython
echo
echo "Installed IPython"
pip3 install ultralytics
touch installed.txt
pip3 freeze > ../installed.txt #installed.txt holds the installed libraries and packages
# cd .. #in base folder
echo
# python3 Yolov5s_setup.py #Setting up for inferencing after training the model
echo
echo "Finished installing YOLOv5 dependencies"
echo "See installed.txt for installed dependencies"
cd yolov11_obb
echo
echo
echo "Training the model:"
echo
echo "i:$IMAGE, b:$BATCH, e:$EPOCHS, d:$DATA, w:$WEIGHTS, $CACHE"
echo
#make sure path arguments are according to current location: yolov5, which is in base folder
python3 yolov11_segment_train.py
echo
echo "Running model v11 on test set:"
echo 
echo "Finished ML Training"
deactivate
