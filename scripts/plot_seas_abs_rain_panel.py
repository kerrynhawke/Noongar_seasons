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
sig_file = "mask_abs_season_significance_masked.nc"

precip_path = os.path.join(input_dir, precip_file)
sig_path = os.path.join(input_dir, sig_file)

os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------
print(f"Opening precipitation dataset: {precip_path}")
ds_precip = xr.open_dataset(precip_path)

print(f"Opening significance mask dataset: {sig_path}")
ds_sig = xr.open_dataset(sig_path)

print("Extracting variables: precip, lon, lat, significance mask")
precip = ds_precip['precip'].values
lon = ds_precip['lon'].values
lat = ds_precip['lat'].values
sig_mask = ds_sig['significance'].values   # shape: (season, lat, lon)

# ---------------------------------------------------------
# Define seasonal groupings
# ---------------------------------------------------------
season_layout = {
    "Summer (DJF)": [11, 0, 1],
    "Birak (DJ)": [11, 0],
    "Bunuru (FM)": [1, 2],
    "Autumn (MAM)": [2, 3, 4],
    "Djeran (AM)": [3, 4],
    "Winter (JJA)": [5, 6, 7],
    "Makuru (JJ)": [5, 6],
    "Spring (SON)": [8, 9, 10],
    "Djilba (AS)": [7, 8],
    "Kambarang (ON)": [9, 10],
}

plot_order = [
    "Summer (DJF)", "Birak (DJ)", "Bunuru (FM)",
    "Autumn (MAM)", "Djeran (AM)", None,
    "Winter (JJA)", "Makuru (JJ)", None,
    "Spring (SON)", "Djilba (AS)", "Kambarang (ON)"
]

season_names = list(season_layout.keys())

# ---------------------------------------------------------
# Plot configuration
# ---------------------------------------------------------
print("Creating 4x3 subplot grid")
fig, axes = plt.subplots(4, 3, figsize=(18, 16),
                         subplot_kw={'projection': ccrs.PlateCarree()})
axes = axes.flatten()

# Adjust layout spacing
plt.subplots_adjust(hspace=0.05, wspace=0.02)

## Title
#fig.suptitle("Absolute change in seasonal rainfall", fontsize=18, y=0.92)

# ---------------------------------------------------------
# Custom colormap (Red → White → Blue)
# ---------------------------------------------------------
colors = [(1, 0, 0), (1, 1, 1), (0, 0, 1)]
cmap = mcolors.LinearSegmentedColormap.from_list("red_white_blue", colors, N=100)

# ---------------------------------------------------------
# Loop through each season and plot
# ---------------------------------------------------------
for i, label in enumerate(plot_order):
    ax = axes[i]

    if label is None:
        ax.axis("off")
        continue

    print(f"Processing season: {label}")

    months = season_layout[label]
    season_index = season_names.index(label)

    season_precip = np.mean([precip[m, :, :] for m in months], axis=0)
    season_sig = sig_mask[season_index, :, :]

    # Filled contour plot
    cs = ax.contourf(
        lon, lat, season_precip,
        cmap=cmap,
        levels=np.linspace(-50, 50, 100),
        extend='both',
        transform=ccrs.PlateCarree()
    )

    # ---------------------------------------------------------
    # Significance shading (grey, semi-transparent)
    # ---------------------------------------------------------
    hatch_mask = np.ma.masked_where(season_sig != 1, season_sig)

    ax.contourf(
        lon, lat, hatch_mask,
        colors=['grey'],
        alpha=0.3,
        transform=ccrs.PlateCarree(),
        zorder=3
    )

    # Season label (top-right)
    ax.text(
        0.98, 0.98, label,
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
output_file = os.path.join(output_dir, "abs_change_seasonal_rainfall.png")
print(f"Saving figure to: {output_file}")
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print("Plot saved and figure closed.")
plt.show()
