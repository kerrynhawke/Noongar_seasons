import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os
from scipy import stats
import pandas as pd

# Define input and output directories and file names
input_dir = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper"
output_dir = "/data/Kerryn/My_Scripts/AGCD_Scripts/dir_figs"
anom_file = "masked_seasregionanom_1900-2022.nc"
file_path = os.path.join(input_dir, anom_file)

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load data from NetCDF file
print(f"Opening NetCDF file: {file_path}")
ds = xr.open_dataset(file_path)

# Identify the main variable
var_name = list(ds.data_vars)[0]
data = ds[var_name]

regional_mean = ds[var_name]

# Extract seasons and years
print("extracting seasons and years")
seasons = regional_mean['season'].values
season_years = ds.coords['season_year'].values

# Define the layout order with placeholders for blanks
print("defining layout order")
season_order = [
    "Summer (DJF)", "Birak (DJ)", "Bunuru (FM)",
    "Autumn (MAM)", "Djeran (AM)", None,
    "Winter (JJA)", "Makuru (JI)", None,
    "Spring (SON)", "Djilba (AS)", "Kambarang (ON)"
]

# Map display names to actual season names in the dataset
print("mapping display names")
season_mapping = {
    "Summer (DJF)": "Summer",
    "Birak (DJ)": "Birak",
    "Bunuru (FM)": "Bunuru",
    "Autumn (MAM)": "Autumn",
    "Djeran (AM)": "Djeran",
    "Winter (JJA)": "Winter",
    "Makuru (JI)": "Makuru",
    "Spring (SON)": "Spring",
    "Djilba (AS)": "Djilba",
    "Kambarang (ON)": "Kambarang"
}

# Create subplots
print("Creating 4x3 subplot grid")
fig, axes = plt.subplots(4, 3, figsize=(18, 16))
axes = axes.flatten()

# Loop through each season and plot
print("looping through each season and plot")
for i, label in enumerate(season_order):
    ax = axes[i]
    if label is None:
        ax.axis('off')
        continue

    season = season_mapping[label]
    print(f"Processing season: {season}")
    y = ds[var_name].sel(season=season).load().values
    x = season_years

    # Ensure 1D arrays
    print("making sure 1D arrays")
    y = np.ravel(y)
    x = np.ravel(x)

    # Create DataFrame for easier manipulation
    df = pd.DataFrame({'year': x, 'anomaly': y})
    df = df.dropna()

    # Add centered 10-year running mean
    print("adding 10-year centred running mean")
    df['running_mean'] = df['anomaly'].rolling(window=10, center=True).mean()

    # Linear regression
    print("linear regression")
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['year'], df['anomaly'])

    # Bar colors
    bar_colors = ['blue' if val >= 0 else 'red' for val in df['anomaly']]

    # Plot bars
    ax.bar(df['year'], df['anomaly'], color=bar_colors)

    # Plot running mean
    ax.plot(df['year'], df['running_mean'], color='black', linewidth=2, label='10-yr Running Mean')

    # Add horizontal line at y=0
    ax.axhline(0, color='gray', linewidth=1)

    # Set y-axis limits
    ax.set_ylim(-120, 220)

    # Add season label
    ax.text(0.03, 0.95, label, transform=ax.transAxes,
            fontsize=12, ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black'))

    # Add slope and p-value
    ax.text(0.98, 0.05, f"Slope: {slope:.2f}\nP-value: {p_value:.3f}",
            transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
            bbox=dict(facecolor='white', edgecolor='none'))

    # Set y-axis label only for leftmost plots
    if i % 3 == 0:
        ax.set_ylabel("Rainfall anomaly (mm)")

    # Remove x-axis label
    ax.set_xlabel("")

# Adjust layout
print("Finalizing layout")
plt.tight_layout()

# Save the figure
output_file = os.path.join(output_dir, "rainfall_anomaly_timeseries_seas_10yrunningmean.png")
print(f"Saving the figure to: {output_file}")
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()
print("Plot saved and figure closed.")

