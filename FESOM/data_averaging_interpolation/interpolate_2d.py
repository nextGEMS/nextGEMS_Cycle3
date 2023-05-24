import smmregrid as rg
import xarray as xr
import numpy as np
import intake
import os
from dask.distributed import Client
import dask
import argparse

def ensure_directory_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Directory {dir_path} created ")
    else:    
        print(f"Directory {dir_path} already exists")
def check_file_exists(filepath):
    return os.path.isfile(filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--experiment', type=str, required=True, help='Experiment name')
    parser.add_argument('--what_interpolate', type=str, required=True, help='Interpolation type')
    parser.add_argument('--output_folder', type=str, required=True, help='Output folder path')
    parser.add_argument('--start_year', type=int, required=True, help='Start year')
    parser.add_argument('--end_year', type=int, required=True, help='End year')
    parser.add_argument('--resolution', type=str, required=True, help='Resolution')

    args = parser.parse_args()

    cat = intake.open_catalog("https://nextgems.github.io/catalog/catalog.yaml")

    data = cat.FESOM[args.experiment][args.what_interpolate].to_dask()

    client = Client(n_workers=20, threads_per_worker=1, memory_limit='10GB')
    regridder = rg.Regridder(weights=f"/work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_{args.resolution}_l2d.nc")

    for var_name, da in data.data_vars.items():
        opath = os.path.join(args.output_folder, "FESOM", args.experiment, args.resolution, args.what_interpolate, var_name)
        ensure_directory_exists(opath)
        if var_name in ['tx_sur', 'ty_sur']:
            regridder = rg.Regridder(weights=f"/work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_{args.resolution}_l2d_elements.nc")
        for year in range(args.start_year, args.end_year+1):
            for mon in range(1, 13):
                print(f"{var_name}, {year}, {mon}")
                ofile = os.path.join(opath, f"{var_name}_{str(year)}-{str(mon).zfill(2)}.nc")
                if not check_file_exists(ofile):
                    monthly_interp = regridder.regrid(da.sel(time=f'{str(year)}-{str(mon).zfill(2)}'))
                    monthly_interp = monthly_interp.to_dataset()
                    monthly_interp.attrs = {'model': "FESOM2",
                                            'experiment':args.experiment,
                                            'var_type': args.what_interpolate, 
                                            "target_resolution": args.resolution}
                    monthly_interp.to_netcdf(ofile, encoding={var_name: {"zlib": True, "complevel": 1, "dtype": np.dtype("single")}},)
                else:
                    print(f"File {ofile} exist, skipping")
                    continue 

    client.close()