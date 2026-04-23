import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os
from scipy import stats
import pandas as pd

# ---------------------------------------------------------
# Define input/output directories and file names
# ---------------------------------------------------------
input_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/outputs"
output_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/figs"
anom_file = "masked_seasregionanom_1900-2022.nc"
file_path = os.path.join(input_dir, anom_file)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------
print(f"Opening NetCDF file: {file_path}")
ds = xr.open_dataset(file_path)

# Identify main variable
var_name = list(ds.data_vars)[0]
regional_mean = ds[var_name]

# Extract seasons and years
print("Extracting seasons and years")
seasons = regional_mean['season'].values
season_years = ds.coords['season_year'].values

# ---------------------------------------------------------
# Define layout order (with blanks)
# ---------------------------------------------------------
season_order = [
    "Summer (DJF)", "Birak (DJ)", "Bunuru (FM)",
    "Autumn (MAM)", "Djeran (AM)", None,
    "Winter (JJA)", "Makuru (JI)", None,
    "Spring (SON)", "Djilba (AS)", "Kambarang (ON)"
]

# Map display names to dataset season names
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

# ---------------------------------------------------------
# Create subplot grid
# ---------------------------------------------------------
print("Creating 4x3 subplot grid")
fig, axes = plt.subplots(4, 3, figsize=(18, 16))
axes = axes.flatten()

# ---------------------------------------------------------
# Loop through each season and plot
# ---------------------------------------------------------
print("Looping through each season and plotting")
for i, label in enumerate(season_order):
    ax = axes[i]

    if label is None:
        ax.axis("off")
        continue

    season = season_mapping[label]
    print(f"Processing season: {season}")

    y = ds[var_name].sel(season=season).load().values
    x = season_years

    # Ensure 1D arrays
    y = np.ravel(y)
    x = np.ravel(x)

    # Build DataFrame
    df = pd.DataFrame({'year': x, 'anomaly': y}).dropna()

    # 10-year centred running mean
    df['running_mean'] = df['anomaly'].rolling(window=10, center=True).mean()

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['year'], df['anomaly'])

    # Bar colours
    bar_colors = ['blue' if val >= 0 else 'red' for val in df['anomaly']]

    # Plot bars
    ax.bar(df['year'], df['anomaly'], color=bar_colors)

    # Running mean
    ax.plot(df['year'], df['running_mean'], color='black', linewidth=2)

    # Zero line
    ax.axhline(0, color='gray', linewidth=1)

    # Y-axis limits
    ax.set_ylim(-120, 220)

    # ---------------------------------------------------------
    # Season label (top-right, no box)
    # ---------------------------------------------------------
    ax.text(
        0.98, 0.98, label,
        transform=ax.transAxes,
        fontsize=12,
        ha='right', va='top'
    )

    # Slope + p-value (bottom-right, keep box)
    ax.text(
        0.98, 0.05,
        f"Slope: {slope:.2f}\nP-value: {p_value:.3f}",
        transform=ax.transAxes,
        fontsize=10,
        ha='right', va='bottom',
        bbox=dict(facecolor='white', edgecolor='none')
    )

    # Y-axis label only for left column
    if i % 3 == 0:
        ax.set_ylabel("Rainfall anomaly (mm)")

    ax.set_xlabel("")

# ---------------------------------------------------------
# Final layout
# ---------------------------------------------------------
print("Finalizing layout")
plt.tight_layout()

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------
output_file = os.path.join(output_dir, "rainfall_anomaly_timeseries_seas_10yrunningmean.png")
print(f"Saving the figure to: {output_file}")
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print("Plot saved and figure closed.")
