import os
import requests
from datetime import datetime

# Folder paths for GRIB data and image outputs
base_folder = "./public"
grib_folder = os.path.join(base_folder, "grib")
images_folder = os.path.join(base_folder, "images")

# Ensure the folders exist
os.makedirs(grib_folder, exist_ok=True)
os.makedirs(images_folder, exist_ok=True)

# Get today's date and format it for the URL
today = datetime.now()
date_str = today.strftime("%Y%m%d")

# Determine the most recent GFS run based on the current hour
current_hour = today.hour
hour_str = f"{(current_hour // 6) * 6:02d}"  # Get the latest run in 6-hour intervals

# Forecast steps limited to f000 to f012 and then every 6 hours up to f096
forecast_steps = [f"f{str(i).zfill(3)}" for i in range(13)]  # Generates ['f000', 'f001', ..., 'f012']
forecast_steps += [f"f{str(i).zfill(3)}" for i in range(12, 97, 6)]  # Adds ['f018', 'f024', ..., 'f096']

# Base URL for downloading the latest GFS model data
base_url = f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.{date_str}%2F{hour_str}%2Fatmos"

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
            filename = os.path.join(grib_folder, f"gfs.t{hour}z.pgrb2.0p25.{step}.grib2")

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
