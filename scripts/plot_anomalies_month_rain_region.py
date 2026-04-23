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
anom_file = "masked_mthregionanom_1900-2022.nc"
file_path = os.path.join(input_dir, anom_file)

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------
print(f"Opening NetCDF file: {file_path}")
ds = xr.open_dataset(file_path)

print("Extracting 'time' and 'monthly_anomaly' variables")
time = pd.to_datetime(ds['time'].values)
monthly_anomaly = ds['monthly_anomaly'].values

# ---------------------------------------------------------
# Month labels (starting with December)
# ---------------------------------------------------------
month_abbrs = ["DEC", "JAN", "FEB", "MAR", "APR", "MAY",
               "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]

# ---------------------------------------------------------
# Create subplot grid
# ---------------------------------------------------------
print("Creating 4x3 subplot grid")
fig, axes = plt.subplots(4, 3, figsize=(18, 16))
axes = axes.flatten()

# ---------------------------------------------------------
# Loop through each month and plot
# ---------------------------------------------------------
for i, month_abbr in enumerate(month_abbrs):
    print(f"Processing month: {month_abbr}")
    ax = axes[i]

    # Reorder so DEC is first
    month_index = (i + 11) % 12

    # Filter data for correct month
    mask = time.month == (month_index + 1)
    month_years = time[mask].year
    month_anomalies = monthly_anomaly[mask]

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(month_years, month_anomalies)

    # Bar colours
    bar_colors = ['blue' if val >= 0 else 'red' for val in month_anomalies]

    # Plot bars
    ax.bar(month_years, month_anomalies, color=bar_colors)

    # 10-year centred running mean
    centered_mean = []
    centered_years = []
    for j in range(5, len(month_anomalies) - 5):
        window_mean = np.mean(month_anomalies[j - 5:j + 6])
        centered_mean.append(window_mean)
        centered_years.append(month_years[j])
    ax.plot(centered_years, centered_mean, color='black', linewidth=2)

    # Horizontal zero line
    ax.axhline(0, color='gray', linewidth=1)

    # Y-axis limits
    ax.set_ylim(-120, 120)

    # ---------------------------------------------------------
    # Month label (top-right, no box)
    # ---------------------------------------------------------
    ax.text(
        0.98, 0.98, month_abbr,
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

    # Remove x-axis label
    ax.set_xlabel("")

# ---------------------------------------------------------
# Hide unused subplots
# ---------------------------------------------------------
for j in range(len(month_abbrs), len(axes)):
    fig.delaxes(axes[j])

# ---------------------------------------------------------
# Final layout
# ---------------------------------------------------------
print("Finalizing layout")
plt.tight_layout()

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------
output_file = os.path.join(output_dir, "rainfall_anomaly_timeseries_months_10yrunningmean.png")
print(f"Saving the figure to: {output_file}")
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print("Plot saved and figure closed.")
plt.show()
