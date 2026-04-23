import xarray as xr 
import numpy as np 
import os

# Input files 
#climatology_file_1961_1990 = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/monclim_from_1961_1990.nc" #unmasked files
#climatology_file_1993_2022 = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/monclim_from_1993_2022.nc" #unmasked files
climatology_file_1961_1990 = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_monclim_1961_1990.nc"
climatology_file_1993_2022 = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_monclim_1993_2022.nc"

# Output files
absolute_change_output_file = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_abs_change_1993_2022_minus_1961_1990.nc"
proportional_change_output_file = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_prop_change_1993_2022_minus_1961_1990.nc"

# Load climatology datasets
print("Loading masked climatology files")
clim_1961_1990 = xr.open_dataset(climatology_file_1961_1990)
clim_1993_2022 = xr.open_dataset(climatology_file_1993_2022)

# Select the variable of interest (e.g., 'precip') 
variable = 'precip' 

# Select the variable from each dataset
print(f"Selecting variable: {variable}")
monthly_means_1961_1990 = clim_1961_1990[variable]
monthly_means_1993_2022 = clim_1993_2022[variable]

# Calculate the monthly means for each period
print("calculate monthly means")

# Extract monthly means
monthly_means_1961_1990 = clim_1961_1990[variable]
monthly_means_1993_2022 = clim_1993_2022[variable]

# Compute the absolute change in rainfall between the two periods 
print("calculate absolute change") 
absolute_change = monthly_means_1993_2022 - monthly_means_1961_1990 

# Compute the proportional change in rainfall between the two periods
print("calculate proportional change")

# Handle zero values to avoid division by zero
with np.errstate(divide='ignore', invalid='ignore'):
    proportional_change = absolute_change / monthly_means_1961_1990
    proportional_change = proportional_change.where(np.isfinite(proportional_change), np.nan)

# Save absolute and proportional change
print("save absolute and proportional change files")

for path, data in zip(
    [absolute_change_output_file, proportional_change_output_file],
    [absolute_change, proportional_change]
):
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted existing file: {path}")
    data.to_netcdf(path)
    print(f"Saved: {path}")

# close datasets
clim_1961_1990.close()
clim_1993_2022.close()
print("Datasets closed.")
