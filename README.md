This document is in the process of being updated Jan 2026 by Muskaan Mittal.

### STEP 0: Setup python environment
You will have to do this both on local computer and eventually on cluster (or wherever you want to run this stuff).

using uv (https://docs.astral.sh/uv/):
```
uv sync
```

Without:
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install . # if this doesn't work, manually install the dependencies in pyproject.toml as shown below:

pip install aiofiles opencv-python numpy pillow requests tqdm
```

If the pyproject.toml doesn't serve you well, there's also a requirements.txt file that may work, run ```pip install -r requirements.txt```. You might have to change versions of some packages in the requirements.txt if it doesn't work right away.

### STEP 1: Acquire Images and Label Data
* Record videos, Parse into images, and get team members to label the images on Labelbox
* Presumably you would use VideoToImages.py (and PreprocessImages.py??) here

### STEP 2: Pull images and labels from labelbox, create train/test split
Note: This step only needs to be done once for any year's dataset. If it has already been done, you will see a folder in this repo called 20XX_dataset which contains a train folder (containing images and labels) and a test folder (containing images and labels), and a file in mrobosub_ml ending in .ndjson.

1. Download data from Labelbox (as a .ndjson).
    1. Go to "Annotate" tab on left -> [Project Name] -> Data Rows -> Select All (using checkbox) -> [num] selected -> Export Data -> Select All -> Export JSON
    2. Go to "Notifications" tab on left and download the export you just set up
    3. You can just keep the .ndjson within the top-level mrobosub_ml directory for now. In step 4 we'll move it inside our dataset folder.
2. Edit the PROJECT_ID, and CLASSES in LabelAndPartition.py
3. Get API key from LabelBox, and run ```export LABELBOX_API_KEY="your_api_key_value"```
4. If running this step on local computer, run
```
python3 LabelAndPartition.py [filename].ndjson
```
If running on HPC, change the mail-user email ID in label_and_partition.sh to your own and run ```sbatch label_and_partition.sh```
4. Move resulting test and train directories to 20XX_dataset folder and push to git

### STEP 3: Train the Model
Use the README.md within the yolovX-slurm-scripts folder to train the model

### STEP 4: Use Model for Inference
Once model is trained, move over its values into main mrobosub repo (as opposed to mrobosub_ml repo) and use it for inference within the main codebase! (tbd on detailed steps for this).




### SLURM 101

* to submit a job:
```$ sbatch [jobname].sh```

*  to view status of a job:
```$ scontrol show job [jobid]```

* to cancel a running job:
```$ scancel [jobid]```

* to view the accounts you have access to and what CPU/GPU capabilities they have:
```$ my_accounts``` (if you try to run something using sbatch and it says incorrect partition, you can use this command to see what accounts you have access to and change the ```#SBATCH --account=lsa2`` field in the .sh files from lsa2 to whatever account it shows)
