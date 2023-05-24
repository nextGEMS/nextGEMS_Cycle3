import xarray as xr
import numpy as np
import glob
import intake
import dask
import argparse
from dask.distributed import Client
from numcodecs import Blosc
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert NetCDF to Zarr")
    parser.add_argument(
        "--run", default="3d_vertices_nz1-upper_3hourly", help="The run to use"
    )
    parser.add_argument(
        "--variable", default="temp_upper", help="The variable to select"
    )
    parser.add_argument("--year", default="2021", help="The year to select")
    parser.add_argument(
        "--output",
        default="/work/bm1344/AWI/Cycle3/test/temp_upper_2021.zarr",
        help="The output path",
    )
    parser.add_argument(
        "--workers", default="./", help="The path to directory for dask workers cache"
    )
    parser.add_argument("--monthly", action="store_true", help="Save data monthly")

    args = parser.parse_args()

    cat = intake.open_catalog("https://nextgems.github.io/catalog/catalog.yaml")
    run = cat.FESOM["IFS_4.4-FESOM_5-cycle3"][args.run].to_dask()

    dask.config.set({"temporary_directory": args.workers})
    compressor = Blosc(cname="zstd", clevel=3)
    client = Client(n_workers=5, threads_per_worker=1, memory_limit="50GB")
    # Get the variable
    toconvert = run[args.variable]
    # Infer spatial dimension name
    spatial_coord = "nod2" if "nod2" in toconvert.dims else "elem"

    # Infer vertical coordinate name

    vertical_coords = [
        coord
        for coord in ["nz1_upper", "nz_upper", "nz", "nz1"]
        if coord in toconvert.coords
    ]
    vertical_coord = vertical_coords[0] if vertical_coords else None

    if vertical_coord is not None:
        chunk_dims = {"time": 12, spatial_coord: 1000000, vertical_coord: 5}
    else:
        chunk_dims = {"time": 12, spatial_coord: 1000000}

    if args.monthly:
        for month in range(1, 13):
            monthly_output = args.output.replace(
                ".zarr", "_{}.zarr".format(str(month).zfill(2))
            )
            if os.path.exists(monthly_output):
                print(f"Output file {monthly_output} already exists, skipping.")
                continue
            monthly_data = toconvert.sel(
                time="{}-{}".format(args.year, str(month).zfill(2))
            )
            monthly_data = monthly_data.chunk(chunk_dims)

            monthly_data.to_dataset().to_zarr(
                monthly_output, encoding={args.variable: {"compressor": compressor}}
            )
    else:
        toconvert = toconvert.sel(time=args.year)
        toconvert = toconvert.chunk(chunk_dims)
        toconvert.to_dataset().to_zarr(
            args.output, encoding={args.variable: {"compressor": compressor}}
        )

    client.close()
