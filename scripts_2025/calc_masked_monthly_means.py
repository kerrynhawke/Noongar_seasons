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
end_year = 2022    # Replace with your end year
output_dir = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/"
mask_file = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/mask_merged.nc"

######################################################################################################
# create output dir in case it does not exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Directory '{output_dir}' created.")
else:
    print(f"Directory '{output_dir}' already exists.")

print("getting list of files")

# get list of files, sorted just sorts the list as would happen with an ls command
file_list = sorted(glob.glob(input_dir + 'agcd_v2-0-1_precip_total_r001_monthly_*.nc'))  # Replace with your directory and file pattern

print("opening files")
# Open multiple NetCDF files as a single dataset
with xr.open_mfdataset(file_list, combine='by_coords', parallel=True) as ds:

    # Subset the region
    ds = ds.sel(lat=slice(-37, -22), lon=slice(110, 130))

    # get the data
    print("getting data")
    data = ds[variable]

    # Filter the data for the specified period
    data = data.sel(time=slice(f'{start_year}-01-01', f'{end_year}-12-31'))

    print("Loading mask")
    mask_ds = xr.open_dataset(mask_file)
    mask_var = list(mask_ds.data_vars)[0]  # Automatically get the first variable
    mask = mask_ds[mask_var]
    mask = mask.sel(lat=data.lat, lon=data.lon) # Align mask to data dimensions 

    print("Applying mask")
    masked_data = data.where(mask == 1)

    # Calculate monthly means
    print("calculating monthly means")
    monthly_means = masked_data.resample(time='1MS').mean()

    # Ensure the time dimension is monthly
    print("verifying monthly")
    print (monthly_means)

    # Reshape the data to (number of years, number of months)
    num_years = end_year - start_year + 1
    num_months = 12
    reshaped_means = monthly_means.values.reshape(num_years, num_months, *monthly_means.shape[1:])


    reshaped_ds = xr.DataArray(
            reshaped_means,
            dims=['year', 'month', 'lat', 'lon'],
            coords={
                'year': np.arange(start_year, end_year + 1),
                'month': np.arange(1, 13),
                'lat': monthly_means.lat,
                'lon': monthly_means.lon
            }
        )

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

# close datasets
ds.close()
mask_ds.close()
