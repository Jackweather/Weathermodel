import xarray as xr

# Path to the GRIB2 file
file_path = r"C:\Users\jacfo\Downloads\Global model runs website\public\grib\gfs.t18z.pgrb2.0p25.f006.grib2"

try:
    # Open the GRIB2 file
    dataset = xr.open_dataset(file_path, engine="cfgrib")

    # Print the dataset structure
    print(dataset)
except Exception as e:
    print(f"Error reading the GRIB2 file: {e}")
