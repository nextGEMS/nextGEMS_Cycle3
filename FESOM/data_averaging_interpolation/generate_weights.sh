#!/bin/bash

# example on how to generate interpolation weights for FESOM. 

# For variables on nodes

cdo genycon,/scratch/a/a270046/cycle3/extracted/tco2559-ng5/sst.nc -setgrid,/work/bm1235/a270046/meshes/NG5_griddes_nodes_IFS.nc -selname,cell_area /work/bm1235/a270046/meshesNG5_griddes_nodes_IFS.nc /work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_100_l2d.nc

cdo genycon,/scratch/a/a270046/cycle3/extracted/tco2559-ng5/moda/2t.nc -setgrid,/work/bm1235/a270046/meshes/NG5_griddes_nodes_IFS.nc -selname,cell_area /work/bm1235/a270046/meshes/NG5_griddes_nodes_IFS.nc /work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_025_l2d.nc

# For variables on elements

cdo genycon,/scratch/a/a270046/cycle3/extracted/tco2559-ng5/sst.nc -setgrid,/work/bm1235/a270046/meshes/NG5_griddes_elems_IFS.nc -selname,cell_area /work/bm1235/a270046/meshes/NG5_griddes_elems_IFS.nc /work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_100_l2d_elements.nc

cdo genycon,/scratch/a/a270046/cycle3/extracted/tco2559-ng5/moda/2t.nc -setgrid,/work/bm1235/a270046/meshes/NG5_griddes_elems_IFS.nc -selname,cell_area /work/bm1235/a270046/meshes/NG5_griddes_elems_IFS.nc /work/ab0995/a270088/NextGems/Cycle3/weights/weights_FESOM_tco2559-ng5_original_2d_ycon_ecmwf_025_l2d_elements.nc