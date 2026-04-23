import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os
from scipy import stats
import pandas as pd

# Define input and output directories and file names
input_dir = "/data2/Kerryn/AGCD_Clim_Sarah_Sapsford_Paper"
output_dir = "/data/Kerryn/My_Scripts/AGCD_Scripts/dir_figs"
anom_file = "masked_mthregionanom_1900-2022.nc"
file_path = os.path.join(input_dir, anom_file)

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load data from NetCDF file
print(f"Opening NetCDF file: {file_path}")
ds = xr.open_dataset(file_path)

# Extract time and anomaly data
print("Extracting 'time' and 'monthly_anomaly' variables")
time = pd.to_datetime(ds['time'].values)
monthly_anomaly = ds['monthly_anomaly'].values

# Define month labels starting with December
month_abbrs = ["DEC", "JAN", "FEB", "MAR", "APR", "MAY",
               "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]

# Create subplots
print("Creating 4x3 subplot grid")
fig, axes = plt.subplots(4, 3, figsize=(18, 16))
axes = axes.flatten()

# Loop through each month and plot
for i, month_abbr in enumerate(month_abbrs):
    print(f"Processing month: {month_abbr}")
    ax = axes[i]
    month_index = (i + 11) % 12

    #filter data for correct month
    mask = time.month == (month_index + 1)
    month_years = time[mask].year
    month_anomalies = monthly_anomaly[mask]

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(month_years, month_anomalies)

    # Bar colors
    bar_colors = ['blue' if val >= 0 else 'red' for val in month_anomalies]

    # Plot bars
    ax.bar(month_years, month_anomalies, color=bar_colors)

    # Add centered 10-year running mean line (5 years before and 5 years after)
    centered_mean = []
    centered_years = []
    for j in range(5, len(month_anomalies) - 5):
        window_mean = np.mean(month_anomalies[j - 5:j + 6])
        centered_mean.append(window_mean)
        centered_years.append(month_years[j])
    ax.plot(centered_years, centered_mean, color='black', linewidth=2, label='10-yr Running Mean')

    # Add horizontal line at y=0
    ax.axhline(0, color='gray', linewidth=1)

    # Set y-axis limits
    ax.set_ylim(-120, 120)

    # Add month label at y=0.95
    ax.text(0.03, 0.95, month_abbr, transform=ax.transAxes,
            fontsize=12, ha='left', va='top', bbox=dict(facecolor='white', edgecolor='black'))

    # Add slope and p-value at y=0.05
    ax.text(0.98, 0.05, f"Slope: {slope:.2f}\nP-value: {p_value:.3f}",
            transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
            bbox=dict(facecolor='white', edgecolor='none'))

    # Set y-axis label only for leftmost plots
    if i % 3 == 0:
        ax.set_ylabel("Rainfall anomaly (mm)")

    # Remove x-axis label
    ax.set_xlabel("")

# Hide unused subplots
for j in range(len(month_abbrs), len(axes)):
    fig.delaxes(axes[j])

# Adjust layout
print("Finalizing layout")
plt.tight_layout()

# Save the figure
output_file = os.path.join(output_dir, "rainfall_anomaly_timeseries_months_10yrunningmean.png")
print(f"Saving the figure to: {output_file}")
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()
print("Plot saved and figure closed.")

# Display the plot
plt.show()
