import xarray as xr
import numpy as np
import glob
import dask
import os

#################### Inputs ##########################################################################
# Define input dir where AGCD 1km monthly precip data lives
input_dir = "/data2/AGCD/v2-0-1/precip/total/r001/01month/"
# Select the variable of interest
variable = 'precip'  # Replace with your variable name
start_year = 1900
end_year = 1901    # Replace with your end year
output_dir = "/data2/Jatin/AGCD_Clim_Sarah_Sapsford_Paper/" # Note to Kerryn: Change to YOUR dir
mask_file = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/mask_merged.nc"
nlat = 1501 
nlon = 1801
######################################################################################################
# create output dir in case it does not exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Directory '{output_dir}' created.")
else:
    print(f"Directory '{output_dir}' already exists.")

# pre=allocated an empty array with all missing of size (years, 12, lat, lon)
num_years = end_year - start_year + 1
num_months = 12
reshaped_means = np.ma.masked_all((num_years, num_months,nlat,nlon))

# loop from start_year to end_year
cc = 0
for yr in range(start_year,end_year+1):
    file_open=input_dir + "agcd_v2-0-1_precip_total_r001_monthly_" + str(yr) + ".nc"
    print("opening: " + file_open)
    ds = xr.open_dataset(file_open)
    del(file_open)
 # Subset the region
    ds = ds.sel(lat=slice(-37, -22), lon=slice(110, 130))
    data = ds[variable]
    # get variable attribute for writing later on
    attrs_data = data.attrs
    # will need lat and lon when writing
    lat = ds["lat"]
    lon = ds["lon"]
    mask_ds = xr.open_dataset(mask_file)
    mask_var = list(mask_ds.data_vars)[0]  # Automatically get the first variable
    mask = mask_ds[mask_var]
    mask = mask.sel(lat=data.lat, lon=data.lon) # Align mask to data dimensions
    masked_data = data.where(mask == 1)
    reshaped_means[cc,:,:,:] = masked_data
    cc = cc + 1
    mask_ds.close()
    ds.close()
    del(data,mask_var,mask,masked_data)



reshaped_ds = xr.DataArray(reshaped_means,dims=['year', 'month', 'lat', 'lon'],coords={'year': np.arange(start_year, end_year + 1),'month': np.arange(1, 13),'lat': lat,'lon': lon})

# re-add the variable attributes before writing
reshaped_ds.attrs = attrs_data

# Save the monthly means to a new NetCDF file
# define a file name to save the output file
file_save = os.path.join(output_dir, f"masked_mthmeans_{start_year}_{end_year}.nc")

# Delete the output file if it exists
if os.path.exists(file_save):
    os.remove(file_save)
    print(f"Output file '{file_save}' has been deleted.")

# Name the variable name before saving
reshaped_ds.name = variable

print("saving to: " + file_save)
reshaped_ds.to_netcdf(file_save)

