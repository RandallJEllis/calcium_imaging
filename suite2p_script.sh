#!/bin/sh
#SBATCH -J suite2p_juanita
#SBATCH --time=00-13:00:00
#SBATCH -p largemem
#SBATCH -N 1 #nodes
#SBATCH -n 8 #tasks (can stand in for cores)
#SBATCH --mem=64g
#SBATCH --output=suite2p.%j.%N.out
#SBATCH --error=suite2p.%j.%N.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=randall.ellis@tufts.edu

module load anaconda/2021.11
source activate suite2p

# Example usage: sbatch job.sh juanita/GCAMP_RF_I3C/ batch
python suite2p_script.py "$@"