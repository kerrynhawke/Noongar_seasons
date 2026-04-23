import xarray as xr
import os
import glob

# ============================
# Step 1: Set up directories
# ============================

base_dir = os.path.expanduser("~/Noongar_seasons/")
input_dir = "/pvol/AGCD/v1-0-3/precip/total/r005/01month/"
output_dir = os.path.join(base_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)

# Friendly label → (start_year, end_year, filename_label)
periods = {
    "early":  (1961, 1990, "1961_1990"),
    "recent": (1995, 2024, "1995_2024"),
}

# ============================
# Step 2: Monthly means
# ============================

def create_monthly_means(start_year, end_year, outfile):
    print(f"\n=== Monthly means for {start_year}–{end_year} ===")
    file_list = sorted(glob.glob(os.path.join(input_dir, "*.nc")))
    datasets = []

    for f in file_list:
        print(f"  Reading: {os.path.basename(f)}")
        ds = xr.open_dataset(f)
        ds_period = ds.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

        if ds_period.time.size == 0:
            print("    → No relevant data, skipping")
            ds.close()
            continue

        print(f"    → Adding {ds_period.time.size} timesteps")
        datasets.append(ds_period)
        ds.close()

    if not datasets:
        print("No data found for this period.")
        return

    combined = xr.concat(datasets, dim="time")
    monthly_means = combined.resample(time="1MS").mean()

    print(f"Saving monthly means → {outfile}")
    monthly_means.to_netcdf(outfile)

# ============================
# Step 3: Monthly climatology
# ============================

def create_monthly_climatology(start_year, end_year, outfile):
    print(f"\n=== Monthly climatology for {start_year}–{end_year} ===")
    file_list = sorted(glob.glob(os.path.join(input_dir, "*.nc")))
    datasets = []

    for f in file_list:
        print(f"  Reading: {os.path.basename(f)}")
        ds = xr.open_dataset(f)
        ds_period = ds.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

        if ds_period.time.size == 0:
            print("    → No relevant data, skipping")
            ds.close()
            continue

        print(f"    → Adding {ds_period.time.size} timesteps")
        datasets.append(ds_period)
        ds.close()

    if not datasets:
        print("No data found for this period.")
        return

    combined = xr.concat(datasets, dim="time")
    monclim = combined.groupby("time.month").mean("time")

    print(f"Saving climatology → {outfile}")
    monclim.to_netcdf(outfile)

# ============================
# Step 4: Run both for each period
# ============================

for label, (start, end, fname_label) in periods.items():

    # Monthly means
    outfile_means = os.path.join(output_dir, f"monthly_mean_{fname_label}.nc")
    create_monthly_means(start, end, outfile_means)

    # Monthly climatology
    outfile_clim = os.path.join(output_dir, f"monclim_{fname_label}.nc")
    create_monthly_climatology(start, end, outfile_clim)

