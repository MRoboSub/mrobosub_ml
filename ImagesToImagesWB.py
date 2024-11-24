import cv2
import os
import sys
import argparse
import glob
import numpy as np

def gray(img):
   def wb(channel, perc = 0.05):
      mi, ma = (np.percentile(channel, perc), np.percentile(channel,100.0-perc))
      channel = np.uint8(np.clip((channel-mi)*255.0/(ma-mi), 0, 255))
      return channel

   return np.dstack([wb(channel, 0.05) for channel in cv2.split(img)] )

if __name__=="__main__":
    
    pathOut = "imagesWB/"
    try:
        os.mkdir(pathOut)
    except:
        print(pathOut + " already exists")

    list_of_imgs = glob.glob("images/*")

    if len(list_of_imgs) == 0:
        print("No images to convert. Did you add them to the images/ folder?")
    
    num_converted = 0
    for imgname in list_of_imgs:
        if (":Zone.Identifier" in imgname):
            os.remove(imgname)
            continue
        img = cv2.imread(imgname, 1)
        imgname = imgname.split("/")[1]
        img = gray(img)
        cv2.imwrite(pathOut + imgname, img)
        num_converted += 1
        print( "converted " + imgname)
    print("DONE: Converted", num_converted, "images.")

