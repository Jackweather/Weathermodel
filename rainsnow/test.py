import os
import requests
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime
from PIL import Image

# Folder paths for GRIB data and image outputs
base_folder = "./public"
grib_folder = os.path.join(base_folder, "grib")  # Folder for GRIB data
grib_folder_temp = os.path.join(grib_folder, "temp")  # Folder for temperature GRIB files
grib_folder_refc = os.path.join(grib_folder, "refc")  # Folder for reflectivity GRIB files
rs_folder = os.path.join(base_folder, "RS")  # Use "RS" folder instead of "images"
os.makedirs(grib_folder_temp, exist_ok=True)
os.makedirs(grib_folder_refc, exist_ok=True)
os.makedirs(rs_folder, exist_ok=True)  # Ensure the "RS" folder exists

# Get today's date and format it for the URL
today = datetime.now()
date_str = today.strftime("%Y%m%d")

# Determine the most recent GFS run based on the current hour
current_hour = today.hour
hour_str = f"{(current_hour // 6) * 6:02d}"  # Get the latest run in 6-hour intervals

# Forecast steps limited to f000 to f012 and then every 6 hours up to f096
forecast_steps = [f"f{str(i).zfill(3)}" for i in range(13)]  # Generates ['f000', ..., 'f012']
forecast_steps += [f"f{str(i).zfill(3)}" for i in range(12, 97, 6)]  # Adds ['f018', ..., 'f096']

# Variables to download
variable_temp = "TMP"  # Temperature
variable_refc = "REFC"  # Reflectivity

# Function to check if the file exists on the server
def file_exists(url):
    response = requests.head(url)
    return response.status_code == 200

# Try the most recent GFS run and fall back if necessary
run_found = False
for hour in [hour_str, f"{(int(hour_str) - 6) % 24:02d}"]:  # Try current and past run
    for step in forecast_steps:
        # Build the URL with the specified variables for both temperature and reflectivity
        url_temp = (f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.{date_str}%2F{hour}%2Fatmos"
                    f"&file=gfs.t{hour}z.pgrb2.0p25.{step}&var_{variable_temp}=on&lev_2_m_above_ground=on")
        url_refc = (f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.{date_str}%2F{hour}%2Fatmos"
                    f"&file=gfs.t{hour}z.pgrb2.0p25.{step}&var_{variable_refc}=on&lev_entire_atmosphere=on")

        # Check if the temperature and reflectivity files exist
        if file_exists(url_temp) and file_exists(url_refc):
            filename_temp = os.path.join(grib_folder_temp, f"gfs.t{hour}z.pgrb2.0p25.{step}.grib2")
            filename_refc = os.path.join(grib_folder_refc, f"gfs.t{hour}z.pgrb2.0p25.{step}.grib2")

            # Download the files
            response_temp = requests.get(url_temp)
            response_refc = requests.get(url_refc)
            if response_temp.status_code == 200 and response_refc.status_code == 200:
                with open(filename_temp, 'wb') as file:
                    file.write(response_temp.content)
                with open(filename_refc, 'wb') as file:
                    file.write(response_refc.content)
                print(f"Downloaded: {filename_temp} and {filename_refc}")
                run_found = True
            else:
                print(f"Failed to download {filename_temp} or {filename_refc}. Status code: {response_temp.status_code}")
                
    if run_found:
        break

if not run_found:
    print("No valid GFS data was found for the specified runs.")

# Define reflectivity bounds and colors for snow and rain with custom levels and colors
# Custom levels for rain intensity
rain_levels = [10, 20, 30, 40, 50, 60, 75]
rain_colors = ['#b2ff59', '#66bb6a', '#ffff00', '#ff8c00', '#ff0000', '#8b0000']  # Light green to dark red
cmap_refc_rain = plt.cm.colors.ListedColormap(rain_colors)
norm_refc_rain = plt.cm.colors.BoundaryNorm(rain_levels, cmap_refc_rain.N)

# Reflectivity bounds and colors for snow (light blue to darker blue)
snow_levels = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 100, 150]  # Reflectivity dBZ ranges for snow
snow_colors = ['#ffffff', '#c8e1ff', '#75c9ff', '#3fa1e6', '#0062d0', '#002e72', '#001c3a', '#000008', '#D3D3D3', '#0000FF', '#B0C4DE', '#FFFAFA']  # Snow (light gray for snow and blue for heavy snow)
cmap_refc_snow = plt.cm.colors.ListedColormap(snow_colors)
norm_refc_snow = plt.cm.colors.BoundaryNorm(snow_levels, cmap_refc_snow.N)

# Function to generate a single reflectivity plot for both snow and rain
def create_combined_reflectivity_plot(file_path_temp, file_path_refc, output_filename, forecast_step):
    try:
        # Open the GRIB2 files with xarray
        dataset_temp = xr.open_dataset(file_path_temp, engine="cfgrib")
        dataset_refc = xr.open_dataset(file_path_refc, engine="cfgrib")

        # Temperature data at 2 meters
        if 't2m' in dataset_temp.variables:
            temperature_k = dataset_temp['t2m']  # Temperature in Kelvin at 2 meters
            temperature_f = (temperature_k - 273.15) * 9 / 5 + 32  # Convert to Fahrenheit
            lats = dataset_temp['latitude'].values
            lons = dataset_temp['longitude'].values

            # Reflectivity data
            if 'refc' in dataset_refc.variables:
                refc = dataset_refc['refc']
                lons = np.where(lons > 180, lons - 360, lons)  # Adjust longitude if necessary

                # Create a meshgrid for plotting
                lon_grid, lat_grid = np.meshgrid(lons, lats)

                # Set up the Basemap
                fig, ax = plt.subplots(figsize=(14, 10))
                m = Basemap(projection='cyl', llcrnrlat=20, urcrnrlat=50,
                            llcrnrlon=-130, urcrnrlon=-60, resolution='i', ax=ax)
                m.drawcoastlines()
                m.drawcountries()
                m.drawstates()

                # Plot the snow reflectivity data (if temperature is below 32°F)
                snow_mask = temperature_f < 32
                refc_snow = np.ma.masked_where(~snow_mask, refc)  # Mask non-snow areas

                # Plot the rain reflectivity data (if temperature is above 32°F)
                rain_mask = temperature_f >= 32
                refc_rain = np.ma.masked_where(~rain_mask, refc)  # Mask non-rain areas

                # Plot the snow reflectivity
                refc_snow_contour = m.contourf(lon_grid, lat_grid, refc_snow, levels=snow_levels, cmap=cmap_refc_snow, norm=norm_refc_snow, latlon=True)

                # Plot the rain reflectivity
                refc_rain_contour = m.contourf(lon_grid, lat_grid, refc_rain, levels=rain_levels, cmap=cmap_refc_rain, norm=norm_refc_rain, latlon=True)

                # Combine colorbars for both snow and rain
                cbar = m.colorbar(refc_snow_contour, location='right', pad=0.05)
                cbar.set_label('Reflectivity (dBZ)', fontsize=12)
                cbar.ax.tick_params(labelsize=10)

                # Set the title based on snow or rain
                snow_or_rain = "Snow and Rain"  # Since both are plotted together
                plt.title(f'{snow_or_rain} - Reflectivity at 2m Above Ground - {output_filename} ({forecast_step})', fontsize=16)
                plt.tight_layout()

                # Save the plot as a PNG file
                plt.savefig(output_filename)
                plt.close()
                print(f"Plot saved: {output_filename}")
        else:
            print("The dataset does not contain the 't2m' variable (2-meter temperature).")

    except Exception as e:
        print(f"Error generating plot: {e}")

# Loop over the forecast steps and generate a single plot for each step
for step in forecast_steps:
    temp_file_path = os.path.join(grib_folder_temp, f"gfs.t{hour_str}z.pgrb2.0p25.{step}.grib2")
    refc_file_path = os.path.join(grib_folder_refc, f"gfs.t{hour_str}z.pgrb2.0p25.{step}.grib2")
    output_filename = os.path.join(rs_folder, f"reflectivity_combined_{date_str}_{step}.png")
    create_combined_reflectivity_plot(temp_file_path, refc_file_path, output_filename, step)
