import xarray as xr
import numpy as np
import pandas as pd

# File paths
monthly_means_path = '/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_mthmeans_1900_2022.nc'
monthly_climatology_path = '/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_monclim_1961_1990.nc'
output_path = '/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_seasregionanom_1900-2022.nc'

# Load datasets
print("Loading datasets...")
monthly_means = xr.open_dataset(monthly_means_path)
monthly_climatology = xr.open_dataset(monthly_climatology_path)

# Identify the main variable
print("Identifying the main variable...")
var_name = list(monthly_means.data_vars)[0]
means = monthly_means[var_name]
climatology = monthly_climatology[var_name]

# Calculate anomalies: subtract climatology for each month
print("Calculating anomalies...")
anomalies = means - climatology

# Average over lat/lon to get regional mean anomaly
print("Averaging over lat/lon to get regional anomaly...")
regional_anomaly = anomalies.mean(dim=['lat', 'lon'])

# Convert to DataFrame
df = regional_anomaly.to_dataframe(name='anomaly').reset_index()

# Define seasons and their months
season_definitions = {
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

# Assign season-year for cross-year seasons
def assign_season_year(row, months):
    if 12 in months and row['month'] == 12:
        return row['year'] + 1
    else:
        return row['year']

# Calculate seasonal means
print("Calculating seasonal anomalies...")
seasonal_data = []

for season, months in season_definitions.items():
    season_df = df[df['month'].isin(months)].copy()
    season_df['season_year'] = season_df.apply(assign_season_year, axis=1, months=months)
    season_mean = season_df.groupby('season_year')['anomaly'].sum().reset_index()
    season_mean['season'] = season
    seasonal_data.append(season_mean)

# Combine all seasonal data
print("Combining seasonal data...")
seasonal_df = pd.concat(seasonal_data, ignore_index=True)

# Convert to xarray Dataset
print("Converting to xarray Dataset...")
seasonal_ds = seasonal_df.set_index(['season', 'season_year']).to_xarray()

# Save to NetCDF
print("Saving to NetCDF...")
seasonal_ds.to_netcdf(output_path)
print(f"Regional seasonal anomalies saved to {output_path}")

