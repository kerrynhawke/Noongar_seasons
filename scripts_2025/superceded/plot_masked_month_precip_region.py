import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

# Load the dataset
file_path = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_mthmeans_1993_2022.nc"
print(f"Loading dataset from: {file_path}")
ds = xr.open_dataset(file_path)

# Display dataset info
print("Dataset loaded successfully.")
print("Variables in dataset:", list(ds.data_vars))
print("Dimensions:", ds.dims)

# Extract the precipitation data
print("Extracting 'precip' variable...")
precip = ds['precip']  # shape: (year, month, lat, lon)
print(f"Precipitation data shape: {precip.shape}")

# Compute spatial mean for each year and month
print("Computing spatial mean (averaging over lat and lon)...")
spatial_mean = precip.mean(dim=['lat', 'lon'], skipna=True)  # shape: (year, month)
print(f"Spatial mean shape: {spatial_mean.shape}")

# Compute monthly mean across years
print("Computing monthly mean across years...")
monthly_mean = spatial_mean.mean(dim='year', skipna=True)  # shape: (month)
print("Monthly mean values:")
print(monthly_mean.values)

# Compute standard deviation across years for each month
print("Computing monthly standard deviation across years...")
monthly_std = spatial_mean.std(dim='year', skipna=True)  # shape: (month)
print("Monthly standard deviation values:")
print(monthly_std.values)

# Create output directory
output_dir = "dir_figs"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "rainfall_mean_month.png")

# Plotting
print("Generating plot...")
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
plt.figure(figsize=(10, 6))
plt.errorbar(month_names, monthly_mean.values, yerr=monthly_std.values, fmt='-o', capsize=5, label='Mean ± Std Dev')
plt.xlabel('Month')
plt.ylabel('Precipitation (mm)')
plt.ylim(0,120)
plt.title('30-year average rainfall by month (1993-2022)')
plt.grid(True)
#plt.legend()
plt.tight_layout()

# Save the plot
plt.savefig(output_file)
print(f"Plot saved successfully to: {output_file}")

# Display the plot
plt.show()

