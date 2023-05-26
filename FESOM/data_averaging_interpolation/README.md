Interpolation and averaging scripts for FESOM
---------------------------------------------

- `interpolate_2d.py` - interpolates 2D FESOM data to 1/4 degree (`025`) or 1 degree (`100`) resolutions with [smmregrid](https://github.com/jhardenberg/smmregrid/tree/main) package. It uses sparce matrix mutliplication method with weights precomputed by `cdo`. Curerntly for FESOM NG5 mesh (used in `IFS_4.4-FESOM_5-cycle3` experiment) we have weight for conservative remapping on 1/4 and 1 degree grids:

```
/work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_025_l2d.nc
/work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_100_l2d.nc
```

- `interpolate_2d_to_025.ipynb` - is just the same as the script before, but in the form of notebook, this is where the script was actually developed in :)

- `interpolate_2D_daily_to_100.sh` - example of batch job script, that calls `interpolate_2d.py` with different parameters.

- `monthly_netcdf2_025.sh` - scritp that uses [fint](https://github.com/FESOM/fint) to do 3D interpolation from precomputed monthly means of FESOM `temp` and `salt` to regular 1/4 degree grid. TODO is to do interpolation with `smmregrid`, but for now it's just linear interpolation based on scipy.
