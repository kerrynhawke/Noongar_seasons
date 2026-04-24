# Indigenous versus conventional seasons analysis documentation:

## Data preparation and creation of monthly climatology and means files

### 1. Create Noongar region mask .nc file from shape file 

- Script: /Noongar_seasons/scripts/0a_create_mask.py
- Original Shapefile: /Noongar_seasons/boundaries/Noongarborder.shp 
- Merged Shapefile (used in calculations*): /Noongar_seasons/boundaries/Noongarborder_merged.shp 
- Output mask file: /Noongar_seasons/outputs/mask_merged.nc 

Note: the original shape file was obtained from Sarah Sapsford and merged in ArcGIS by Kerryn Hawke into a single polygon over the land (retaining island polygons) lsbefore converting into NetCDF format. This was done as the original had many polygons which resulted in erroneous null values within the region in the NetCDF file. 

### 2. Create monthly climatologies 

- Script: /Noongar_seasons/scripts/calc_masked_monthly_climatology.py 
- Input files: /data2/AGCD/v2-0-1/precip/total/r001/01month/ (AGCD downloaded files)
- Mask file: /Noongar_seasons/boundaries/Noongarborder_merged.shp (created in 1 above)
- Output masked climatology file 1: /Noongar_seasons/output/masked_monclim_from_1961_1990.nc 
- Output masked climatology file 2: /Noongar_seasons/output/masked_monclim_from_1993_2022.nc

### 3. Calculate monthly means 

- Script: /Noongar_seasons/scripts/calc_masked_monthly_means.py 
- Input files: /data2/AGCD/v2-0-1/precip/total/r001/01month/ (AGCD downloaded files)
- Mask file: /Noongar_seasons/boundaries/Noongarborder_merged.shp (created in 1 above)
- Output masked monthly mean file 1: /Noongar_seasons/output/masked_mthmeans_1900_2022.nc 
- Output masked monthly mean file 2: /Noongar_seasons/output/masked_mthmeans_1961_1990.nc
- Output masked monthly mean file 3: /Noongar_seasons/output/masked_mthmeans_1993_2022.nc 

## Figure 3. Monthly mean rainfall climatologies ADD

Workflow for the creation of a figure depicting 


## Figure 4. Absolute change in monthly rainfall 

Workflow for the creation of a figure depicting absolute change in rainfall for each month, 1993-2022 compared to 1961-1990 with significance stippling (significance mask P < 0.05, using the Mann-Whitney U test).

### 4. Calculate absolute change in rainfall between 1961-1990 and 1993-2022 

Calculation: absolute_change = monthly_means_1993_2022 - monthly_means_1961_1990 

- Script: /Noongar_seasons/scripts/calc_masked_abs_prop_rain_change.py 
- Input climatology file 1: /Noongar_seasons/outpt/masked_monclim_from_1961_1990.nc (created in 2 above)
- Input climatology file 2: /Noongar_seasons/output/masked_monclim_from_1993_2022.nc (created in 2 above)
- Input masked monthly mean file 2: /Noongar_seasons/output/masked_mthmeans_1961_1990.nc (created in 3 above)
- Input masked monthly mean file 3: /Noongar_seasons/output/masked_mthmeans_1993_2022.nc (created in 3 above)
- Output absolute change file: /Noongar_seasons/output/masked_abs_change_1993_2022_minus_1961_1990.nc 


### 5. Calculate significance for monthly absolute change in rainfall between 1961-1990 and 1993-2022

Test: Mann-Whitney U test, where P < 0.05

- Script: /Noongar_seasons/scripts/calc_masked_abs_sig_month_mask.py
- Input masked monthly mean file 2: /Noongar_seasons/output/masked_mthmeans_1961_1990.nc (created in 3 above)
- Input masked monthly mean file 3: /Noongar_seasons/output/masked_mthmeans_1993_2022.nc (created in 3 above)
- Mask file: /Noongar_seasons/boundaries/Noongarborder_merged.shp (created in 1 above)
- Output masked monthly absolute change significance mask file: /Noongar_seasons/output/mask_abs_month_significance_masked.nc


### 6. Create absolute change in monthly rainfall plot
3x4 plot showing spatial absolute change in monthly rainfall across Noongar region (-50 mm to +50 mm) with significance stippling (P = 0.05)

- Script: /Noongar_seasons/scripts/plot_abs_month_rain_panel.py
- Input absolute change file: /Noongar_seasons/outputs/masked_abs_change_1993_2022_minus_1961_1990.nc (created in 4 above)
- Input masked monthly absolute change significance mask file: /Noongar_seasons/outputs/mask_abs_month_significance_masked.nc (created in 5 above)
 - Output plot: /Noongar_seasons/figs/mask_abs_sig_change_month_rain_sig.png


## Figure 4. Proportional change in monthly rainfall

Workflow for the creation of a figure depicting proportional change in rainfall for each month, 1993-2022 compared to 1961-1990 with significance stippling (significance mask P < 0.05, using the Mann-Whitney U test).

### 7. Calculate proportional change in rainfall between 1961-1990 and 1993-2022

Calculation: proportional_change = absolute_change / monthly_means_1961_1990  
- Script: /Noongar_seasons/scripts/calc_masked_abs_prop_rain_change.py
- Input climatology file 1: /Noongar_seasons/outputs/monclim_from_1961_1990.nc (created in 2 above)
- Input climatology file 2: /Noongar_seasons/outputs/monclim_from_1993_2022.nc (created in 2 above)
- Input monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (created in 3 above)
- Input monthly mean file 3: /Noongar_seasons/outputs/masked_mthmeans_1993_2022.nc (created in 3 above)
- Output proportional change file: /Noongar_seasons/outputs/masked_prop_change_1993_2022_minus_1961_1990.nc


### 8. Calculate significance for monthly proportional change in rainfall between 1961-1990 and 1993-2022

Test: Mann-Whitney U test, where P < 0.05

- Script: /Noongar_seasons/scripts/calc_masked_prop_sig_month_mask.py 
- Input masked monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (created in 3 above)
- Input masked monthly mean file 3: /Noongar_seasons/outputs/masked_mthmeans_1993_2022.nc (created in 3 above)
- Mask file: /Noongar_seasons/boundaries/Noongarborder_merged.shp (created in 1 above)
- Output masked monthly proportional change significance mask file: /Noongar_seasons/outputs/mask_abs_month_significance_masked.nc


### 9. Create proportional change in monthly rainfall plot
3x4 plot showing spatial proportional change in monthly rainfall across Noongar region (-50 mm to +50 mm) with significance stippling (P = 0.05)

- Script: /data/Kerryn/AGCD_Scripts/plot_abs_month_rain_panel.py
- Input proportional change file: /Noongar_seasons/outputs/masked_prop_change_1993_2022_minus_1961_1990.nc (created in 7 above)
- Input masked monthly proportional change significance mask file: /Noongar_seasons/outputs/mask_abs_month_significance_masked.nc (created in 8 above)
- Output plot: /Noongar_seasons/figs/mask_prop_sig_change_month_rain.png


## Figure 5. Absolute change in seasonal rainfall

Workflow for the creation of a figure depicting absolute change in seasonal rainfall (mm) between 1961-1990 and 1993-2022. The Noongar six-season calendar includes Birak (first summer, Debember-January), Bunuru (second summer, February-March), Djeran (autumn, April-May), Makuru (winter, June-July), Djilba (first spring, August-September) and Kambarang (second spring, October-November). The four-season calendar includes summer (December-February), autumn (March-May), winter (June-August) and spring (September-November). Significance stippling (significance mask P < 0.05, using the Mann-Whitney U test).

### 10. Calculate absolute change in rainfall between 1961-1990 and 1993-2022

Calculation: absolute_change = monthly_means_1993_2022 - monthly_means_1961_1990

- Script: /data/Kerryn/AGCD_Scripts/calc_masked_abs_prop_rain_change.py
- Input climatology file 1: /Noongar_seasons/outputs/monclim_from_1961_1990.nc (created in 2 above)
- Input climatology file 2: /Noongar_seasons/outputs/monclim_from_1993_2022.nc (created in 2 above)
- Input monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (created in 3 above)
- Input monthly mean file 3: /Noongar_seasons/outputs/masked_mthmeans_1993_2022.nc (created in 2 above)
- Output absolute change file: /Noongar_seasons/outputs/masked_abs_change_1993_2022_minus_1961_1990.nc


### 11. Calculate significance for seasonal absolute change in rainfall between 1961-1990 and 1993-2022

Test: Mann-Whitney U test, where P < 0.05

- Script: /data/Kerryn/AGCD_Scripts/calc_masked_abs_sig_seas_mask.py
- Input masked monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (created in Step 3)
- Input masked monthly mean file 3: /Noongar_seasons/outputs/masked_mthmeans_1993_2022.nc (created in Step 3)
- Mask file: /Noongar_seasons/outputs/mask_merged.nc (created in Step 1)
- Output masked seasonal absolute change significance mask file: /Noongar_seasons/outputs/mask_abs_season_significance_masked.nc


### 12. Create absolute change in seasonal rainfall plot
3x4 plot showing spatial absolute change in seasonal rainfall across Noongar region (-1 % to +1 %) with significance stippling (P = 0.05)

- Script: /data/Kerryn/AGCD_Scripts/plot_abs_seas_rain_panel.py 
- Input absolute change file: /Noongar_seasons/outputs/masked_abs_change_1993_2022_minus_1961_1990.nc (created in 10 above)
- Input masked seasonal absolute change significance mask file: /Noongar_seasons/outputs/mask_abs_season_significance_masked.nc (created in 11 above)
- Output plot: Noongar_seasons/figs/mask_abs_sig_change_seas_rain.png



## Figure 6. Proportional change in seasonal rainfall

Workflow for the creation of a figure depicting proportional change in seasonal rainfall (mm) between 1961-1990 and 1993-2022. The Noongar six-season calendar includes Birak (first summer, Debember-January), Bunuru (second summer, February-March), Djeran (autumn, April-May), Makuru (winter, June-July), Djilba (first spring, August-September) and Kambarang (second spring, October-November). The four-season calendar includes summer (December-February), autumn (March-May), winter (June-August) and spring (September-November). Significance stippling (significance mask P < 0.05, using the Mann-Whitney U test).


### 13. Calculate proportional change in rainfall between 1961-1990 and 1993-2022

Calculation: proportional_change = absolute_change / monthly_means_1961_1990

- Script: /data/Kerryn/AGCD_Scripts/calc_masked_abs_prop_rain_change.py
- Input climatology file 1: /Noongar_seasons/outputs/monclim_from_1961_1990.nc (created in 2 above)
- Input climatology file 2: /Noongar_seasons/outputs/monclim_from_1993_2022.nc (created in 2 above)
- Input monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (created in 3 above)
- Input monthly mean file 3: /Noongar_seasons/outputs/masked_mthmeans_1993_2022.nc (created in 3 above)
- Output proportional change file: /Noongar_seasons/outputs/masked_prop_change_1993_2022_minus_1961_1990.nc


### 14. Calculate significance for seasonal proportional change in rainfall between 1961-1990 and 1993-2022

Test: Mann-Whitney U test, where P < 0.05

- Script: /data/Kerryn/AGCD_Scripts/calc_masked_prop_sig_seas_mask_s2.py 
- Input masked monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (created in Step 3)
- Input masked monthly mean file 3: /Noongar_seasons/outputs/masked_mthmeans_1993_2022.nc (created in Step 3)
- Mask file: /Noongar_seasons/outputs/mask_merged.nc (created in Step 1)
- Output masked seasonal proportional change significance mask file: /Noongar_seasons/outputs/mask_prop_season_significance_masked.nc


### 15. Create proportional change in seasonal rainfall plot
3x4 plot showing spatial proportional change in seasonal rainfall across Noongar region (-1 % to +1 %) with significance stippling (P = 0.05)

- Script: /data/Kerryn/AGCD_Scripts/plot_prop_seas_rain_panel.py 
- Input proportional change file: /Noongar_seasons/outputs/masked_prop_change_1993_2022_minus_1961_1990.nc (created in 13 above)
- Input masked seasonal proportional change significance mask file: /Noongar_seasons/outputs/mask_prop_season_significance_masked.nc (created in 14 above)
- Output plot: Noongar_seasons/figs/mask_prop_sig_change_month_rain.png


## Figure 7. Monthly rainfall anomalies
Workflow for the creation of a figure depicting monthly rainfall anomalies (mm) 1900-2022 compared to 1961-1990 climatology, with 10-year centred running mean.

### 16. calculate monthly rainfall anomalies, 1900-2022
- Input masked monthly mean file 1: /Noongar_seasons/outputs/masked_mthmeans_1900_2022.nc (calculated in 3 above)
- Input masked monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (calculated in 3 above)
- Output masked monthly anomalies file: Noongar_seasons/outputs/masked_mthregionanom_1900-2022.nc


### 17. Create monthly rainfall anomaly timeseries
3x4 monthly timeseries panel plot, 1900-2022 monthly rainfall anomaly (-100 mm to +100 mm) with 10-year centred running mean

- Script: /data/Kerryn/AGCD_Scripts/plot_anomalies_month_rain_region.py 
- Input file: /Noongar_seasons/outputs/masked_mthregionanom_1900-2022.nc (created in 16 above)
- Output plot: Noongar_seasons/figs/rainfall_anomaly_timeseries_months_10yrunningmean.png

## Figure 8. Seasonal rainfall anomalies - CHECK
Workflow for the creation of a figure depicting seasonal rainfall anomalies (mm) 1900-2022 compared to 1961-1990 climatology, with 10-year centred running mean. The Noongar six-season calendar includes Birak (first summer, December-January), Bunuru (second summer, February-March), Djeran (autumn, April-May), Makuru (winter, June-July), Djilba (first spring, August-September) and Kambarang (second spring, October-November). The four-season calendar includes summer (December-February), autumn (March-May), winter (June-August) and spring (September-November).

### 18. calculate seasonal rainfall anomalies, 1900-2022
- Input masked monthly mean file 1: /Noongar_seasons/outputs/masked_mthmeans_1900_2022.nc (calculated in 3 above)
- Input masked monthly mean file 2: /Noongar_seasons/outputs/masked_mthmeans_1961_1990.nc (calculated in 3 above)
- Output masked monthly anomalies file: Noongar_seasons/outputs/masked_mthregionanom_1900-2022.nc


### 19. Create monthly rainfall anomaly timeseries
3x4 seasonal timeseries panel plot, 1900-2022 monthly rainfall anomaly (-100 mm to +100 mm) with 10-year centred running mean

- Script: /data/Kerryn/AGCD_Scripts/plot_anomalies_month_rain_region.py 
- Input file: /Noongar_seasons/outputs/masked_mthregionanom_1900-2022.nc (created in 16 above)
- Output plot: Noongar_seasons/figs/rainfall_anomaly_timeseries_months_10yrunningmean.png