#!/bin/bash
#SBATCH --job-name=tozarr
#SBATCH -p compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=0
##SBATCH --ntasks=3072
#SBATCH --time=08:00:00
#SBATCH -o slurm-out.out
#SBATCH -e slurm-err.out
#SBATCH -A ab0995

source /sw/etc/profile.levante

python fesom_netcdf2zarr.py --run 3d_vertices_nz1-upper_3hourly --variable salt_upper --year 2020 --output /work/bm1344/AWI/Cycle3/test/salt_upper_2020.zarr --workers /scratch/a/a270088/dask/workers2/

