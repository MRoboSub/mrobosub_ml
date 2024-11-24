import os
import sys
import json
# import glob
# import math
# import random

TRAIN_PERCENT = 0.75
VALIDATE_PERCENT = 1 - TRAIN_PERCENT
TEST_SET = []
classes = ["gate", "gman", "bootlegger", "gun", "badge"]

def generateFiles(json_file_name, model_num):
   global TRAIN_PERCENT, VALIDATE_PERCENT, TEST_SET

   TRAININGDATA_PATH = "/content/drive/Shareddrives/Michigan Robotic Submarine/Software/ML Training/yolov5/"
   DRIVE_PATH = TRAININGDATA_PATH + "Model {}/".format(model_num)

   # Create Data/images and Data/labels
   try:
      os.mkdir("Data/")
      #os.mkdir("Data/images") images have been moved to TrainingData folder
      os.mkdir("Data/labels")
   except:
      print("Error generating the Data directory and Data/labels directory - did they already exist?")

   # Parse JSON file from LabelBox
   # - Creates label text files (e.g. 02-14-2021_1.png)
   with open(json_file_name) as f1:

      x = json.load(f1)
      for count, z in enumerate(x):
         tempDict = z["Label"]
         tempKey = "objects"


         # Only make text file for labeled images
         if tempKey in tempDict.keys():
            file = z["External ID"]
            # Remove any TEST_SET files
            if file in TEST_SET:
              continue
            file = file.split(".")[0]
            img_width, img_height = float(file.split("_")[1]), float(file.split("_")[2])

            if not z["Skipped"]:# if there was a label for this image
               if z["Agreement"] == -1 or z["Agreement"] > 0.75: #if it has high enough consensus or only labeled by 1 person
                  with open("Data/labels/{}.txt".format(file), "w+") as f2:
                     for cnt, label in enumerate(z["Label"]["objects"]): # loop through labels in this image and write to label file
                        x_center = (label["bbox"]["left"] + (label["bbox"]["width"] / 2.0)) / img_width
                        y_center = (label["bbox"]["top"] + (label["bbox"]["height"] / 2.0)) / img_height
                        width = label["bbox"]["width"] / img_width
                        height = label["bbox"]["height"] / img_height
                        class_name = classes.index(label["value"])
                        f2.write("{} {} {} {} {}".format(class_name, x_center, y_center, width, height))
                        if cnt < len(z["Label"]["objects"]) - 1:
                           f2.write("\n")

   with open("model_{}.yaml".format(model_num), "w+") as f:
        f.write("# Train/val/test sets as 1) dir: path/to/imgs, 2) file: path/to/imgs.txt, or 3) list: [path/to/imgs1, path/to/imgs2, ..]\n" +
                "path: ../mrobosub_ml/Data  # dataset root dir\n" +
                "train: images # train images (relative to 'path') 128 images\n" +
                "val: images  # val images (relative to 'path') 128 images\n" +
                "test:  # test images (optional)\n" +
                "# Classes\n" +
                "nc: 5  # number of classes\n" +
                "names: [ 'gate', 'gman', 'bootlegger', 'gun', 'badge']  # class names)")
   f.close()
        


# Main Function
if __name__ == '__main__':
  if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("[ERROR] usage: python3 generateTrainingFiles.py JSONFILENAME.json MODEL_NUM [optional: WB]")
    exit()

  wb = False
  if len(sys.argv) == 4:
    if (sys.argv[3] != "WB"):
      print("[ERROR]: should the 4th argument be \"WB\"?")
      exit()
    else:
      wb = True

  generateFiles(json_file_name=str(sys.argv[1]), model_num=str(sys.argv[2]))
