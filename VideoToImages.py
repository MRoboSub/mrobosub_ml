import cv2
import os
import sys
import argparse
import numpy as np
from datetime import datetime

def extractImages(pathIn, wb):
    number = 0
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success,image = vidcap.read()
    success = True
    pathOut = ""
    if (wb):
        pathOut = "imagesWB/"
    else:
        pathOut = "images/"

    try:
        os.mkdir(pathOut)
    except:
        print(pathOut + " already exists")

    date = datetime.now().strftime("%m%d%Y")
    pathOut += date

    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*250))    #THIS LINE CONTROLS HOW MANY FRAMES PER SECONDS
        success,image = vidcap.read()
        if not success:
            break
        print ('Read a new frame: ', success)
        height, width = image.shape[:2]
        if(wb):
            image = gray(image)
        cv2.imwrite( pathOut + "_" + str(width) + "_" + str(height) + "_" + str(number)+".png", image)     # save frame as JPEG file
        count = count + 1
        number = number + 1

def gray(img):
   def wb(channel, perc = 0.05):
      mi, ma = (np.percentile(channel, perc), np.percentile(channel,100.0-perc))
      channel = np.uint8(np.clip((channel-mi)*255.0/(ma-mi), 0, 255))
      return channel

   return np.dstack([wb(channel, 0.05) for channel in cv2.split(img)] )

if __name__=="__main__":
    wb = False
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: python3 VideoToImages.py PATHTOVIDEOFILE [wb]")
        exit(1)
    elif len(sys.argv) == 3:
        wb = True

    pathToVid = str(sys.argv[1]) # "/Users/andrewhuston/documents/RoboSub/NCSU/forward2.avi"

    extractImages(pathToVid, wb)
