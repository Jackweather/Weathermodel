import xarray as xr
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

# Path to the GRIB2 file
file_path = r"C:\Users\jacfo\Downloads\Global model runs website\public\grib\gfs.t18z.pgrb2.0p25.f006.grib2"

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
        # The longitude might already be in the correct format, check if conversion is needed
        lons = np.where(lons > 180, lons - 360, lons)

        # Create a meshgrid for plotting
        lon_grid, lat_grid = np.meshgrid(lons, lats)

        # Define temperature bounds and corresponding colors
        bounds = [-90, -70, -50, -40, -30, -20, 0, 10, 32, 40, 50, 60, 70, 80, 90, 100, 120]

        # Define colors
        # First set: below freezing (32°F) - cooler shades (blues and pinks)
        # Second set: above freezing (32°F) - warmer shades (greens, yellows, and reds)
        colors = [
            '#FFB6C1', '#FF69B4', '#D84C9A', '#9B36A2', '#6A0DAD', '#4B0082', '#8A2BE2', '#4169E1',  # blues
            '#90EE90', '#32CD32', '#228B22', '#FFFF00', '#FFA500', '#FF4500', '#B22222', '#000000'   # warmer colors
        ]

        # Create a custom colormap
        cmap = ListedColormap(colors)
        norm = BoundaryNorm(bounds, cmap.N)

        # Set up the Basemap
        fig, ax = plt.subplots(figsize=(14, 10))
        m = Basemap(projection='cyl', llcrnrlat=20, urcrnrlat=50,
                    llcrnrlon=-130, urcrnrlon=-60, resolution='i', ax=ax)

        # Draw map features
        m.drawcoastlines()
        m.drawcountries()
        m.drawstates()

        # Plot temperature data using contourf with the custom colormap
        temp_contour = m.contourf(
            lon_grid, lat_grid, temperature_f, levels=bounds, cmap=cmap, norm=norm, latlon=True
        )

        # Add a colorbar
        cbar = m.colorbar(temp_contour, location='right', pad=0.05)
        cbar.set_label('Temperature (°F)', fontsize=12)
        cbar.ax.tick_params(labelsize=10)

        # Add a title
        plt.title('Temperature (°F) at 2m Above Ground', fontsize=16)
        plt.tight_layout()
        plt.show()
    else:
        print("The dataset does not contain the 't2m' variable (2-meter temperature).")

except Exception as e:
    print(f"Error opening the GRIB2 file: {e}")
