#!/bin/sh
#SBATCH -J create_bigtif
#SBATCH --time=00-12:00:00
#SBATCH -p largemem
#SBATCH -N 1 #nodes
#SBATCH -n 1 #tasks (can stand in for cores)
#SBATCH --mem=48g
#SBATCH --output=create_bigtiff.%j.%N.out
#SBATCH --error=create_bigtiff.%j.%N.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=randall.ellis@tufts.edu

module load anaconda/2021.11
source activate suite2p
python create_bigtifs_multiple_folders.py "$@"
