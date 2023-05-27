# Collection of python functions to help with analysis of nextGEMS data
import xarray as xr
import numpy as np
import matplotlib.pylab as plt
import matplotlib.cm as cm
import cmocean.cm as cmo
from scipy.interpolate import (
    CloughTocher2DInterpolator,
    LinearNDInterpolator,
    NearestNDInterpolator,
)
import pyproj
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from scipy.spatial import cKDTree
import numpy as np
from pyproj import CRS, Transformer

g = pyproj.Geod(ellps="WGS84")

def lon_lat_to_cartesian(lon, lat, R=6371000):
    """
    calculates lon, lat coordinates of a point on a sphere with
    radius R. Taken from http://earthpy.org/interpolation_between_grids_with_ckdtree.html
    """
    lon_r = np.radians(lon)
    lat_r = np.radians(lat)

    x = R * np.cos(lat_r) * np.cos(lon_r)
    y = R * np.cos(lat_r) * np.sin(lon_r)
    z = R * np.sin(lat_r)
    return x, y, z

def create_indexes_and_distances(model_lon, model_lat, lons, lats, k=1, workers=2):
    """
    Creates KDTree object and query it for indexes of points in FESOM mesh that are close to the
    points of the target grid. Also return distances of the original points to target points.
    Parameters
    ----------
    mesh : fesom_mesh object
        pyfesom mesh representation
    lons/lats : array
        2d arrays with target grid values.
    k : int
        k-th nearest neighbors to return.
    n_jobs : int, optional
        Number of jobs to schedule for parallel processing. If -1 is given
        all processors are used. Default: 1.
    Returns
    -------
    distances : array of floats
        The distances to the nearest neighbors.
    inds : ndarray of ints
        The locations of the neighbors in data.
    """
    xs, ys, zs = lon_lat_to_cartesian(model_lon, model_lat)
    xt, yt, zt = lon_lat_to_cartesian(lons.flatten(), lats.flatten())

    tree = cKDTree(list(zip(xs, ys, zs)))
    distances, inds = tree.query(list(zip(xt, yt, zt)), k=k, workers=workers)

    return distances, inds

def projected_grid_to_platecarree_pyproj(box, res, projection="World_Mercator", n_points=100):
    """
    Generate a grid of points in the desired projection and then convert the grid points back to 
    PlateCarree (longitude and latitude) space.

    This function creates additional points along the edges of the bounding box specified by the user.
    It then transforms those edge points to the projected coordinate space and calculates the bounding box in
    the projected coordinate space based on the transformed edge points. Finally, it creates a grid in the
    projected coordinate space using the calculated bounding box and converts the grid points back to the
    PlateCarree space.

    Parameters
    ----------
    box : list
        A list representing the bounding box in PlateCarree space, in the format [left,right,down,up].
    res : tuple or None
        A tuple (lonNumber, latNumber) representing the desired grid resolution in the projected
        coordinate space. If None, the default resolution (500, 500) is used.
    projection : str, optional
        The desired projection for the grid, specified as a string with the projection name or the EPSG code. 
        Default is 'World_Mercator'.
    n_points : int, optional
        The number of points to generate along each edge of the bounding box for approximating
        the corners of the projected image. Default is 100.

    Returns
    -------
    x : numpy.ndarray
        A 1D array of x coordinates in the projected coordinate space.
    y : numpy.ndarray
        A 1D array of y coordinates in the projected coordinate space.
    lon : numpy.ndarray
        A 2D array of longitude values in PlateCarree space corresponding to the generated grid points.
    lat : numpy.ndarray
        A 2D array of latitude values in PlateCarree space corresponding to the generated grid points.

    Notes
    -----
    The edge points are created by generating evenly spaced longitude and latitude values within the
    bounding box specified by the user. Four sets of points are created: the top edge, the bottom edge,
    the left edge, and the right edge of the bounding box. These points are then stacked together into a
    single array. Transforming these edge points to the target projection's coordinate space provides an 
    approximation of the edges of the projected image, which can be used to calculate a bounding box in 
    the projected coordinate space.
    """
    if isinstance(projection, str):
        projection_crs = CRS.from_string(projection)
    else:
        projection_crs = CRS.from_epsg(projection)

    # Define CRS for PlateCarree
    platecarree_crs = CRS.from_epsg(4326)

    # Create Transformer objects
    to_projection = Transformer.from_crs(platecarree_crs, projection_crs, always_xy=True)
    to_platecarree = Transformer.from_crs(projection_crs, platecarree_crs, always_xy=True)

    # Parse the bounding box and grid resolution
    left, right, down, up = box
    lonNumber, latNumber = res if res is not None else (500, 500)

    # Generate edge points in PlateCarree space
    lons = np.linspace(left, right, n_points)
    lats = np.linspace(down, up, n_points)
    edge_points_lon, edge_points_lat = np.meshgrid(
        np.hstack((lons, lons, np.repeat(left, n_points), np.repeat(right, n_points))),
        np.hstack((np.repeat(down, n_points), np.repeat(up, n_points), lats, lats)),
    )

    # Transform edge points to the target projection's coordinate space
    edge_points_x, edge_points_y = to_projection.transform(edge_points_lon, edge_points_lat)

    # Calculate the bounding box in the target projection's coordinate space
    xmin, xmax = np.min(edge_points_x), np.max(edge_points_x)
    ymin, ymax = np.min(edge_points_y), np.max(edge_points_y)

    # Create a grid in the target projection's coordinate space
    x = np.linspace(xmin, xmax, lonNumber)
    y = np.linspace(ymin, ymax, latNumber)
    x2d, y2d = np.meshgrid(x, y)

    # Convert the grid points back to PlateCarree space
    lon, lat = to_platecarree.transform(x2d, y2d)

    return x, y, lon, lat

def tunnel_fast1d(latvar, lonvar, lonlat):
    """
    Find closest point in a set of (lat,lon) points to specified pointd.

    Parameters:
    -----------
        latvar : ndarray
            1d array with lats
        lonvar : ndarray
            1d array with lons
        lonlat : ndarray
            2d array with the shape of [2, number_of_point],
            that contain coordinates of the points

    Returns:
    --------
        node : int
            node number of the closest point

    Taken from here http://www.unidata.ucar.edu/blogs/developer/en/entry/accessing_netcdf_data_by_coordinates
    and modifyed for 1d
    """

    rad_factor = np.pi / 180.0  # for trignometry, need angles in radians
    # Read latitude and longitude from file into numpy arrays
    latvals = latvar[:] * rad_factor
    lonvals = lonvar[:] * rad_factor

    # Compute numpy arrays for all values, no loops
    clat, clon = np.cos(latvals), np.cos(lonvals)
    slat, slon = np.sin(latvals), np.sin(lonvals)

    clat_clon = clat * clon
    clat_slon = clat * slon

    lat0_rad = lonlat[1, :] * rad_factor
    lon0_rad = lonlat[0, :] * rad_factor

    delX_pre = np.cos(lat0_rad) * np.cos(lon0_rad)
    delY_pre = np.cos(lat0_rad) * np.sin(lon0_rad)
    delZ_pre = np.sin(lat0_rad)

    nodes = np.zeros((lonlat.shape[1]))
    for i in range(lonlat.shape[1]):
        delX = delX_pre[i] - clat_clon
        delY = delY_pre[i] - clat_slon
        delZ = delZ_pre[i] - slat
        dist_sq = delX**2 + delY**2 + delZ**2
        minindex_1d = dist_sq.argmin()  # 1D index of minimum element
        node = np.unravel_index(minindex_1d, latvals.shape)
        nodes[i] = node[0]

    return nodes


def transect_get_lonlat(lon_start, lat_start, lon_end, lat_end, npoints=30):
    lonlat = g.npts(lon_start, lat_start, lon_end, lat_end, npoints)
    lonlat = np.array(lonlat)
    return lonlat.T


def transect_get_nodes(lonlat, lons, lats):
    nodes = tunnel_fast1d(lats, lons, lonlat)
    return nodes.astype("int")


def transect_get_distance(lonlat):
    (az12, az21, dist) = g.inv(
        lonlat[0, :][0:-1], lonlat[1, :][0:-1], lonlat[0, :][1:], lonlat[1, :][1:]
    )
    dist = dist.cumsum() / 1000
    dist = np.insert(dist, 0, 0)
    return dist
