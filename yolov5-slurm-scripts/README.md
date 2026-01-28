# yolov5-slurm-scripts Guide
Scripts to be run on a HPC cluster to train a model using Yolov5, organize Yolov5 output, and assist in sorting and transferring test data, training data, and the yolov5 program to a HPC cluster.<br><br>
**By Andrew Huston, James Leung** <br>
hustona@umich.edu  
jameleu@umich.edu <br><br>
**Edited Jan 2026 by Muskaan Mittal** <br>
muskaan@umich.edu <br>

#### Table of Contents
  * [How to Train a Model](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#how-to-train-a-model)
    * [SSH into Great Lakes Cluster](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#ssh-into-great-lakes-cluster)
    * [Clone yolov5-slurm-scripts Repository into Cluster](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#clone-yolov5-slurm-scripts-repository-into-cluster)
    * [Steps to Train](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#steps-to-train-model) 
  * [Updating HPC Cluster Scripts](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#updating-hpc-cluster-scripts)
  * [Modifying Training Settings](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#modifying-training-settings)
  * [Output of Model Training](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#output-of-model-training)
  * [Additional Information about these Scripts](https://gitlab.eecs.umich.edu/mrobosub/yolov5-slurm-scripts#additional-information-about-these-scripts)
  
  <br>

# How to Train a Model

## SSH into Great Lakes Cluster
```
$ ssh UNIQUENAME@greatlakes.arc-ts.umich.edu
```
Subsequently, log in with a University of Michigan account with Great Lakes Cluster access, and complete the 2-factor Authentication when prompted.

NOTE: If not on campus wifi, you will have to join the UM-VPN https://its.umich.edu/enterprise/wifi-networks/vpn 

<br>

## Clone ```mrobosub_ml``` Repository into Cluster
Run this in the directory that you want to clone ```mrobosub_ml``` in:
``` 
$  git clone https://github.com/MRoboSub/mrobosub_ml.git
$  cd mrobosub_ml
```


## Steps to Train Model
  #### 1. Load in the correct python version to be used while training:
  ``` 
  $  module load python/3.9.12
  ```

  #### 2. Allow the setup script to be executable:
  ``` 
  $  chmod +x setup.sh
  ```

  #### 3. Run the setup script. This will ensure the cluster has the yolov5 repo, the dataset for training, and the necessary virtual environment:
  ``` 
  $  ./setup.sh
  ``` 
  
  #### 4. Make sure the dataset you want to use is in the outermost level of the mrobosub_ml repo, called mrobosub_dataset_20xx (and contains train/images, train/labels, test/images, and test/labels)

  #### 5. Optional (See "Modifying Training Settings" Section Below): Make any desired options to training parameters.

  <br>

  #### 6. Change email in job_submission.sh to your email

  #### 7. Run ```sbatch.sh``` to submit the training job.
  ``` 
  $  ./sbatch.sh &
  ``` 

<br>


# Updating HPC Cluster Scripts
Edit Jan 2026: These steps may not work exactly anymore as the yolov5-slurm-scripts no longer has its own git repo but rather is part of mrobosub_ml git repo

Sometimes, the HPC Cluster git repository may need to be updated. In that case, please update the local version. To check if there are updates, go to the cloned ```yolov5-slurm-scripts``` directory and run:
```
$  git remote update
$  git status
```

Then, if the HPC Cluster scripts local version is not up to date with the master branch of the HPC cluster scripts repository, to update, run:
```
$  ./force_update.sh
```
This git resets, git pulls, then adds ```rwx``` access to the user. When this runs, the gitlab username and password of an account in the MRobosub Gitlab needs to be given.

<br>

# Modifying Training Settings

## Adjusting Parameters Through ```Parameters.txt``` for Training, Inferencing, and Weight Conversion
A default set of parameters are given through the git repository version of ```Parameters.txt```. 

The following options can be used to adjust parameters for the following; otherwise, defaults are applied:

### Training
  * ```-i``` - image size for training. **Default:** ```640```
  * ```-b``` - batch size. **Default**: ```64```
  * ```-e``` - number of epochs. **Default**: ```256```
  * ```-d``` - path of ```.yaml``` file relative to ```yolov5-slurm-scripts/yolov5```. **Default:** ```../model.yaml```
  * ```-w``` - weights file. **Default**: ```yolov5s.pt``` (this default works, as long as have the Yolov5 program cloned locally)
  * ```-c``` - use cache when training. **Default**: no cache 
   
### Inferencing
  * ```-s``` - test data directory path relative to ```yolov5-slurm-scripts/yolov5```. **Default:** ```../mrobosub_dataset_2023/test/images/```
  * ```-l``` - image size for inferencing. **Default**: ```672```
  * ```-f``` - confidence threshold for inferencing. **Default**: ```0.08```

### Shared Parameters
  * ```-o``` - **Used for both inferencing and converting weights**: the path of the trained weights file (this file is created when the model is trained). This path is relative to ```yolov5-slurm-scripts/yolov5```. **Default**: ```./runs/train/exp$NUMBER/weights/best.pt```, where ```$NUMBER``` is the number of times a model has been, before the current training, previously trained with Yolov5 since Yolov5 was cloned onto the HPC cluster. This means ```$NUMBER``` starts from 0 and increases by one with each new model training. 

### How ```Parameters.txt``` is Used by ```job_submission.sh``` and its Implications For Using Job Arrays
```job_submission.sh``` reads the first line of ```Parameters.txt```. If job arrays are used, each line in ```Parameters.txt``` represents the different model parameters for each individual model training job (called a task in this case) in the job array.

To use job arrays, the most basic way of creating one is using ```#SBATCH --array=<TOTAL_NUMBER_OF_JOBS>``` in a new line under any of the other parameters in ```job_submission.sh```, AND in ```Parameters.txt```, adding as many lines of different model parameters as the number of tasks in the job array (size of the job array).

See more about creating and using job arrays in the **Job Arrays** section and through the job array term in the **Definitions** section of this [guide](https://docs.google.com/document/d/1hUtCJcm9Sge2El9cNhVsJEPxg40ibhXmS-RamFfvTfY/edit?usp=sharing).

<br>

## Adjusting model.yaml for different datasets
model.yaml is a file that yolov5 uses to know the location of images and labels to train and test on. It also lets the training process know the number and names of classes that the model should detect. 

* ```path: ``` specifies a filepath prefix to apply to the following image locations relative to yolov5/. Default is ../../mrobosub_datasets_2025.
* ```train: ``` specifies the location of the folder with training data images. Default is train/images.
* ```val: ``` specifies the location of the folder with validation images. Default is same as train.
* ```test: ``` specifies the location of the folder with test set images. Default is test/images.
* ```nc: ``` specifies the number of classes the model will detect
* ```names: ``` specifies the names of these classes, with the same indexes as the labels reference them with.

<br>

## Modifying Job CPU/GPU Allocation Through ```job_submission.sh``` Using SLURM Framework
More about SLURM workload manager framework that is used on the Great Lakes Cluster: [Official Slurm Documentation](https://slurm.schedmd.com/overview.html).

**NOTE:** These are the defaults according to ```job_submission.sh```, not SLURM. SLURM has its own defaults for all parameters not specified, such as for all the parameters not specified in ```job_submission.sh```.
  * ```--job-name``` - the SLURM job's name. **Default**: ```robosub_ml_training```
  * ```--partition``` - which set of nodes (partition) to submit the job to. There is also standard (no gpu) and debug (for debugging). Gpu partition allows for gpu. **Default**: ```gpu```
  * ```--time``` - maximum time allowed for submitted job in *DAYS-HOURS:MINUTES:SECONDS*. **Default**: ```00-06:00:00```
  * ```--mail-user``` - the email to which notifications are sent about the submitted job. **Default**: ```jameleu@umich.edu```
  * ```--mail-type``` - the type of email notification requested for the submitted job. **Default**: ```END```
    * *BEGIN*, *NONE*, *FAIL*, *REQUEUE*, and *ARRAY_TASKS* are the other options, and they mean that an email will be sent to give information on how the job does that action described by the option (if it does or does not do that action, etc. Also, using *ARRAY_TASKS* should mean emails will be sent about each individual job (called a task) in a job array).
  * ```--nodes``` - the number of nodes (computers) to allocate. The Robosub account can only have 1. **Default**: ```1```
  * ```--ntasks``` - the number of tasks assigned to each node (the limit seems to be one task per thread of a node's core (there seems to be one thread per core, so this is effectively one task per core of a node)). 36 seems to be the limit, given not too much memory per CPU is used. **Default**: ```36```
  * ```--cpus-per-task``` - the number of CPUs per task. 1 seems to be the limit, and there seems to be overlap with ntasks with this parameter. **Default**: ```1```
  * ```--mem-per-cpu``` - memory per cpu. 12000m seems to be the limit, given there are not too many ntasks. **Default**: ```5000m```
  * ```--gres``` - can be used to set the number of GPUs used. The Robosub account can only have 1. **Default**: ```gpu:1```
  * ```--output``` - the name for the output file of the job. **Default**: ```array_%A_%a.out```
    * **NOTE:** ```%A``` is the master job ID (job array ID), and ```%a``` is the array task ID (ID of individual job, also called task, within job array).
  * ```--error``` - the name for the error file of the job. **Default**: ```array_%A_%a.err```

### Suggested GPU and CPU allocations for Best Performance
The suggested number of tasks and memory per cpu for best performance are one of the following configurations:
  1. ```ntasks=36``` and ```mem-per-cpu=5000m```. This is slightly faster than configuration 2: 256 epochs completed in **1.609 hours** for a model with 213 layers, 7023610 parameters, 0 gradients, 15.8 GFLOPs.
  
  2. ```ntasks=15``` and ```mem-per-cpu=12000m```. This is slightly slower than configuration 1: 256 epochs completed in **1.610 hours** for a model with 213 layers, 7023610 parameters, 0 gradients, 15.8 GFLOPs.

Also, to see the node specifications in the HPC cluster, use the command ```scontrol show nodes``` on the HPC cluster terminal.

For more information on possible allocations, see the **GPU Partition -> Available allocations based on observations:** section in this [guide](https://docs.google.com/document/d/1hUtCJcm9Sge2El9cNhVsJEPxg40ibhXmS-RamFfvTfY/edit?usp=sharing). For more information on viewing HPC cluster node specification-related information (such as queues (basically a wait list) and available nodes), see **Queue**, **Node info and availability**, and **Tip** sections in that [guide](https://docs.google.com/document/d/1hUtCJcm9Sge2El9cNhVsJEPxg40ibhXmS-RamFfvTfY/edit?usp=sharing). Before using allocations, it may also be helpful to review the [student teams limits](https://arc.umich.edu/greatlakes/studentteams/) on the Great Lakes Cluster or whichever cluster the model is being trained on.

<br>

# Output of Model Training

## Obtaining Model's ONNX File and Other Results From Cluster

### ONNX File and Training Files Locations
The path of the ONNX file (converted trained weights), for a model is ```yolov5-slurm-scripts/yolov5/runs/train/exp$NUMBER/weights/best.onnx```, where ```$NUMBER``` is the number of times a model has been, before the current training, previously trained with Yolov5 since Yolov5 was cloned onto the HPC cluster (the highest number is the most recent ```exp``` directory). Many other artifacts from the training session can also be found in ```yolov5-slurm-scripts/yolov5/runs/train/exp$NUMBER/```.

### Test Set Model Evaluation Results Location
Similarly, the results of the newly trained model on the test set can be found in ```yolov5-slurm-scripts/yolov5/runs/val/exp$NUMBER```, where ```$NUMBER``` is the number of times a model has been, before the current training, previously trained with Yolov5 since Yolov5 was cloned onto the HPC cluster (the highest number is the most recent ```exp``` directory).

### Using SCP to transfer ONNX File and Other Results to Local
On your local device, navigate to the directory in which you want to receive the files. Then run the following command to transfer all desired files to the current directory: 
```
$ scp UNIQUENAME@greatlakes.arc-ts.umich.edu:PATH_TO_RESULTS_DIR/* .
```

### Using Globus to transfer ONNX File and Other Results to Local
Using this method, a person can transfer files to and from the cluster quikcly.
  1. Go [here](https://arc.umich.edu/globus/) to create an account. 
  2. Download the [Globus Connect Personal Program](https://www.globus.org/globus-connect-personal) to upload local files. This program will allow the online Globus Collection to access and manage your local files through Globus. A *collection* in Globus is a group of a system's local files that can be changed, transferred to another collection, or added onto from another collection's files.
  3. Run the downloaded program and follow its instructions to create a collection name (```name#<YOURCHOICE>```) and add a description for the collection.
  4. Change the panel view in the top right corner to the middle option (split view between two collections). Go to File Manager on the [Globus Website](https://app.globus.org) and search for your local collection in either the left or right panel, then the ```umich#greatlakes``` collection in the other panel.
  5. Select your files and directories only on the panel of your desired **source** collection, then click *transfer or sync to…* in the middle toolbar between the two panels. If *start* is not clickable above the source panel, then check if there are any files selected in the destination panel. If *start* is clickable, then click *start* and ensure the arrow points in the direction of the file transfer you desire (source to destination).
  6. There are also other options in the middle between the two panels that one can do after selecting files: *sharing* (with Globus accounts), *new folder*, *rename*, *delete*, *download*, *open*, *upload*, *get link*, *show hidden files*, and *manage activation* (creates and authorizes an endpoint, which is not needed for converting the ONNX file and results).

### Other Methods of file transfer
See [MRobosub Slurm Documentation](https://docs.google.com/document/d/1hUtCJcm9Sge2El9cNhVsJEPxg40ibhXmS-RamFfvTfY/edit?usp=sharing) under "File Transfer To HPC Cluster" Section.

## Checking Installed Dependencies in Virtual Environment Through ```installed.txt```
When the machine learning model is trained by running ```sbatch.sh```, the Yolov5 dependencies will automatically be installed in the virtual environment manually created for Yolov5 and the HPC Cluster Scripts. After training the model by running ```sbatch.sh```, these dependencies can be viewed in ```installed.txt```. The libraries and packages that should be installed for Yolov5 and the HPC Cluster Scripts are in the git repository version of ```installed.txt```.

<br>

## The Output Logging System and Resetting the Output Logging System Through ```sbatch.sh```

The file logging system for the output is taken care of through ```sbatch.sh```.

**NOTE:** If ```sbatch.sh```, when running, is interrupted, or multiple instances of ```sbatch.sh``` are being run at once, the logging system will not work, and the output and error files for that training will be in ```yolov5-slurm-scripts```. This logging system works with job arrays. Additionally, when using job arrays, the output and error files will be separate and different for each task in the job array (based on the task ID).

Logging System Organizational structure:
  * ```log_file``` - This is a directory is in ```yolov5-slurm-scripts``` and contains ```log_set``` directories. Created only on the first run of ```sbatch.sh``` or when the ```-r``` option is used when running ```sbatch.sh```. On the first run, ```log_files_1``` is created in ```yolov5-slurm-scripts```. In all other cases besides the first run or using the ```-r``` option, the most recent ```log_file``` is the storage location of the most recent ```log_set``` directory that has the output and error files of the model just trained. 
  * ```log_set``` - Each time a model is trained by running ```sbatch.sh```, a new ```log_set_$NUMBER``` is created, where ```$NUMBER``` is one plus the number of ```log_set``` directories in the most recent ```log_file``` directory. This means ```$NUMBER``` starts from 1 and increases by one with each new model training. The output (```.out```) and error files (```.err```) for that specific training of the model are found in this ```log_set``` directory. 

**Options:**

  * ```-r``` - create a new ```log_file_$NUMBER``` directory, where ```$NUMBER``` is one plus the number of ```log_file``` directories in ```yolov5-slurm-scripts```. Any future output or error files from model training will be stored in a new ```log_set``` directory in this new ```log_file``` directory, and the first ```log_set``` number in this ```log_file``` directory will start from 1.

<br>

## Where to Find Command Line Output for Running the HPC Clusters
In the most recent ```log_files``` that is in the most recent ```log_set```, there should be two files:
  * ```.err``` file - This contains the output obtained from Yolov5 during training, inferencing, and weights conversion. This also contains any error or warning outputs. 
  * ```.out``` file - This contains ```Parameters.txt``` arguments passed, along with the forms of these arguments when passed into ```train.py``` for training. Additionally, this file has various other messages, such as which steps of the HPC Cluster scripts' processes were reached, like training. The trained weights location and dependencies installed are also listed here.

<br>


# Additional Information about these Scripts

## Training Scripts (Inferencing and Weight Conversion Occur, Here, Too) 

To train, run, in cd ```yolov5-slurm-scripts```:
```
$  ./sbatch.sh &
```
Because the SLURM workload manager on the Great Lakes Cluster might not immediately run a job right away due to that job being behind other higher priority jobs in queue, ```sbatch.sh``` runs until it reaches its last step and sleeps until the output is received and output files are created for that machine learning model training. After such files are created, ```sbatch.sh``` takes its last step and moves these files into the proper logging files directory. Therefore, ```./sbatch.sh``` should be run in the background (using ```&```) so that the cluster terminal can still be used afterwards.

There are no arguments or options for ```sbatch.sh```. All of the training parameters are read from ```Parameters.txt```.

Running ```sbatch.sh``` runs ```job_submission.sh```, ```Yolov5s.sh```, and ```Yolov5s_setup.py```.

### About ```job_submission.sh```
```job_submission.sh``` is called by ```sbatch.sh``` using the ```sbatch``` SLURM keyword, and SLURM reads the allocations written with SLURM syntax in ```job_submission.sh```. After, the parameters for model training, inferencing, and weight conversion are read from ```Parameters.txt``` and passed into ```Yolov5s.sh```, which is run and submitted as a SLURM job.

### About ```Yolov5s.sh```
This file enters the virtual environment created for the HPC Cluster scripts and Yolov5 and installs all Yolov5 dependencies. Using the arguments passed from ```job_submission.sh```, ```Yolov5s.sh``` uses the Yolov5 program to train the model using ```train.py```, run inferencing using ```detect.py```, and convert the weights to ONNX and other files through ```export.py```. ```train.py```, ```detect.py```, and ```export.py``` are all files from the cloned Yolov5 repository. 

If inferencing and converting does not work using the HPC Cluster scripts, it can be done locally with a cloned Yolov5 program. The weights file created from training the model can be found in ```yolov5-slurm-scripts/yolov5/runs/train/exp$NUMBER/weights/best.pt```, where ```$NUMBER``` is the number of times a model has been, before the current training, previously trained with Yolov5 since Yolov5 was cloned onto the HPC cluster (basically a organizational numbering system starting from 0).

For inferencing and converting, MRobosub usually calls the following from the ```yolov5-slurm-scripts/yolov5``` directory:

*Inferencing:*
```
$  python3 detect.py --weights TRAINED_WEIGHTS_PATH --img INFERENCING_IMAGE_SIZE --conf CONFIDENCE --source TEST_DATA_PATH --save-txt --name [optional: TRAINING_WEIGHTS_NAME]
```

*Converting:*

```
$  python3 export.py --weights TRAINED_WEIGHTS_PATH --include onnx --simplify 
```

### About ```Yolov5s_setup.py```

When installing dependencies for Yolov5, ```Yolov5s.sh``` calls this file to include additional dependencies using Python. This file also prints the GPU device (graphics card) being used to train the model.

<br>

## Additional Great Lakes Cluster and SLURM Documentation by MRobosub
The guide that was mentioned several times in this README.md: [Slurm Great Lakes HPC Cluster Simple User Guide](Slurm Great Lakes HPC Cluster Simple User Guide)
