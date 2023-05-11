import xarray as xr
import numpy as np
import glob
import intake
import dask
import argparse
from dask.distributed import Client
from numcodecs import Blosc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert NetCDF to Zarr')
    parser.add_argument('--run', default='3d_vertices_nz1-upper_3hourly', help='The run to use')
    parser.add_argument('--variable', default='temp_upper', help='The variable to select')
    parser.add_argument('--year', default='2021', help='The year to select')
    parser.add_argument('--output', default='/work/bm1344/AWI/Cycle3/test/temp_upper_2021.zarr', help='The output path')
    parser.add_argument('--workers', default='./', help='The path to directory for dask workers cache')

    args = parser.parse_args()

    cat = intake.open_catalog("../../catalog.yaml")
    run = cat.FESOM['tco2559-ng5-cycle3'][args.run].to_dask()

    dask.config.set({'temporary_directory': args.workers})
    compressor = Blosc(cname="zstd", clevel=3)
    client = Client(n_workers=5, threads_per_worker=1, memory_limit='50GB')

    # Get the variable
    toconvert = run[args.variable].sel(time=args.year)

    # Infer spatial dimension name
    spatial_coord = 'nod2' if 'nod2' in toconvert.dims else 'elem'
    
    # Infer vertical coordinate name
    vertical_coords = [coord for coord in ['nz1_upper', 'nz_upper', 'nz', 'nz1'] if coord in toconvert.coords]
    vertical_coord = vertical_coords[0] if vertical_coords else None

    if vertical_coord is not None:
        chunk_dims = {'time': 12, spatial_coord: 1000000, vertical_coord: 5}
    else:
        chunk_dims = {'time': 12, spatial_coord: 1000000}

    toconvert = toconvert.chunk(chunk_dims)
    toconvert.to_dataset().to_zarr(args.output, encoding={args.variable: {"compressor": compressor}})
    client.close()
    
