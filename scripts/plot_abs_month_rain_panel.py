import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pyproj
import matplotlib.colors as mcolors
import os

# Set variables
variable = 'rain_sig'
time = 'month'
change = 'abs_sig'
mask = 'mask'

# Set the PROJ database path
pyproj.datadir.set_data_dir('/data/Kerryn/miniconda3/envs/python/lib/python3.12/site-packages/pyproj/proj_dir/share/proj')

# Open the masked monthly precipitation data file
fopen = nc.Dataset("/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/masked_abs_change_1993_2022_minus_1961_1990.nc", "r")
print("Opening dataset")

# Load the precipitation data
precip = fopen.variables['precip'][:]
lon = fopen.variables['lon'][:]
lat = fopen.variables['lat'][:]

# Load the significance mask
sig_file = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper/mask_abs_month_significance_masked.nc"
sig_ds = nc.Dataset(sig_file, "r")
sig_mask = sig_ds.variables['significance'][:]  # shape: (month, lat, lon)

# Set up the plot and axis
fig, axs = plt.subplots(nrows=4, ncols=3, subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(8.5, 11))
print("Setting up plot format")
axs = axs.flatten()

# Adjust spacing between subplots
plt.subplots_adjust(hspace=0.005, wspace=0.05, top=0.93, bottom=0.08)

# Labels for each subplot
fig_label = ["DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]
print("Adding labels")

# Add a title to the panel plot
fig.suptitle("Absolute change in monthly rainfall", fontsize=14, y=0.95)
print("Adding title")

# Define the custom colormap
colors = [(1, 0, 0), (1, 1, 1), (0, 0, 1)]  # R -> W -> B
n_bins = 100
cmap_name = 'red_white_blue'
cm = mcolors.LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

# Loop through each month
for i in range(precip.shape[0]):
    month_index = (i + 11) % 12
    month_precip = precip[month_index, :, :]
    month_sig = sig_mask[month_index, :, :]

    # Plot precipitation
    cs = axs[i].contourf(lon[:], lat[:], month_precip, transform=ccrs.PlateCarree(),
                         cmap=cm, levels=np.linspace(-50, 50, n_bins), extend='both')

    # Overlay cross hatching for significant areas
    hatch_mask = np.ma.masked_where(month_sig != 1, month_sig)
    axs[i].contourf(lon[:], lat[:], hatch_mask, transform=ccrs.PlateCarree(),
                    colors='none', hatches=['xxxx'], linewidths=0)

    axs[i].text(0.95, 0.92, fig_label[i], transform=axs[i].transAxes,
                fontsize=10, ha='right', va='top',
                bbox=dict(facecolor='white', edgecolor='black'))

    axs[i].coastlines()
    axs[i].set_extent([113.5, 124.5, -36.0, -29.0], crs=ccrs.PlateCarree())

print("Looping through months")

# Add a single colorbar for the entire figure
cbar = fig.colorbar(cs, ax=axs, orientation='horizontal', fraction=0.02, pad=0.04, ticks=np.arange(-50, 51, 10))
precip_units = 'mm'
cbar.set_label(precip_units, labelpad=10)
print("Adding single colourbar")

# Save the figure
file_save = f"{mask}_{change}_change_{time}_{variable}.png"
output_path = os.path.join("dir_figs", file_save)
os.makedirs("dir_figs", exist_ok=True)

if os.path.exists(output_path):
    os.remove(output_path)
    print(f"Output file '{file_save}' has been deleted.")

plt.savefig(output_path, dpi=300)

print(f"Saving file as {output_path}")

# Display the plot
plt.show()

