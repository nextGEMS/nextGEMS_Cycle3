#!/bin/bash
#SBATCH --job-name=zar2mm
#SBATCH -p compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=0
##SBATCH --ntasks=3072
#SBATCH --time=08:00:00
#SBATCH -o slurm-out_zar2mm.out
#SBATCH -e slurm-err_zar2mm.out
#SBATCH -A ab0995

source /sw/etc/profile.levante

python zarr_to_monthly_means.py