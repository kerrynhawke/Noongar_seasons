import xarray as xr
import numpy as np

ds = xr.open_dataset("/pvol/AGCD/v1-0-3/precip/total/r005/01month/agcd_v1_precip_total_r005_monthly_2024.nc")

print("Lat shape:", ds.lat.shape)
print("Lon shape:", ds.lon.shape)

print("Lat spacing unique:", np.unique(np.diff(ds.lat.values)))
print("Lon spacing unique:", np.unique(np.diff(ds.lon.values)))

print("Lat ascending:", np.all(np.diff(ds.lat.values) > 0))
print("Lon ascending:", np.all(np.diff(ds.lon.values) > 0))
