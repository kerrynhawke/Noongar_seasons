import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import pyproj

# ---------------------------------------------------------
# Define input/output directories and file names
# ---------------------------------------------------------
input_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/outputs"
output_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/figs"

precip_file = "masked_abs_change_1993_2022_minus_1961_1990.nc"
sig_file = "mask_abs_month_significance_masked.nc"

precip_path = os.path.join(input_dir, precip_file)
sig_path = os.path.join(input_dir, sig_file)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------
print(f"Opening precipitation dataset: {precip_path}")
ds_precip = xr.open_dataset(precip_path)

print(f"Opening significance mask dataset: {sig_path}")
ds_sig = xr.open_dataset(sig_path)

# Extract variables
print("Extracting variables: precip, lon, lat, significance mask")
precip = ds_precip['precip'].values
lon = ds_precip['lon'].values
lat = ds_precip['lat'].values
sig_mask = ds_sig['significance'].values  # shape: (month, lat, lon)

# ---------------------------------------------------------
# Plot configuration
# ---------------------------------------------------------
month_labels = ["DEC", "JAN", "FEB", "MAR", "APR", "MAY",
                "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]

print("Creating 4x3 subplot grid")
fig, axes = plt.subplots(4, 3, figsize=(18, 16),
                         subplot_kw={'projection': ccrs.PlateCarree()})
axes = axes.flatten()

# Adjust layout spacing
plt.subplots_adjust(hspace=0.05, wspace=0.02)

## Title
#fig.suptitle("Absolute change in monthly rainfall", fontsize=18, y=0.92)

# ---------------------------------------------------------
# Custom colormap (Red → White → Blue)
# ---------------------------------------------------------
colors = [(1, 0, 0), (1, 1, 1), (0, 0, 1)]
cmap = mcolors.LinearSegmentedColormap.from_list("red_white_blue", colors, N=100)

# ---------------------------------------------------------
# Loop through each month and plot
# ---------------------------------------------------------
for i, month_abbr in enumerate(month_labels):
    print(f"Processing month: {month_abbr}")
    ax = axes[i]

    # Reorder so DEC is first
    month_index = (i + 11) % 12

    month_precip = precip[month_index, :, :]
    month_sig = sig_mask[month_index, :, :]

    # Filled contour plot
    cs = ax.contourf(
        lon, lat, month_precip,
        cmap=cmap,
        levels=np.linspace(-50, 50, 100),
        extend='both',
        transform=ccrs.PlateCarree()
    )

    # ---------------------------------------------------------
    # Significance shading (grey, semi-transparent)
    # ---------------------------------------------------------
    hatch_mask = np.ma.masked_where(month_sig != 1, month_sig)

    ax.contourf(
        lon, lat, hatch_mask,
        colors=['grey'],          # grey fill
        alpha=0.3,                # semi-transparent
        transform=ccrs.PlateCarree(),
        zorder=3
    )
 
    # Month label (top-left)
    ax.text(0.98, 0.98, month_abbr,
            transform=ax.transAxes,
            fontsize=12,
            ha='right', va='top'
    )

    # Map formatting
    ax.coastlines()
    ax.set_extent([113.5, 124.5, -36.0, -29.0], crs=ccrs.PlateCarree())

# ---------------------------------------------------------
# Colorbar
# ---------------------------------------------------------
print("Adding colorbar")
cbar = fig.colorbar(cs, ax=axes, orientation='horizontal',
                    fraction=0.03, pad=0.05,
                    ticks=np.arange(-50, 51, 10))
cbar.set_label("mm", fontsize=12)

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------
output_file = os.path.join(output_dir, "abs_change_monthly_rainfall.png")
print(f"Saving figure to: {output_file}")
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print("Plot saved and figure closed.")
plt.show()
