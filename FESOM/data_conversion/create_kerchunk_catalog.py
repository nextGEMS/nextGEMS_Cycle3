import json
import glob

import tqdm
import kerchunk.hdf
import fsspec
import base64

import xarray as xr
from kerchunk.combine import MultiZarrToZarr


import base64
import xarray as xr


def encode_value(v):
    try:
        return v.decode("ascii")
    except UnicodeDecodeError:
        return "base64:" + base64.b64encode(v).decode("ascii")


def fix_time(single):
    t = xr.open_dataset(
        "reference://",
        engine="zarr",
        backend_kwargs={
            "storage_options": {
                "fo": single,
            },
            "consolidated": False,
        },
    )[["time"]].compute()
    t.time.encoding = {}
    m = {}
    t.to_zarr(
        m,
        encoding={
            "time": {
                "units": "seconds since 1990-01-01",
                "dtype": "i4",
                "compressor": None,
            }
        },
    )
    return {
        "version": single["version"],
        # "templates": single["templates"],
        "refs": {
            **single["refs"],
            **{k: encode_value(v) for k, v in m.items() if k.startswith("time/")},
        },
    }


# path_to_output = "/work/mh0287/m300918/Sensitivity_runs_output/FESOM/iage/"
path_to_output = "/work/mh0287/m300918/Sensitivity_runs_output/FESOM/iage_glob/"
# files = "*.nc"

# urls = list(sorted(glob.glob(f"{path_to_output}/{files}")))

urls = []
# for vvar in ["fh", "MLD1", "MLD2", "ssh", "sst", "sss", "tx_sur", "ty_sur"]:
#     var_url = list(sorted(glob.glob(f"{path_to_output}/{vvar}*.nc")))
#     urls.extend(var_url)

# for vvar in [
#     # "Av",
#     # "Kv",
#     # "N2",
#     # "Ri",
#     "salt",
#     # "shear",
#     "temp",
#     # "tke",
#     "tra_1007",
#     "unod",
#     "vnod",
#     # "w",
# ]:
#     var_url = list(sorted(glob.glob(f"{path_to_output}/{vvar}*.nc")))
#     urls.extend(var_url)

for vvar in [
    "Av",
    "Kv",
    "N2",
    "Ri",
    # "salt",
    "shear",
    # "temp",
    "tke",
    # "tra_1007",
    # "unod",
    # "vnod",
    "w",
]:
    var_url = list(sorted(glob.glob(f"{path_to_output}/{vvar}*.nc")))
    urls.extend(var_url)

singles = []
for u in tqdm.tqdm(urls):
    with fsspec.open(u) as inf:
        h5chunks = kerchunk.hdf.SingleHdf5ToZarr(inf, u, inline_threshold=100)
        singles.append(h5chunks.translate())


from kerchunk.combine import MultiZarrToZarr

mzz = MultiZarrToZarr([fix_time(s) for s in singles], concat_dims=["time"])

out = mzz.translate()


ds = xr.open_dataset(
    "reference://",
    engine="zarr",
    backend_kwargs={
        "storage_options": {
            "fo": out,
        },
        "consolidated": False,
    },
)

oname = "FESOM_13_tropo_age_interpolated_05_deg"
with open(
    f"/work/bm1344/AWI/Cycle3/FESOM_13_tropo_age_interpolated/{oname}_3d_interfaces.json",
    "w",
) as outfile:
    json.dump(out, outfile)

# b = xr.open_zarr(
#     f"reference:://work/bm1344/AWI/Cycle3/FESOM_13_tropo_age_interpolated/{oname}.json",
#     consolidated=False,
# )
