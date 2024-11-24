import os
import sys
import json
import glob
import random
import shutil

classes = ["abydos", "earth", "taurus", "serpens_caput", "auriga", "cetus"]

def generateFiles(json_file_name):
    LABEL_PATH = "temp"
    IMG_PATH = "temp"

    files = glob.glob("images/*")
    if len(files) == 0:
        print("No \"images\" folder detected.") 
        print("\"images\" folder should have preprocessed images.")
        exit()

    # Create Data/images and Data/labels
    try:
        os.mkdir("TRAIN")
        os.mkdir("TRAIN/images")
        os.mkdir("TRAIN/labels")
        os.mkdir("TEST")
        os.mkdir("TEST/images")
        os.mkdir("TEST/labels")
    except:
        print("Error generating the TRAIN/TEST directories - did they already exist?")
        exit()

    # Parse JSON file from LabelBox
    # - Creates label text files (e.g. 02-14-2021_1.png)
    with open(json_file_name) as f1:

        for line in f1:
            z = json.loads(line)
            file = z["data_row"]["external_id"]
            file = file.split(".")[0]
            img_width, img_height = float(file.split("_")[1]), float(file.split("_")[2])

            objects = z["projects"][list(z["projects"].keys())[0]]["labels"][0]["annotations"]["objects"]
            if objects: # if there is a label for this image

                if random.random() < .1: #choose test or train
                    LABEL_PATH = "TEST/labels/{}.txt".format(file)
                    IMG_PATH = "TEST/images/{}.png".format(file)
                else:
                    LABEL_PATH = "TRAIN/labels/{}.txt".format(file)
                    IMG_PATH = "TRAIN/images/{}.png".format(file)

                with open(LABEL_PATH, "w+") as f2:
                    for cnt, label in enumerate(objects): # loop through labels in this image and write to label file
                        x_center = (label["bounding_box"]["left"] + (label["bounding_box"]["width"] / 2.0)) / img_width
                        y_center = (label["bounding_box"]["top"] + (label["bounding_box"]["height"] / 2.0)) / img_height
                        width = label["bounding_box"]["width"] / img_width
                        height = label["bounding_box"]["height"] / img_height
                        class_name = classes.index(label["name"])
                        f2.write("{} {} {} {} {}".format(class_name, x_center, y_center, width, height))
                        if cnt < len(objects) - 1:
                            f2.write("\n")
                try:
                    shutil.move("images/{}.png".format(file), IMG_PATH)
                except:
                    print("Could not move image images/{}.png.")
                    

# Main Function
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("[ERROR] usage: python3 generateTrainingFiles.py [JSONFILE]")
        exit()
    generateFiles(str(sys.argv[1]))