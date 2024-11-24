import os
import shutil
import glob
from PIL import Image
from datetime import datetime

"""

This file is used to ensure raw data images have the right format, size, and naming scheme

NOTE:
    - There should be an "images/" folder found in the same directory as this file
    - If trying to use this script multiple times in one day, change the starting index varible to ensure no duplicate names

"""

WIDTH = 672
HEIGHT = 376
DATE = datetime.now().strftime("%m%d%Y")
index = 0

files = glob.glob("images/*")
if len(files) == 0:
    print("No \"images\" folder detected.") 
    print("Please create this folder with the raw data images.")
    exit()

try:
    os.mkdir("tmp_images")
except:
    print("Problem creating temp directory")

for f in files:
    image = Image.open(f)
    image = image.resize((WIDTH, HEIGHT))
    path_out = "images/" + DATE + "_" + str(WIDTH) + "_" + str(HEIGHT) + "_" + str(index) + ".png"
    image.save("tmp_" + path_out)
    print("Processed " + path_out)
    index += 1

shutil.rmtree("images/")
os.rename("tmp_images", "images")
print("\nAdd these numbered images to google drive.")
print("They will be needed with these names after labeling for partitioning.")