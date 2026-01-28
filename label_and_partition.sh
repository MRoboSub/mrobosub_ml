#!/bin/bash

# NOTE: to run LabelAndPartition as an sbatch job, run $ sbatch label_and_partition.sh

#SBATCH --job-name=label_and_partition
#SBATCH --account=lsa2 # this might need to be changed, run $ my_accounts to see options
#SBATCH --partition=gpu
#SBATCH --time=00-06:00:00
#SBATCH --mail-user=muskaan@umich.edu # use your own email here please!!
#SBATCH --mail-type=END
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=5000m
#SBATCH --gres=gpu:1
#SBATCH --output=array_%A_%a.out
#SBATCH --error=array_%A_%a.err

echo "________________________START________________________"

python3 LabelAndPartition.py 2025v1_data.ndjson            # use appropriate year's .ndjson file here

echo "________________________END________________________"
