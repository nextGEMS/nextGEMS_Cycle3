import smmregrid as rg
import xarray as xr
import numpy as np
import intake
import os
from dask.distributed import Client
import dask


if __name__ == "__main__":
    cat = intake.open_catalog("/home/a/a270088/PYTHON/nextgems/catalog/FESOM/IFS_4.4-FESOM_5-cycle3_zarr.yaml")
    data = cat['3D_daily_native_zarr'].to_dask()

    dask.config.set({'temporary_directory': '/scratch/a/a270088/dask/'})
    # client = Client(n_workers=5, threads_per_worker=1, memory_limit='50GB')
    client = Client(n_workers=20, threads_per_worker=1, memory_limit='10GB')
    
    for year in range(2024, 2025):
        print(year)
        for vari in ['u', 'v', 'w']:
            print(f"variable: {vari}, year: {year}")
            vari_mm = data[vari].sel(time=str(year)).resample(time='1M').mean(dim='time')
            vari_mm.to_netcdf(f'/work/bm1344/AWI/Cycle3/test/monthly_means/{vari}/{vari}_{str(year)}.nc')
        
    
    
