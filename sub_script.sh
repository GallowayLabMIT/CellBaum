#!/bin/bash
#SBATCH -c 48
#SBATCH --output=snakemake-%j.txt

# Loading the required module
source /etc/profile
module load anaconda/2021a
# Activate local conda module
eval "$(conda shell.bash hook)"
conda activate /home/gridsan/groups/galloway/conda_envs/cellbaum
# Run snakemake
snakemake -j48

