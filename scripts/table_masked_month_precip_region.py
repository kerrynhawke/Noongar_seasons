import xarray as xr
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
import os

# ---------------------------------------------------------
# Define input/output directories and file names
# ---------------------------------------------------------
input_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/outputs"
output_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/tables"

file_LHS = "masked_mthmeans_1961_1990.nc"
file_RHS = "masked_mthmeans_1993_2022.nc"

path_LHS = os.path.join(input_dir, file_LHS)
path_RHS = os.path.join(input_dir, file_RHS)

os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------
# Function to compute monthly spatial means
# ---------------------------------------------------------
def compute_monthly_means(path):
    print(f"Loading dataset: {path}")
    ds = xr.open_dataset(path)

    precip = ds["precip"]  # (year, month, lat, lon)

    # Spatial mean over region
    spatial_mean = precip.mean(dim=["lat", "lon"], skipna=True)

    # Monthly mean across years
    monthly_mean = spatial_mean.mean(dim="year", skipna=True)

    return monthly_mean.values  # length 12


# ---------------------------------------------------------
# Compute monthly means for both periods
# ---------------------------------------------------------
mean_LHS = compute_monthly_means(path_LHS)
mean_RHS = compute_monthly_means(path_RHS)

# ---------------------------------------------------------
# Load full datasets for significance testing
# ---------------------------------------------------------
ds_LHS = xr.open_dataset(path_LHS)["precip"].mean(dim=["lat", "lon"])
ds_RHS = xr.open_dataset(path_RHS)["precip"].mean(dim=["lat", "lon"])

# ---------------------------------------------------------
# Build comparison table
# ---------------------------------------------------------
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

df = pd.DataFrame({
    "Month": month_names,
    "1961–1990 (mm)": mean_LHS,
    "1993–2022 (mm)": mean_RHS,
})

# ---------------------------------------------------------
# Calculate differences
# ---------------------------------------------------------
df["Difference (mm)"] = df["1993–2022 (mm)"] - df["1961–1990 (mm)"]
df["% Difference"] = (df["Difference (mm)"] / df["1961–1990 (mm)"]) * 100

# ---------------------------------------------------------
# Mann–Whitney U significance test for each month
# ---------------------------------------------------------
p_values = []

for m in range(12):
    lhs_vals = ds_LHS.sel(month=m+1).values  # 30 values
    rhs_vals = ds_RHS.sel(month=m+1).values  # 30 values

    stat, p = mannwhitneyu(lhs_vals, rhs_vals, alternative="two-sided")
    p_values.append(p)

df["p-value"] = p_values
df["Significant (<0.05)"] = df["p-value"] < 0.05

# ---------------------------------------------------------
# Round values for readability
# ---------------------------------------------------------
df = df.round({
    "1961–1990 (mm)": 1,
    "1993–2022 (mm)": 1,
    "Difference (mm)": 1,
    "% Difference": 1,
    "p-value": 4
})

# ---------------------------------------------------------
# Save CSV
# ---------------------------------------------------------
csv_path = os.path.join(output_dir, "monthly_precip_comparison_with_significance.csv")
df.to_csv(csv_path, index=False)

print("\nMonthly precipitation comparison table saved to:")
print(csv_path)
print("\nPreview:\n")
print(df.to_string(index=False))
