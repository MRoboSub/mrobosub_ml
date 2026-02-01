#!/bin/bash
#SBATCH --account=lsa2 # this might need to be changed, run $ my_accounts to see options
#SBATCH --job-name=robosub_ml_training
#SBATCH --partition=gpu
#SBATCH --time=00-06:00:00
#SBATCH --mail-user=muskaan@umich.edu # change to your email before you run this!!
#SBATCH --mail-type=END
#SBATCH --nodes=1
#SBATCH --ntasks=2 # this number used to be 36 (maybe using robosub account) but currently it isn't allowing any higher than 2
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=5000m
#SBATCH --gres=gpu:1
#SBATCH --output=array_%A_%a.out
#SBATCH --error=array_%A_%a.err

echo
echo "________________________START________________________" 
one=1
#LINE=$(sed -n "$SLURM_ARRAY_TASK_ID"p Parameter1.txt)
LINE=$(sed -n "$one"p Parameters.txt)
#job array ver: #MESSAGE="TASK ID: $SLURM_ARRAY_TASK_ID and LINE reads: $LINE"
echo "LINE reads: $LINE"

chmod +x Yolov5s.sh
./Yolov5s.sh $LINE 

echo "________________________END________________________"
