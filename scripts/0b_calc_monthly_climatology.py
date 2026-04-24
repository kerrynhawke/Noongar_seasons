import xarray as xr
import numpy as np
import glob
import os
#################### Inputs ##########################################################################
# Define input dir where AGCD 1km monthly precip data lives
input_dir="/data2/AGCD/v2-0-1/precip/total/r001/01month/"
# Select the variable of interest
variable = 'precip'  # Replace with your variable name
start_year = 1961
end_year = 1990    # Replace with your end year
output_dir="/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/"
mask_file = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/mask_merged.nc"

######################################################################################################
# create output dir in case it does not exist
# Check if the directory exists
if not os.path.exists(output_dir):
    # Create the directory
    os.makedirs(output_dir)
    print(f"Directory '{output_dir}' created.")
else:
    print(f"Directory '{output_dir}' already exists.")

print("getting list of files")
# get list of files, sorted just sorts the list as would happen with an ls command

file_list = sorted(glob.glob(os.path.join(input_dir, 'agcd_v2-0-1_precip_total_r001_monthly_*.nc')))

print("opening files")
# Open multiple NetCDF files as a single dataset with Dask
ds = xr.open_mfdataset(file_list, combine='by_coords', parallel=True)

print("subsetting region")
# subset the region
ds = ds.sel(lat=slice(-37,-22), lon=slice(110,130))

# get the data
print("getting data")
data = ds[variable]
# Filter the data for the specified period
data = data.sel(time=slice(f'{start_year}-01-01', f'{end_year}-12-31'))

# load the mask
print("Loading mask")
mask_ds = xr.open_dataset(mask_file)
mask_var = list(mask_ds.data_vars)[0]  # Automatically get the first variable
mask = mask_ds[mask_var]

# Align mask to data dimensions
#mask = mask.sel(lat=data.lat, lon=data.lon)
data, mask = xr.align(data, mask, join="exact")

print("Applying mask")
masked_data = data.where(mask == 1)

# Calculate monthly climatologies
# Function to calculate monthly mean
def monthly_mean(data):
    return data.groupby('time.month').mean('time')

# Calculate climatologies for each month
print("calc the clim")
monthly_climatologies = monthly_mean(masked_data)

# Name the variable before saving
monthly_climatologies.name = variable

# Save the monthly climatologies to a new NetCDF file
# define a file name to save the output file
file_save = output_dir + "masked_monclim_" + str(start_year) + "_" + str(end_year) + ".nc"

# Delete the output file if it exists
if os.path.exists(file_save):
    os.remove(file_save)
    print(f"Output file '{file_save}' has been deleted.")

print("saving to: " + file_save)
monthly_climatologies.to_netcdf(file_save)

# close datasets
ds.close()
mask_ds.close()
