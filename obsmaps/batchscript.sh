#!/bin/bash
#SBATCH -N 1
#SBATCH -C haswell
#SBATCH -q premium
#SBATCH -J writeobs1
#SBATCH --mail-user=mabitbol15@gmail.com
#SBATCH --mail-type=ALL
#SBATCH -t 24:04:00

#OpenMP settings:
export OMP_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread


srun -n 1 -c 64 --cpu_bind=cores write_obs_maps.py
