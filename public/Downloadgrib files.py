import os
import requests
from datetime import datetime

# Folder paths for GRIB data and image outputs
base_folder = "./public"
grib_folder = os.path.join(base_folder, "grib")  # Folder for GRIB data
grib_folder_temp = os.path.join(grib_folder, "temp")  # Folder for temperature GRIB files
grib_folder_refc = os.path.join(grib_folder, "refc")  # Folder for reflectivity GRIB files
grib_folder_mslet = os.path.join(grib_folder, "mslet")  # Folder for MSLET GRIB files
rs_folder = os.path.join(base_folder, "RS")  # Use "RS" folder instead of "images"

# Create directories if they don't exist
os.makedirs(grib_folder_temp, exist_ok=True)
os.makedirs(grib_folder_refc, exist_ok=True)
os.makedirs(grib_folder_mslet, exist_ok=True)
os.makedirs(rs_folder, exist_ok=True)  # Ensure the "RS" folder exists

# Function to delete all files in a folder
def delete_all_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)  # Remove the file
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Remove the directory
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

# Function to run the main task
def run_task():
    # Delete old files in each folder before starting
    delete_all_files_in_folder(grib_folder_temp)
    delete_all_files_in_folder(grib_folder_refc)
    delete_all_files_in_folder(grib_folder_mslet)
    delete_all_files_in_folder(rs_folder)

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
    variable_mslet = "MSLET"  # Mean sea level pressure

    # Function to check if the file exists on the server
    def file_exists(url):
        response = requests.head(url)
        return response.status_code == 200

    # Try the most recent GFS run and fall back if necessary
    run_found = False
    for hour in [hour_str, f"{(int(hour_str) - 6) % 24:02d}"]:  # Try current and past run
        for step in forecast_steps:
            # Build the URL with the specified variables for temperature, reflectivity, and MSLET
            url_temp = (f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.{date_str}%2F{hour}%2Fatmos"
                        f"&file=gfs.t{hour}z.pgrb2.0p25.{step}&var_{variable_temp}=on&lev_2_m_above_ground=on")
            url_refc = (f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.{date_str}%2F{hour}%2Fatmos"
                        f"&file=gfs.t{hour}z.pgrb2.0p25.{step}&var_{variable_refc}=on&lev_entire_atmosphere=on")
            url_mslet = (f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?dir=%2Fgfs.{date_str}%2F{hour}%2Fatmos"
                         f"&file=gfs.t{hour}z.pgrb2.1p00.anl&var_{variable_mslet}=on&lev_mean_sea_level=on")

            # Check if the temperature, reflectivity, and MSLET files exist
            if file_exists(url_temp) and file_exists(url_refc) and file_exists(url_mslet):
                filename_temp = os.path.join(grib_folder_temp, f"gfs.t{hour}z.pgrb2.0p25.{step}.grib2")
                filename_refc = os.path.join(grib_folder_refc, f"gfs.t{hour}z.pgrb2.0p25.{step}.grib2")
                filename_mslet = os.path.join(grib_folder_mslet, f"gfs.t{hour}z.pgrb2.1p00.{step}.grib2")

                # Download the files
                response_temp = requests.get(url_temp)
                response_refc = requests.get(url_refc)
                response_mslet = requests.get(url_mslet)
                
                if response_temp.status_code == 200 and response_refc.status_code == 200 and response_mslet.status_code == 200:
                    with open(filename_temp, 'wb') as file:
                        file.write(response_temp.content)
                    with open(filename_refc, 'wb') as file:
                        file.write(response_refc.content)
                    with open(filename_mslet, 'wb') as file:
                        file.write(response_mslet.content)
                    print(f"Downloaded: {filename_temp}, {filename_refc}, and {filename_mslet}")
                    run_found = True
                else:
                    print(f"Failed to download one or more files. Status codes: {response_temp.status_code}, {response_refc.status_code}, {response_mslet.status_code}")

        if run_found:
            break

    if not run_found:
        print("No valid GFS data was found for the specified runs.")

# Run the task
run_task()
