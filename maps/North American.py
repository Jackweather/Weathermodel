import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# Create a plot with a Cartopy projection for North America
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# Set the extent to cover North America
ax.set_extent([-180, -50, 10, 90], crs=ccrs.PlateCarree())

# Add coastlines and country boundaries
ax.coastlines(resolution='110m')
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1)

# Add lakes and rivers for geographical context
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgreen')
ax.add_feature(cfeature.LAKES, facecolor='lightblue', edgecolor='blue')
ax.add_feature(cfeature.RIVERS, edgecolor='blue')

# Add state boundaries for the U.S.
ax.add_feature(cfeature.STATES, linestyle=':', edgecolor='gray')





# Title for the map
ax.set_title('Map of North America with Features')

# Show the map
plt.show()
