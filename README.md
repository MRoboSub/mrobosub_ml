### STEP 0: Setup python environment:

using uv (https://docs.astral.sh/uv/):
```
uv sync
```

Without:
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install [dependencies that are in the pyproject.toml]
```
You may also need to ```pip install opencv-python numpy pillow requests``` as some of these aren't currently in the pyproject.toml

If the pyproject.toml doesn't serve you well, there's also a requirements.txt file that may work well to pip install stuff. You might have to change versions of some packages if it doesn't work right away on your system.

### STEP 1: Acquire Labelled Data
* Record videos, Parse into images, and get team members to label the images on Labelbox
* Presumably you would use VideoToImages.py (and PreprocessImages.py??) here

### STEP 2: Get Test/Train split and parse bounding boxes for each image
Note: This step only needs to be done once for any year's dataset. If it has already been done, you will see a folder in this repo called 20XX_dataest which contains a train folder (containing images and labels), a test folder (containing images and labels), and a file ending in .ndjson

1. Download data from Labelbox (as a .ndjson).
    1. Go to "Annotate" tab on left -> [Project Name] -> Data Rows -> Select All (using checkbox) -> [num] selected -> Export Data -> Select All -> Export JSON
    2. Go to "Notifications" tab on left and download the export you just set up
    3. You can just keep the .ndjson within the top-level mrobosub_ml directory for now. In step 4 we'll move it inside our dataset folder.
2. Edit the  PROJECT_ID, and CLASSES in LabelAndPartition.py, and set environment variable LABELBOX_API_KEY="your key"
3. Run (on either local computer or HPC)
```
python3 LabelAndPartition.py [filename].ndjson
```
If running on HPC, can use ```sbatch label_and_partition.sh```
4. Move resulting test and train directories (and the .ndjson file) to 20XX_dataset folder and push to git

### STEP 3: Training the Model
1. Use the README.md within the slurm-scripts folder :)




### SLURM 101

to submit a job:
```sbatch [jobname].sh```

to view status of a job:
```scontrol show job [jobid]```

to cancel a running job:
```scancel [jobid]```

to view the accounts you have access to and what CPU/GPU capabilities they have:
```my_accounts```
