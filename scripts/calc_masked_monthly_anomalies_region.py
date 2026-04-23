import xarray as xr
import numpy as np
import xarray as xr
import pandas as pd

# File paths
monthly_means_path = '/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_mthmeans_1900_2022.nc'
monthly_climatology_path = '/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_monclim_1961_1990.nc'
output_path = '/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_mthregionanom_1900-2022.nc'

# Load datasets
print("Loading datasets...")
monthly_means = xr.open_dataset(monthly_means_path)
monthly_climatology = xr.open_dataset(monthly_climatology_path)

# Identify the main variable
print("Identifying the main variable...")
var_name = list(monthly_means.data_vars)[0]
means = monthly_means[var_name]
climatology = monthly_climatology[var_name]

# Create a proper time coordinate from Year and Month dimensions
print("Creating time coordinate...")
years = monthly_means['year'].values
months = monthly_means['month'].values
year_grid, month_grid = np.meshgrid(years, months, indexing='ij')
flat_years = year_grid.flatten()
flat_months = month_grid.flatten()
time = pd.to_datetime({'year': flat_years, 'month': flat_months, 'day': 15})

# Reshape the data to [time, lat, lon]
means = means.stack(time=('year', 'month'))
means = means.assign_coords(time=time)
means = means.swap_dims({'time': 'time'})

# Calculate anomalies: subtract climatology for each month
print("Calculating anomalies...")
anomalies = means.groupby('time.month') - climatology

# Average over lat/lon to get regional mean anomaly
print("Averaging over lat/lon to get regional anomaly...")
regional_anomaly = anomalies.mean(dim=['lat', 'lon'])

# Create dataset
print("Creating dataset...")
result_ds = xr.Dataset({
    'monthly_anomaly': regional_anomaly
})

# Save to NetCDF
print("Saving to NetCDF...")
result_ds.to_netcdf(output_path)
print(f"Regional monthly anomalies saved to {output_path}")

