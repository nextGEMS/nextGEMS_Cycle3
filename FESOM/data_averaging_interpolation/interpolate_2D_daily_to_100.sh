#!/bin/bash
#SBATCH --job-name=tozarr
#SBATCH -p compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=0
##SBATCH --ntasks=3072
#SBATCH --time=08:00:00
#SBATCH -o slurm-out_100_daily.out
#SBATCH -e slurm-err_100_daily.out
#SBATCH -A ab0995

source /sw/etc/profile.levante

python interpolate_2d.py --experiment IFS_4.4-FESOM_5-cycle3 \
                         --what_interpolate 2D_daily_native \
                         --output_folder /work/bm1344/AWI/Cycle3/ \
                         --start_year 2024 \
                         --end_year 2024 \
                         --resolution "100" 

