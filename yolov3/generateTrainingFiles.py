import os
import sys
import json
import glob
import math
import random

TRAIN_PERCENT = 0.75
VALIDATE_PERCENT = 1 - TRAIN_PERCENT
TEST_SET = []
classes = ["gate", "gman", "bootlegger", "buoy"]

def generateFiles(json_file_name, model_num):
   global TRAIN_PERCENT, VALIDATE_PERCENT, TEST_SET

   TRAININGDATA_PATH = "/content/drive/Shareddrives/Michigan Robotic Submarine/Software/ML Training/yolov3/"
   DRIVE_PATH = TRAININGDATA_PATH + "Model {}/".format(model_num)

   # Add test_set files to the dictionary so we don't generate training data for them
   # with open("test_set.txt") as test_set_file:
   #   TEST_SET = test_set_file.readlines()
   # test_set_file.close()

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
            
            with open("Data/labels/{}.txt".format(file), "w+") as f2:
               x_center = (z["Label"]["objects"][0]["bbox"]["left"] + (z["Label"]["objects"][0]["bbox"]["width"] / 2.0)) / img_width
               y_center = (z["Label"]["objects"][0]["bbox"]["top"] + (z["Label"]["objects"][0]["bbox"]["height"] / 2.0)) / img_height
               width = z["Label"]["objects"][0]["bbox"]["width"] / img_width
               height = z["Label"]["objects"][0]["bbox"]["height"] / img_height
               class_name = classes.index(z["Label"]["objects"][0]["value"])
               f2.write("{} {} {} {} {}".format(class_name, x_center, y_center, width, height))
            f2.close()
   f1.close()

   # Generate classes.names
   with open('classes.names', "w+") as f:
      for x in classes:
         f.write(x + "\n")
   f.close()


   # Generate obj.data
   with open('obj.data', "w+") as f:
      f.write("classes = "+ str(len(classes)) +"\n\n")
      f.write("train = " + DRIVE_PATH + "train.txt\n\n")
      f.write("valid = " + DRIVE_PATH + "validate.txt\n\n")
      f.write("names = " + DRIVE_PATH + "classes.names\n\n")
      f.write("backup = " + DRIVE_PATH + "backup/\n")
   f.close()


   # Divide images into training / validation
   list_of_imgs = [file[12:-3] for file in glob.glob("Data/labels/*.txt")]

   train = random.sample(list_of_imgs, math.floor(len(list_of_imgs)*TRAIN_PERCENT))
   validate = []

   for img in list_of_imgs:
      if img not in train:
         validate.append(img)

   # Generate train.txt
   with open('train.txt', "w+") as f:
      for file in train:
         file = file + "png"
         f.write(DRIVE_PATH + "Data/images/" + file + "\n")
   f.close()

   # Generate validate.txt
   with open('validate.txt', "w+") as f:
      for file in validate:
         file = file + "png"
         f.write(DRIVE_PATH + "Data/images/" + file + "\n")
   f.close()

   # Generate train.shapes
   with open('train.shapes', "w+") as f:
      for train_file in train:
        img_width, img_height = train_file.split("_")[1], train_file.split("_")[2]
        f.write(img_width + " " + img_height + "\n")
   f.close()

   # Generate validate.shapes
   with open('validate.shapes', "w+") as f:
      for validate_file in validate:
        img_width, img_height = validate_file.split("_")[1], validate_file.split("_")[2]
        f.write(img_width + " " + img_height + "\n")
   f.close()


# Main Function
if __name__ == '__main__':
  print("THIS VERSION FOR YOLOV3 IS DEPRICATED. YOU NEED TO UPDATE IT TO HANDLE MULTIPLE LABELS IN A JSON FILE, AMONG OTHER THINGS")
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
