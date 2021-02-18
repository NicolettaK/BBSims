#!/bin/bash
#SBATCH --constraint=haswell
#SBATCH --nodes=1
#SBATCH --time=24:00:00

module load python
source activate myenv
python write_obs_maps.py
