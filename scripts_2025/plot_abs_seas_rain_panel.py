import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pyproj
import matplotlib.colors as mcolors
import os

# Set variables
variable = 'rain'
time = 'seas'
change = 'abs_sig'
mask = 'mask'

# Set the PROJ database path
pyproj.datadir.set_data_dir('/data/Kerryn/miniconda3/envs/python/lib/python3.12/site-packages/pyproj/proj_dir/share/proj')

# Load the dataset
fopen = nc.Dataset("/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_abs_change_1993_2022_minus_1961_1990.nc", "r")
print("Opening dataset")

precip = fopen.variables['precip'][:]
lon = fopen.variables['lon'][:]
lat = fopen.variables['lat'][:]

# Load the significance mask
sig_file = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/mask_abs_season_significance_masked.nc"
sig_ds = nc.Dataset(sig_file, "r")
sig_mask = sig_ds.variables['significance'][:]  # shape: (season, lat, lon)

# Define seasonal groupings
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

# Set up the plot and axis
fig, axs = plt.subplots(nrows=4, ncols=3, subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(11, 11))
axs = axs.flatten()

fig.suptitle("Absolute change in seasonal rainfall", fontsize=14, y=0.95)
plt.subplots_adjust(hspace=0.005, wspace=0.05, top=0.93, bottom=0.08)

# Define custom colormap
colors = [(1, 0, 0), (1, 1, 1), (0, 0, 1)]  # R -> W -> B
n_bins = 100
cm = mcolors.LinearSegmentedColormap.from_list('red_white_blue', colors, N=n_bins)

# Plot each season
for i, label in enumerate(plot_order):
    if label is None:
        axs[i].axis('off')
        continue
    months = season_layout[label]
    season_index = season_names.index(label)
    season_precip = np.mean([precip[m, :, :] for m in months], axis=0)
    season_sig = sig_mask[season_index, :, :]

    # Plot precipitation
    cs = axs[i].contourf(lon[:], lat[:], season_precip, transform=ccrs.PlateCarree(),
                         cmap=cm, levels=np.linspace(-50, 50, n_bins), extend='both')

    # Overlay grey cross-hatching for significant areas
    hatch_mask = np.ma.masked_where(season_sig != 1, season_sig)
    axs[i].contourf(lon[:], lat[:], hatch_mask, transform=ccrs.PlateCarree(),
                    colors='none', hatches=['xxxx'], linewidths=0)

    axs[i].text(0.95, 0.92, label, transform=axs[i].transAxes,
                fontsize=10, ha='right', va='top',
                bbox=dict(facecolor='white', edgecolor='black'))

    axs[i].coastlines()
    axs[i].set_extent([113.5, 124.5, -36.0, -29.0], crs=ccrs.PlateCarree())

# Add a single colorbar
cbar = fig.colorbar(cs, ax=axs, orientation='horizontal', fraction=0.02, pad=0.04, ticks=np.arange(-50, 51, 10))
cbar.set_label('mm', labelpad=10)
print("Adding single colourbar")

# Save the figure
file_save = f"{mask}_{change}_change_{time}_{variable}.png"
output_path = os.path.join("dir_figs", file_save)
os.makedirs("dir_figs", exist_ok=True)

if os.path.exists(output_path):
    os.remove(output_path)
    print(f"Output file '{file_save}' has been deleted.")

plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saving file as {output_path}")

# Display the plot
plt.show()

