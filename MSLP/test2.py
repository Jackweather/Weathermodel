import requests
import os
import cfgrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from scipy.ndimage import gaussian_filter, minimum_filter, maximum_filter
from PIL import Image
from datetime import datetime

# Define the function to download GRIB files
def download_grib_files():
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    current_hour = today.hour
    run_hour = (current_hour // 6) * 6
    hour_str = f"{run_hour:02d}"
    forecast_steps = [f"f{str(i).zfill(3)}" for i in range(13)]
    forecast_steps += [f"f{str(i).zfill(3)}" for i in range(12, 97, 6)]
    output_folder = os.path.join(os.getcwd(), 'public', 'mslet')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    for step in forecast_steps:
        url = f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?dir=%2Fgfs.{date_str}%2F{hour_str}%2Fatmos&file=gfs.t{hour_str}z.pgrb2.1p00.{step}&var_MSLET=on&var_PRMSL=on&lev_mean_sea_level=on"
        output_filename = os.path.join(output_folder, f"gfs_t{hour_str}z_pgrb2_1p00_{step}.grb2")
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_filename, 'wb') as file:
                file.write(response.content)
        else:
            continue

# Define the function to create PNG from GRIB
def create_png_from_grib(file_path, output_folder):
    forecast_hour = file_path.split("_")[-1].replace(".grb2", "").replace("f", "")
    ds = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'meanSea'})
    lons, lats = np.meshgrid(ds.longitude.values, ds.latitude.values)
    mslp = ds.prmsl.values / 100
    min_val = np.nanmin(mslp)
    max_val = np.nanmax(mslp)
    if np.isnan(min_val) or np.isnan(max_val) or min_val >= max_val:
        raise ValueError("Invalid data detected. Check the GRIB2 file for issues.")
    mslp_smoothed = gaussian_filter(mslp, sigma=2)
    neighborhood_size = 10
    local_min = minimum_filter(mslp_smoothed, neighborhood_size)
    local_max = maximum_filter(mslp_smoothed, neighborhood_size)
    lows = (mslp_smoothed == local_min)
    highs = (mslp_smoothed == local_max)
    plt.figure(figsize=(16, 10), dpi=120)
    m = Basemap(projection='lcc', resolution='i', lat_0=37.5, lon_0=-98.35, width=9e6, height=6e6)
    m.drawcoastlines(linewidth=0.8)
    m.drawcountries(linewidth=0.8)
    m.drawstates(linewidth=0.5)
    m.drawcounties(linewidth=0.4, color='gray')
    x, y = m(lons, lats)
    x_mask = (x >= 0) & (x <= m.urcrnrx) & (y >= 0) & (y <= m.urcrnry)
    mslp = np.where(x_mask, mslp, np.nan)
    contour_levels = np.arange(min_val, max_val, 4) if min_val < max_val else np.linspace(980, 1040, 20)
    contour_lows = m.contour(x, y, mslp, levels=contour_levels[contour_levels < 1019], colors="red", linewidths=1.2)
    contour_highs = m.contour(x, y, mslp, levels=contour_levels[contour_levels >= 1019], colors="blue", linewidths=1.2)
    plt.clabel(contour_lows, inline=True, fontsize=9, fmt="%1.0f", colors='red')
    plt.clabel(contour_highs, inline=True, fontsize=9, fmt="%1.0f", colors='blue')
    for i in range(mslp.shape[0]):
     for j in range(mslp.shape[1]):
        if x_mask[i, j]:
            pressure_value = mslp[i, j]  # Get the actual pressure value
            if highs[i, j]:
                plt.text(x[i, j], y[i, j], f"H\n{pressure_value:.0f}", color='blue', 
                         fontsize=14, fontweight='bold', ha='center', va='center')
            elif lows[i, j]:
                plt.text(x[i, j], y[i, j], f"L\n{pressure_value:.0f}", color='red', 
                         fontsize=14, fontweight='bold', ha='center', va='center')

    plt.title(f"High and Low Pressure Systems Over the USA (Forecast Hour: {forecast_hour})", fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', linewidth=0.5)
    output_filename = os.path.join(output_folder, f"{os.path.basename(file_path)}.png")
    plt.savefig(output_filename, bbox_inches='tight', dpi=300)
    plt.close()

# Define the function to create a GIF from PNG files
def create_gif_from_png(output_folder):
    png_files = [f for f in os.listdir(output_folder) if f.endswith(".png")]
    png_files.sort()
    images = [Image.open(os.path.join(output_folder, f)) for f in png_files]
    gif_filename = os.path.join(os.getcwd(), 'public', 'HL', 'animation.gif')
    images[0].save(gif_filename, save_all=True, append_images=images[1:], duration=500, loop=0)

output_folder = os.path.join(os.getcwd(), 'public', 'HL')
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

download_grib_files()
grib_folder = os.path.join(os.getcwd(), 'public', 'mslet')
for file_name in os.listdir(grib_folder):
    if file_name.endswith(".grb2"):
        create_png_from_grib(os.path.join(grib_folder, file_name), output_folder)
create_gif_from_png(output_folder)
