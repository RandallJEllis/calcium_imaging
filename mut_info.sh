#!/bin/sh
#SBATCH -J mut_info
#SBATCH --time=1-00:00:00
#SBATCH -p batch
#SBATCH -N 1 #nodes
#SBATCH -n 10 #tasks (can stand in for cores)
#SBATCH --mem=96gb #Memory requested
#SBATCH --output=sh_mut_info.%j.%N.out
#SBATCH --error=sh_mut_info.%j.%N.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=randall.ellis@tufts.edu

module load anaconda/2021.11
source activate suite2p
python mut_info.py "$@"
