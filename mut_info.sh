#!/bin/sh
#SBATCH -J mut_info
#SBATCH --time=04-00:00:00
#SBATCH -p batch
#SBATCH -N 1 #nodes
#SBATCH -n 2 #tasks (can stand in for cores)
#SBATCH --mem=8gb #Memory requested
#SBATCH --output=create_bigtiff.%j.%N.out
#SBATCH --error=create_bigtiff.%j.%N.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=randall.ellis@tufts.edu

module load anaconda/2021.11
source activate suite2p
python mut_info.py $1