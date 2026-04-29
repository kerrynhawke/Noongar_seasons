import xarray as xr
import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------
# Directories (UPDATED AS REQUESTED)
# ---------------------------------------------------------
input_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/outputs"
output_dir = "/mnt/d/Kerryn/projects_Kerryn/Noongar_seasons/tables"
os.makedirs(output_dir, exist_ok=True)

excel_out = os.path.join(output_dir, "precip_change_summary.xlsx")

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
# Helper: compute spatial stats
# ---------------------------------------------------------
def spatial_stats(arr):
    flat = arr.flatten()
    flat = flat[~np.isnan(flat)]
    if len(flat) == 0:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

    spatial_mean = flat.mean()
    q25, q50, q75 = np.percentile(flat, [25, 50, 75])
    return spatial_mean, flat.min(), flat.max(), q50, q75 - q25, flat.std()


# ---------------------------------------------------------
# Helper: detect time dimension
# ---------------------------------------------------------
def detect_time_dim(ds):
    for dim in ["month", "season", "time"]:
        if dim in ds.dims:
            return dim
    raise ValueError("No valid time dimension found (expected month/season/time).")


# ---------------------------------------------------------
# Main processor
# ---------------------------------------------------------
def process_file(precip_file, sig_file, is_monthly=True):
    print(f"\nProcessing: {precip_file}")

    ds_precip = xr.open_dataset(os.path.join(input_dir, precip_file))
    ds_sig = xr.open_dataset(os.path.join(input_dir, sig_file))

    precip_var = list(ds_precip.data_vars)[0]
    sig_var = list(ds_sig.data_vars)[0]

    precip = ds_precip[precip_var]
    sig = ds_sig[sig_var]

    precip_dim = detect_time_dim(precip)
    sig_dim = detect_time_dim(sig)

    rows = []

    # ---------------------------------------------------------
    # MONTHLY CASE
    # ---------------------------------------------------------
    if is_monthly:
        for i, month in enumerate(MONTH_NAMES, start=1):
            p = precip.sel({precip_dim: i})
            s = sig.sel({sig_dim: i})

            mean_val = float(p.mean(dim=["lat", "lon"], skipna=True).values)
            sig_fraction = float((s > 0).sum() / s.size)

            direction = "Increase" if mean_val > 0 else "Decrease" if mean_val < 0 else "No change"

            spatial_mean, mn, mx, med, iqr, sd = spatial_stats(p.values)

            rows.append({
                "Period": month,
                "Mean change": mean_val,
                "Spatial mean": spatial_mean,
                "Direction": direction,
                "Fraction significant": sig_fraction,
                "Percent significant": sig_fraction * 100,
                "Min": mn,
                "Max": mx,
                "Median": med,
                "IQR": iqr,
                "Std dev": sd
            })

        return pd.DataFrame(rows)

    # ---------------------------------------------------------
    # SEASONAL CASE (10 seasons)
    # ---------------------------------------------------------

    season_labels = list(sig[sig_dim].values)

    for season in season_labels:
        months = SEASON_DEFINITIONS[season]

        p = precip.sel({precip_dim: months}).mean(dim=precip_dim)
        s = sig.sel({sig_dim: season})

        mean_val = float(p.mean(dim=["lat", "lon"], skipna=True).values)
        sig_fraction = float((s > 0).sum() / s.size)

        direction = "Increase" if mean_val > 0 else "Decrease" if mean_val < 0 else "No change"

        spatial_mean, mn, mx, med, iqr, sd = spatial_stats(p.values)

        rows.append({
            "Period": season,
            "Mean change": mean_val,
            "Spatial mean": spatial_mean,
            "Direction": direction,
            "Fraction significant": sig_fraction,
            "Percent significant": sig_fraction * 100,
            "Min": mn,
            "Max": mx,
            "Median": med,
            "IQR": iqr,
            "Std dev": sd
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# Build all four tables
# ---------------------------------------------------------
abs_monthly = process_file(
    "masked_abs_change_1993_2022_minus_1961_1990.nc",
    "mask_abs_month_significance_masked.nc",
    is_monthly=True
)

prop_monthly = process_file(
    "masked_prop_change_1993_2022_minus_1961_1990.nc",
    "mask_prop_month_significance_masked.nc",
    is_monthly=True
)

abs_seasonal = process_file(
    "masked_abs_change_1993_2022_minus_1961_1990.nc",
    "mask_abs_season_significance_masked.nc",
    is_monthly=False
)

prop_seasonal = process_file(
    "masked_prop_change_1993_2022_minus_1961_1990.nc",
    "mask_prop_season_significance_masked.nc",
    is_monthly=False
)

# ---------------------------------------------------------
# Save combined Excel workbook
# ---------------------------------------------------------
with pd.ExcelWriter(excel_out) as writer:
    abs_monthly.to_excel(writer, sheet_name="abs_monthly", index=False)
    prop_monthly.to_excel(writer, sheet_name="prop_monthly", index=False)
    abs_seasonal.to_excel(writer, sheet_name="abs_seasonal", index=False)
    prop_seasonal.to_excel(writer, sheet_name="prop_seasonal", index=False)

print("\nSaved combined Excel workbook:")
print(excel_out)
