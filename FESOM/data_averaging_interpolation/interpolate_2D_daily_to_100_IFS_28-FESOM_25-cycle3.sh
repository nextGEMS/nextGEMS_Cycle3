#!/bin/bash
#SBATCH --job-name=orca_100
#SBATCH -p compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=0
##SBATCH --ntasks=3072
#SBATCH --time=08:00:00
#SBATCH -o slurm-out_100_orca.out
#SBATCH -e slurm-err_100_orca.out
#SBATCH -A ab0995

source /sw/etc/profile.levante

python interpolate_2d.py --experiment IFS_28-FESOM_25-cycle3 \
                         --what_interpolate 2D_daily_native \
                         --output_folder /work/bm1344/AWI/Cycle3/ \
                         --start_year 2020 \
                         --end_year 2024 \
                         --resolution "100" \
                         --node_weights /work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_IFS_28-FESOM_25_original_2d_ycon_ecmwf_100_l2d.nc \
                         --elem_weights /work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_IFS_28-FESOM_25_original_2d_ycon_ecmwf_100_l2d_elements.nc
