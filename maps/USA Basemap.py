from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import shapefile  # PyShp module for creating shapefiles

# Create the map focused on the USA
plt.figure(figsize=(12, 8), dpi=120)
m = Basemap(projection='lcc', resolution='i',  # 'i' resolution for more detail
            lat_0=37.5, lon_0=-98.35,
            width=6e6, height=3e6)

# Draw map features and extract coordinates
m.drawcoastlines(linewidth=0.8)
m.drawcountries(linewidth=0.8)
m.drawstates(linewidth=0.5)

# Initialize a shapefile writer
w = shapefile.Writer("usa_map")
w.field("ID", "N", 10)  # Field for each shape ID

# Draw counties and save coordinates to shapefile
m.drawcounties(linewidth=0.4, color='gray')  # Draw counties
for county in m.counties:
    for segment in county:
        shape_points = []
        for point in segment:
            # Make sure point is a tuple or list, not a single float
            if isinstance(point, tuple):
                lon, lat = point  # Unpack the tuple directly
            else:
                # If point is a float, skip it (this shouldn't happen)
                continue
            # Convert map projection coordinates to lat/lon
            shape_points.append([lon, lat])  # Append longitude and latitude
        # Add each county shape to the shapefile
        w.poly([shape_points])  # Add the list of points as a polygon

# Save the shapefile
w.close()

# Add a title
plt.title("USA Map with Counties", fontsize=14, fontweight='bold')

# Save the map as a PNG image
plt.savefig("usa_map.png", dpi=300)  # Save as high-resolution PNG

# Show the plot
plt.show()
