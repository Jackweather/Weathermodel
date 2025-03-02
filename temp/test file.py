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
grib_folder = os.path.join(base_folder, "grib")
grib_folder_surft = os.path.join(grib_folder, "surft")  # Add the 'surft' folder
images_folder = os.path.join(base_folder, "images")
temp_folder = os.path.join(base_folder, "temp")

# Ensure the folders exist
os.makedirs(grib_folder, exist_ok=True)
os.makedirs(grib_folder_surft, exist_ok=True)  # Ensure 'surft' folder exists
os.makedirs(temp_folder, exist_ok=True)

# Get today's date and format it for the URL
today = datetime.now()
date_str = today.strftime("%Y%m%d")

# Determine the most recent GFS run based on the current hour
current_hour = today.hour
hour_str = f"{(current_hour // 6) * 6:02d}"  # Get the latest run in 6-hour intervals

# Forecast steps limited to f000 to f012 and then every 6 hours up to f096
forecast_steps = [f"f{str(i).zfill(3)}" for i in range(13)]  # Generates ['f000', ..., 'f012']
forecast_steps += [f"f{str(i).zfill(3)}" for i in range(12, 97, 6)]  # Adds ['f018', ..., 'f096']

# Variable to download
variable = "TMP"  # Temperature

# Function to check if the file exists on the server
def file_exists(url):
    response = requests.head(url)
    return response.status_code == 200

# Try the most recent GFS run and fall back if necessary
run_found = False
for hour in [hour_str, f"{(int(hour_str) - 6) % 24:02d}"]:  # Try current and past run
    for step in forecast_steps:
        # Build the URL with the specified variable
        url = (f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.{date_str}%2F{hour}%2Fatmos"
               f"&file=gfs.t{hour}z.pgrb2.0p25.{step}&var_{variable}=on&lev_2_m_above_ground=on")

        # Check if the file exists
        if file_exists(url):
            filename = os.path.join(grib_folder_surft, f"gfs.t{hour}z.pgrb2.0p25.{step}.grib2")  # Save to 'surft' folder

            # Request the file from the URL
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {filename}")
                run_found = True
            else:
                print(f"Failed to download {filename}. Status code: {response.status_code}")

    # If files are found for this run, exit the loop
    if run_found:
        break

if not run_found:
    print("No valid GFS data was found for the specified runs.")

# Function to generate the plot
def create_temperature_plot(file_path, output_filename):
    try:
        # Open the GRIB2 file with xarray
        dataset = xr.open_dataset(file_path, engine="cfgrib")

        # Check if the 2-meter temperature ('t2m') is available
        if 't2m' in dataset.variables:
            temperature_k = dataset['t2m']  # Temperature in Kelvin at 2 meters
            temperature_f = (temperature_k - 273.15) * 9 / 5 + 32  # Convert to Fahrenheit
            lats = dataset['latitude'].values
            lons = dataset['longitude'].values

            # Convert longitude to match Basemap's format (-180 to 180)
            lons = np.where(lons > 180, lons - 360, lons)

            # Create a meshgrid for plotting
            lon_grid, lat_grid = np.meshgrid(lons, lats)

           # Define temperature bounds and corresponding colors
            bounds = [-50, -45, -40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 32, 40, 50, 60, 70, 80, 90, 100, 110, 120]
            colors = [
    '#001F3F', '#003366', '#004C99', '#0066CC', '#3399FF', '#66B2FF', '#99CCFF', '#CCE5FF',  # Cool blues
    '#E6F7FF', '#FFFFFF', '#FFE6E6', '#FFCCCC', '#FF9999', '#FF6666', '#FF3333', '#FF1A1A',  # Transition to warm
    '#FF0000', '#E60000', '#CC0000', '#B20000', '#990000', '#800000', '#660000', '#4C0000',  # Deep reds
    '#330000', '#1A0000'
]



            cmap = plt.cm.colors.ListedColormap(colors)
            norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

            # Set up the Basemap
            fig, ax = plt.subplots(figsize=(14, 10))
            m = Basemap(projection='cyl', llcrnrlat=20, urcrnrlat=50,
                        llcrnrlon=-130, urcrnrlon=-60, resolution='i', ax=ax)
            m.drawcoastlines()
            m.drawcountries()
            m.drawstates()

            # Plot temperature data
            temp_contour = m.contourf(lon_grid, lat_grid, temperature_f, levels=bounds, cmap=cmap, norm=norm, latlon=True)
            cbar = m.colorbar(temp_contour, location='right', pad=0.05)
            cbar.set_label('Temperature (°F)', fontsize=12)
            cbar.ax.tick_params(labelsize=10)

            plt.title(f'Temperature (°F) at 2m Above Ground - {output_filename}', fontsize=16)
            plt.tight_layout()

            # Save the plot as a PNG file
            plt.savefig(output_filename)
            plt.close()
            print(f"Plot saved: {output_filename}")
        else:
            print("The dataset does not contain the 't2m' variable (2-meter temperature).")

    except Exception as e:
        print(f"Error opening the GRIB2 file: {e}")

# Generate the plots for each forecast step
image_files = []
for hour in [hour_str, f"{(int(hour_str) - 6) % 24:02d}"]:  # Try current and past run
    for step in forecast_steps:
        grib_file_path = os.path.join(grib_folder_surft, f"gfs.t{hour}z.pgrb2.0p25.{step}.grib2")  # Use 'surft' folder
        if os.path.exists(grib_file_path):
            output_filename = os.path.join(temp_folder, f"temperature_{hour}_{step}.png")
            create_temperature_plot(grib_file_path, output_filename)
            image_files.append(output_filename)

# Create an animated GIF
plot_files = [os.path.join(temp_folder, f"temperature_{hour}_{step}.png") for hour in [hour_str, f"{(int(hour_str) - 6) % 24:02d}"] for step in forecast_steps]
images = [Image.open(file) for file in plot_files if os.path.exists(file)]
animation_path = os.path.join(temp_folder, "gfs_animation.gif")
if images:
    images[0].save(animation_path, save_all=True, append_images=images[1:], duration=500, loop=0)
    print(f"GIF created: {animation_path}")
else:
    print("No images found to create a GIF.")
