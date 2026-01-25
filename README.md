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

### STEP 1: Acquire Labelled Data
* Record videos, Parse into images, and get team members to label the images on Labelbox
* Presumably you would use VideoToImages.py (and PreprocessImages.py??) here

### STEP 2: Get Test/Train split and parse bounding boxes for each image
1. Download data from Labelbox (as a .ndjson).
    1. Go to "Annotate" tab on left -> [Project Name] -> Data Rows -> Select All (using checkbox) -> [num] selected -> Export Data -> Select All -> Export JSON
    2. Go to "Notifications" tab on left and download the export you just set up
2. Edit the API_KEY, PROJECT_ID, and CLASSES in LabelAndPartition.py and run (on either local computer or HPC)
```
python3 LabelAndPartition.py [filename].ndjson
```
3. Push resulting test and train directories under 20XXDataset folder to git using large file storage

### STEP 3: Training the Model
1. Use the README.md within the slurm-scripts folder :)




SLURM 101

to submit a job:
```sbatch [jobname].sh```

to view status of a job:
```scontrol show job [jobid]```

to cancel a running job:
```scancel [jobid]```

to view the accounts you have access to and what CPU/GPU capabilities they have:
```my_accounts```
