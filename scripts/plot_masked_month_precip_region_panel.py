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

# Ensure output directory exists
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
print("Generating two‑panel plot...")

month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
ax1, ax2 = axes

# ---------------------------------------------------------
# LEFT PANEL — 1961–1990
# ---------------------------------------------------------
ax1.errorbar(
    month_names, mean_LHS, yerr=std_LHS,
    fmt="-o", capsize=5, linewidth=2, markersize=8
)

ax1.grid(False)
ax1.set_xlabel("")
ax1.set_ylabel("Precipitation (mm)", fontsize=16)
ax1.set_ylim(0, 120)
ax1.tick_params(axis='both', labelsize=14)

# Panel label
ax1.text(0.02, 0.98, "a)", transform=ax1.transAxes,
         fontsize=18, ha='left', va='top')

# ---------------------------------------------------------
# RIGHT PANEL — 1993–2022
# ---------------------------------------------------------
ax2.errorbar(
    month_names, mean_RHS, yerr=std_RHS,
    fmt="-o", capsize=5, linewidth=2, markersize=8
)

ax2.grid(False)
ax2.set_xlabel("")
ax2.set_ylabel("")  # no duplicate y‑label
ax2.set_ylim(0, 120)
ax2.tick_params(axis='both', labelsize=14)

# Panel label
ax2.text(0.02, 0.98, "b)", transform=ax2.transAxes,
         fontsize=18, ha='left', va='top')

plt.tight_layout()

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------
output_file = os.path.join(output_dir, "rainfall_mean_month_two_panel.png")
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"Plot saved successfully to: {output_file}")

plt.close()
plt.show()
