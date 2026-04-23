import xarray as xr
import os
import glob

## Step 1: Set up directories

base_dir = os.path.expanduser("~/Noongar_seasons/")
input_dir = "/pvol/AGCD/v1-0-3/precip/total/r005/01month/"
output_dir = os.path.join(base_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)

# set up labels → (start_year, end_year, filename_label)
periods = {
    "early":  (1961, 1990, "1961_1990"),
    "recent": (1995, 2024, "1995_2024"),
}

## Step 2: Create monthly means

def create_monthly_means_file_by_file(start_year, end_year, outfile):
    """Process raw AGCD files one at a time and compute monthly means."""

    print(f"\nProcessing period {start_year}–{end_year}")
    print(f"Output file will be: {outfile}")

    file_list = sorted(glob.glob(os.path.join(input_dir, "*.nc")))
    datasets = []

    print(f"Found {len(file_list)} input files")

    for f in file_list:
        print(f"  Reading file: {os.path.basename(f)}")
        ds = xr.open_dataset(f)

        # Select only the time range we need
        ds_period = ds.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))

        if ds_period.time.size == 0:
            print("    → No data in this file for selected period, skipping")
            ds.close()
            continue

        print(f"    → Adding {ds_period.time.size} timesteps")
        datasets.append(ds_period)
        ds.close()

    if len(datasets) == 0:
        print("No data found for this period. Skipping.")
        return

    print("Concatenating datasets…")
    combined = xr.concat(datasets, dim="time")

    print("Computing monthly means…")
    monthly_means = combined.resample(time="1MS").mean()

    print(f"Saving output to {outfile}")
    monthly_means.to_netcdf(outfile)

    print("Done.")

## Step 3: Run for each period

for label, (start, end, fname_label) in periods.items():
    outfile = os.path.join(output_dir, f"monthly_mean_{fname_label}.nc")
    create_monthly_means_file_by_file(start, end, outfile)
