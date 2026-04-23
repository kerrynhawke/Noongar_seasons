import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------
# Define input/output directories and file names
# ---------------------------------------------------------
input_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/outputs"
output_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/figs"

file_LHS = "masked_mthmeans_1961_1990.nc"
file_RHS = "masked_mthmeans_1993_2022.nc"

path_LHS = os.path.join(input_dir, file_LHS)
path_RHS = os.path.join(input_dir, file_RHS)

os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------
# Function to compute monthly mean + std
# ---------------------------------------------------------
def compute_month_stats(path):
    print(f"Loading dataset: {path}")
    ds = xr.open_dataset(path)

    precip = ds["precip"]  # (year, month, lat, lon)

    # Spatial mean
    spatial_mean = precip.mean(dim=["lat", "lon"], skipna=True)

    # Monthly mean + std across years
    monthly_mean = spatial_mean.mean(dim="year", skipna=True)
    monthly_std = spatial_mean.std(dim="year", skipna=True)

    return monthly_mean.values, monthly_std.values

# ---------------------------------------------------------
# Compute stats for both periods
# ---------------------------------------------------------
mean_LHS, std_LHS = compute_month_stats(path_LHS)
mean_RHS, std_RHS = compute_month_stats(path_RHS)

# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------
print("Generating overlay plot...")

month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

plt.figure(figsize=(12, 6))

# ---------------------------------------------------------
# 1961–1990 (blue)
# ---------------------------------------------------------
plt.plot(
    month_names, mean_LHS,
    color="blue", linewidth=2, label="1961–1990"
)

plt.fill_between(
    month_names,
    mean_LHS - std_LHS,
    mean_LHS + std_LHS,
    color="blue",
    alpha=0.2
)

# ---------------------------------------------------------
# 1993–2022 (red)
# ---------------------------------------------------------
plt.plot(
    month_names, mean_RHS,
    color="red", linewidth=2, label="1993–2022"
)

plt.fill_between(
    month_names,
    mean_RHS - std_RHS,
    mean_RHS + std_RHS,
    color="red",
    alpha=0.2
)

# ---------------------------------------------------------
# Formatting
# ---------------------------------------------------------
plt.ylabel("Precipitation (mm)", fontsize=16)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.ylim(0, 120)

plt.grid(False)
plt.xlabel("")  # no x-axis label

plt.legend(fontsize=14)
plt.tight_layout()

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------
output_file = os.path.join(output_dir, "rainfall_mean_month_overlay.png")
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"Plot saved successfully to: {output_file}")

plt.close()
plt.show()
