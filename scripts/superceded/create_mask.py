import os
os.environ["PROJ_LIB"] = "/data/Kerryn/miniconda3/envs/python/share/proj"
import xarray as xr
import geopandas as gpd
shapefile_path = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/Noongarborder_merged.shp"
gdf = gpd.read_file(shapefile_path, engine="fiona")
import numpy as np
from shapely.geometry import Point



#### Step 1: Set input/output directory ####
base_dir = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper"

#### Step 2: Load the NetCDF data ####
nc_path = os.path.join(base_dir, "absolute_change_1993_2022_minus_1961_1990.nc")
ds = xr.open_dataset(nc_path)

lat = ds['lat'].values
lon = ds['lon'].values

# Create 2D lat/lon grids
lon2d, lat2d = np.meshgrid(lon, lat)

# Flatten to 1D
lat1d = lat2d.ravel()
lon1d = lon2d.ravel()

#### Step 3: Read the shapefile ####
shapefile_path = os.path.join(base_dir, "Noongarborder_merged.shp") #define the mask input .shp filename
gdf = gpd.read_file(shapefile_path)

# Ensure the shapefile and data are in the same CRS
if gdf.crs is None:
    gdf.set_crs("EPSG:4326", inplace=True)  # Assuming WGS84
else:
    gdf = gdf.to_crs("EPSG:4326")

#### Step 4: Create mask ####
points = gpd.GeoSeries([Point(x, y) for x, y in zip(lon1d, lat1d)], crs="EPSG:4326")
mask_flat = points.within(gdf.unary_union)
mask_2d = mask_flat.values.reshape(lat2d.shape).astype(int)

#### Step 5: Save mask to NetCDF ####
output_path = os.path.join(base_dir, "mask_merged.nc") # define the mask output .nc filename
mask_ds = xr.Dataset(
    {"mask_region": (["lat", "lon"], mask_2d)},
    coords={"lat": lat, "lon": lon}
)

mask_ds.to_netcdf(output_path)
print(f"Mask saved to: {output_path}")

