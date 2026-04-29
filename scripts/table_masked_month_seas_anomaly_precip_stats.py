import xarray as xr
import numpy as np
import pandas as pd
from scipy import stats
import os

# ---------------------------------------------------------
# Directories (UPDATED AS REQUESTED)
# ---------------------------------------------------------
input_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/outputs"
output_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/tables"
os.makedirs(output_dir, exist_ok=True)

excel_out = os.path.join(output_dir, "precip_anomaly_summary.xlsx")

# ---------------------------------------------------------
# Define ALL seasons (10 total)
# ---------------------------------------------------------
SEASON_DEFINITIONS = {
    'Summer':     [12, 1, 2],
    'Autumn':     [3, 4, 5],
    'Winter':     [6, 7, 8],
    'Spring':     [9, 10, 11],
    'Birak':      [12, 1],
    'Bunuru':     [2, 3],
    'Djeran':     [4, 5],
    'Makuru':     [6, 7],
    'Djilba':     [8, 9],
    'Kambarang':  [10, 11]
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------
anom_file = "masked_mthregionanom_1900-2022.nc"
file_path = os.path.join(input_dir, anom_file)

print(f"Opening NetCDF file: {file_path}")
ds = xr.open_dataset(file_path)

time = pd.to_datetime(ds["time"].values)
anom = ds["monthly_anomaly"].values

# ---------------------------------------------------------
# Trend classification helper
# ---------------------------------------------------------
def classify_trend(slope):
    if slope > 0.2:
        return "Strong increase"
    elif 0.05 < slope <= 0.2:
        return "Weak increase"
    elif -0.05 <= slope <= 0.05:
        return "No trend"
    elif -0.2 <= slope < -0.05:
        return "Weak decrease"
    else:
        return "Strong decrease"

# ---------------------------------------------------------
# Compute stats for a 1D anomaly series
# ---------------------------------------------------------
def compute_stats(years, values):
    # Sen slope
    sen_slope, sen_intercept, lower, upper = stats.theilslopes(values, years)

    # p-value from OLS
    _, _, _, p_value, _ = stats.linregress(years, values)

    # Basic stats
    mean_val = np.mean(values)
    sd_val = np.std(values)
    mn = np.min(values)
    mx = np.max(values)
    med = np.median(values)
    q25, q75 = np.percentile(values, [25, 75])
    iqr = q75 - q25

    # Counts
    n_pos = np.sum(values > 0)
    n_neg = np.sum(values < 0)

    # Trend classification
    trend_class = classify_trend(sen_slope)

    # Significance flag
    sig_flag = "Significant" if p_value < 0.05 else "Not significant"

    return {
        "Sen slope (mm/yr)": sen_slope,
        "P-value": p_value,
        "Significance": sig_flag,
        "Trend classification": trend_class,
        "Mean anomaly": mean_val,
        "Std dev": sd_val,
        "Min anomaly": mn,
        "Max anomaly": mx,
        "Median": med,
        "IQR": iqr,
        "N positive anomalies": n_pos,
        "N negative anomalies": n_neg
    }

# ---------------------------------------------------------
# MONTHLY STATISTICS
# ---------------------------------------------------------
monthly_rows = []

for i, month_name in enumerate(MONTH_NAMES):
    month_index = i + 1

    mask = time.month == month_index
    years = time[mask].year
    values = anom[mask]

    stats_dict = compute_stats(years, values)
    stats_dict["Month"] = month_name
    monthly_rows.append(stats_dict)

monthly_df = pd.DataFrame(monthly_rows)
monthly_df = monthly_df[["Month"] + [c for c in monthly_df.columns if c != "Month"]]

# ---------------------------------------------------------
# BOM SEASONAL STATISTICS
# ---------------------------------------------------------
bom_seasons = ["Summer", "Autumn", "Winter", "Spring"]
bom_rows = []

for season in bom_seasons:
    months = SEASON_DEFINITIONS[season]
    mask = np.isin(time.month, months)
    years = time[mask].year
    values = anom[mask]

    stats_dict = compute_stats(years, values)
    stats_dict["Season"] = season
    bom_rows.append(stats_dict)

bom_df = pd.DataFrame(bom_rows)
bom_df = bom_df[["Season"] + [c for c in bom_df.columns if c != "Season"]]

# ---------------------------------------------------------
# NOONGAR SEASONAL STATISTICS
# ---------------------------------------------------------
noongar_seasons = ["Birak", "Bunuru", "Djeran", "Makuru", "Djilba", "Kambarang"]
noongar_rows = []

for season in noongar_seasons:
    months = SEASON_DEFINITIONS[season]
    mask = np.isin(time.month, months)
    years = time[mask].year
    values = anom[mask]

    stats_dict = compute_stats(years, values)
    stats_dict["Season"] = season
    noongar_rows.append(stats_dict)

noongar_df = pd.DataFrame(noongar_rows)
noongar_df = noongar_df[["Season"] + [c for c in noongar_df.columns if c != "Season"]]

# ---------------------------------------------------------
# Save to Excel (three tabs)
# ---------------------------------------------------------
with pd.ExcelWriter(excel_out) as writer:
    monthly_df.to_excel(writer, sheet_name="Monthly_Stats", index=False)
    bom_df.to_excel(writer, sheet_name="BOM_Season_Stats", index=False)
    noongar_df.to_excel(writer, sheet_name="Noongar_Season_Stats", index=False)

print(f"\nSaved statistics table to:\n{excel_out}")
