import xarray as xr
import numpy as np
from scipy.stats import mannwhitneyu
import os

# Set input and output file directories
print("Setting file directories")
input_dir = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/"
output_dir = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/"
mask_path = os.path.join(input_dir, "mask_merged.nc")

# Load datasets using xarray
print("Loading datasets with xarray")
hist_ds = xr.open_dataset(os.path.join(input_dir, "masked_mthmeans_1961_1990.nc"))
recent_ds = xr.open_dataset(os.path.join(input_dir, "masked_mthmeans_1993_2022.nc"))
mask_ds = xr.open_dataset(mask_path)

# Extract precipitation data
print("Extracting precipitation data")
hist_precip = hist_ds['precip']
recent_precip = recent_ds['precip']
mask = mask_ds['mask_region'].values.astype(bool)

# Stack year and month into a single time dimension
print("Stacking year and month into time dimension")
hist_precip = hist_ds['precip'].stack(time=('year', 'month')).transpose('time', 'lat', 'lon')
recent_precip = recent_ds['precip'].stack(time=('year', 'month')).transpose('time', 'lat', 'lon')

# Extract dimensions
n_months = 12
n_years = hist_precip.sizes['time'] // n_months
n_lat = hist_precip.sizes['lat']
n_lon = hist_precip.sizes['lon']

# Reshape to (years, months, lat, lon)
print("Reshaping to (years, months, lat, lon)")
hist_precip = hist_precip.values.reshape((n_years, n_months, n_lat, n_lon))
recent_precip = recent_precip.values.reshape((n_years, n_months, n_lat, n_lon))

# Compute proportional change
print("Computing proportional change")
epsilon = 1e-6  # to avoid division by zero
hist_safe = np.where(hist_precip == 0, epsilon, hist_precip)
prop_change = (recent_precip - hist_precip) / hist_safe

# Create mask array: True where p < 0.05
print("Creating mask array where p < 0.05")
sig_mask = np.full((n_months, n_lat, n_lon), False, dtype=bool)

# Perform Mann-Whitney U test for each month
print("Performing Mann-Whitney U test for each month")
for m in range(n_months):
    prop_vals = prop_change[:, m, :, :].reshape(n_years, -1)
    U, P = mannwhitneyu(prop_vals, np.zeros_like(prop_vals), axis=0, alternative='two-sided')
    P = P.reshape(n_lat, n_lon)
    sig_mask[m] = (P < 0.05) & mask  # Apply spatial mask

# Construct output filename and path
print("Creating output filename and path")
time = 'month'
change = 'prop'
mask_label = 'mask'
output_filename = f"{mask_label}_{change}_{time}_significance_masked.nc"
output_path = os.path.join(output_dir, output_filename)

# Save significance mask to NetCDF
print("Saving significance mask to NetCDF")
sig_ds = xr.Dataset(
    {
        "significance": (["month", "lat", "lon"], sig_mask.astype(np.int8))
    },
    coords={
        "month": np.arange(1, 13),
        "lat": hist_ds["lat"],
        "lon": hist_ds["lon"]
    }
)
sig_ds["significance"].attrs["description"] = "Binary mask where 1 indicates p < 0.05 from Mann-Whitney U test on monthly proportional change, masked by valid regions"
sig_ds["significance"].attrs["units"] = "boolean"
sig_ds.to_netcdf(output_path)

print(f"Significance mask saved to '{output_path}'")

# Close datasets
hist_ds.close()
recent_ds.close()
mask_ds.close()

