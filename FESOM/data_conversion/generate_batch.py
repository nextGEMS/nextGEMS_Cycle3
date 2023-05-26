import os

# Variables
variables = {
    "3D_daily_native": ["temp", "salt", "u", "v", "w"],
    "3D_3h_native": ["temp_upper", "salt_upper", "u_upper", "v_upper", "w_upper"],
}

# Base path for worker directories
base_path = "/scratch/a/a270088/dask/"

# Years
years = range(2020, 2025)  # Change this as per your requirement

for run, var_list in variables.items():
    for variable in var_list:
        for year in years:
            # Create worker directory for this run
            worker_dir = os.path.join(base_path, f"{variable}_{year}")
            os.makedirs(worker_dir, exist_ok=True)

            with open(f"job_fesom_netcdf2zarr_{variable}_{year}.sh", "w") as file:
                file.write("#!/bin/bash\n")
                file.write(f"#SBATCH --job-name={variable[:5]}{str(year)[2:]}\n")
                file.write("#SBATCH -p compute\n")
                file.write("#SBATCH --nodes=1\n")
                file.write("#SBATCH --ntasks-per-node=128\n")
                file.write("#SBATCH --mem=0\n")
                file.write("#SBATCH --time=08:00:00\n")
                file.write(f"#SBATCH -o slurm-out_{variable}_{year}.out\n")
                file.write(f"#SBATCH -e slurm-err_{variable}_{year}.out\n")
                file.write("#SBATCH -A ab0995\n\n")
                file.write("source /sw/etc/profile.levante\n\n")
                monthly_option = "--monthly" if run == "3D_3h_native" else ""
                file.write(
                    f"python fesom_netcdf2zarr.py --run {run} --variable {variable} --year {year} --output /work/bm1344/AWI/Cycle3/test/{variable}_{year}.zarr --workers {worker_dir} {monthly_option}\n"
                )

print("Batch job scripts have been created!")
