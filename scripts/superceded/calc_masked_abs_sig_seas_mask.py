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
hist_ds = xr.open_dataset(os.path.join(input_dir, "monthlymeans_1961_1990.nc"))
recent_ds = xr.open_dataset(os.path.join(input_dir, "monthlymeans_1993_2022.nc"))
mask_ds = xr.open_dataset(mask_path)

# Extract precipitation data
print("Extracting precipitation data")
hist_precip = hist_ds['precip']
recent_precip = recent_ds['precip']
mask = mask_ds['mask_region'].values.astype(bool)

# Get dimensions
n_months = 12
n_years = hist_precip.shape[0] // 12
n_lat = hist_precip.shape[1]
n_lon = hist_precip.shape[2]

# Reshape to (years, months, lat, lon)
print("Reshaping to years")
hist_precip = hist_precip.values.reshape((n_years, n_months, n_lat, n_lon))
recent_precip = recent_precip.values.reshape((n_years, n_months, n_lat, n_lon))

# Define seasons
seasons = {
    'Summer': [12, 1, 2],
    'Autumn': [3, 4, 5],
    'Winter': [6, 7, 8],
    'Spring': [9, 10, 11],
    'Birak': [12, 1],
    'Bunuru': [2, 3],
    'Djeran': [4, 5],
    'Makuru': [6, 7],
    'Djilba': [8, 9],
    'Kambarang': [10, 11]
}
season_names = list(seasons.keys())
n_seasons = len(season_names)

# Function to compute seasonal means
def get_seasonal_means(data, season_months):
    season_data = []
    for months in season_months.values():
        month_indices = [(m - 1) % 12 for m in months]
        season_mean = data[:, month_indices, :, :].mean(axis=1)
        season_data.append(season_mean)
    return np.array(season_data)

# Compute seasonal means
print("Computing seasonal means")
hist_seasonal = get_seasonal_means(hist_precip, seasons)
recent_seasonal = get_seasonal_means(recent_precip, seasons)

# Create mask array: True where p < 0.05
print("Creating mask array where p < 0.05")
sig_mask = np.full((n_seasons, n_lat, n_lon), False, dtype=bool)

# Perform Mann-Whitney U test for each season
print("Performing Mann-Whitney U test for each season")
for i in range(n_seasons):
    hist_vals = hist_seasonal[i].reshape(n_years, -1)
    recent_vals = recent_seasonal[i].reshape(n_years, -1)
    U, P = mannwhitneyu(hist_vals, recent_vals, axis=0, alternative='two-sided')
    P = P.reshape(n_lat, n_lon)
    sig_mask[i] = (P < 0.05) & mask  # Apply spatial mask

# Construct output filename and path
print("Creating output filename and path")
time = 'season'
change = 'abs'
mask_label = 'mask'
output_filename = f"{mask_label}_{change}_{time}_significance_masked.nc"
output_path = os.path.join(output_dir, output_filename)

# Save significance mask to NetCDF
print("Saving significance mask to NetCDF")
sig_ds = xr.Dataset(
    {
        "significance": (["season", "lat", "lon"], sig_mask.astype(np.int8))
    },
    coords={
        "season": season_names,
        "lat": hist_ds["lat"],
        "lon": hist_ds["lon"]
    }
)
sig_ds["significance"].attrs["description"] = "Binary mask where 1 indicates p < 0.05 from Mann-Whitney U test, masked by valid regions"
sig_ds["significance"].attrs["units"] = "boolean"
sig_ds.to_netcdf(output_path)

print(f"Significance mask saved to '{output_path}'")

# Close datasets
hist_ds.close()
recent_ds.close()
mask_ds.close()

