#!/bin/bash
#SBATCH --job-name=to025
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

# here is not the most effitient way to interpolate, but we use it for safety reasons :)
# we use fint library: https://github.com/FESOM/fint/tree/main
# first we have to create example interpolation using linear method. It is slow, 
# but we need to do it only for one time step:

# fint /work/bm1235/a270046/cycle3/tco2559l137/hzfy/hres/intel.levante.openmpi/lvt.intel.sp/Cycle3_012020/temp.fesom.2020.nc \
# /work/ab0995/a270088/meshes/NG5 \
# -t 0 \
# -d -1 \
# --interp mtri_linear \
# --target /scratch/a/a270046/cycle3/extracted/tco2559-ng5/moda/2t.nc \
# -o /work/ab0995/a270088/NextGems/Cycle3/mask/mask_ng5_025.nc

# this "mask" can be used to speed up linear interpolation. This is usually done to make nearest neighbor fast, but
# here we dealing with only 12 timesteps per file, so let's be nice :)

# Define variables
variables=("salt" "temp")

# Define years
years=(2020 2021)

# Base path
base_path="/work/bm1344/AWI/Cycle3/test/monthly_means"

for var in "${variables[@]}"; do
    for year in "${years[@]}"; do
        fint "${base_path}/${var}/${var}_${year}.nc" \
        /work/ab0995/a270088/meshes/NG5 \
        --influence 15000 \
        -t -1 \
        -d -1 \
        --interp mtri_linear \
        --mask /work/ab0995/a270088/NextGems/Cycle3/mask/mask_ng5_025.nc \
        --target /scratch/a/a270046/cycle3/extracted/tco2559-ng5/moda/2t.nc \
        -o "${base_path}/025/${var}/${var}_${year}_025.nc"
    done
done

