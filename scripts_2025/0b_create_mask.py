import os
import xarray as xr
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

## Step 1: Set directories and filenames
base_dir = "/mnt/projects/Noongar_seasons/"

input_dir = os.path.join(base_dir, "outputs")
output_dir = os.path.join(base_dir, "outputs")
shapefile_dir = os.path.join(base_dir, "boundaries")

# Define filenames
shape_file = "Noongarborder_merged.shp"
input_file = "absolute_change_1993_2022_minus_1961_1990.nc"
output_file = "Noongar_mask.nc"

# Build full paths
nc_path = os.path.join(input_dir, input_file)
shapefile_path = os.path.join(shapefile_dir, shape_file)
output_path = os.path.join(output_dir, output_file)

## Step 2: Load the NetCDF data
ds = xr.open_dataset(nc_path)

lat = ds['lat'].values
lon = ds['lon'].values

# Create 2D lat/lon grids
lon2d, lat2d = np.meshgrid(lon, lat)

# Flatten to 1D
lat1d = lat2d.ravel()
lon1d = lon2d.ravel()

## Step 3: Read the shapefile
gdf = gpd.read_file(shapefile_path)

# Ensure the shapefile and data are in the same CRS
if gdf.crs is None:
    gdf.set_crs("EPSG:4326", inplace=True)  # Assuming WGS84
else:
    gdf = gdf.to_crs("EPSG:4326")

## Step 4: Create mask
points = gpd.GeoSeries([Point(x, y) for x, y in zip(lon1d, lat1d)], crs="EPSG:4326")
mask_flat = points.within(gdf.unary_union)
mask_2d = mask_flat.values.reshape(lat2d.shape).astype(int)

## Step 5: Save mask to NetCDF
mask_ds = xr.Dataset(
    {"mask_region": (["lat", "lon"], mask_2d)},
    coords={"lat": lat, "lon": lon}
)

mask_ds.to_netcdf(output_path)
print(f"Mask saved to: {output_path}")

