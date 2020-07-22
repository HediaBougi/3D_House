import json
import rasterio
from rasterio.mask import mask
from pathlib import Path
import numpy as np
import plotly.graph_objects as go
from BBox import BBox
from PolygonRequest import *

address = input("Please enter a valid address:\t")

#Tiff files path
data_dsm_path = "/home/becode/3D House Project/Data/DSM/GeoTIFF/"
data_dtm_path = "/home/becode/3D House Project/Data/DTM/GeoTIFF/"

#Request the formatted address
#Request BBox of the address
#Raise an error msg if the address doesn't exist
try:

    req = requests.get(f"http://loc.geopunt.be/geolocation/location?q={address}&c=1").json()

    formattedaddress = req["LocationResult"][0]["FormattedAddress"]

    # Get Bounding Box of the entered address
    bb_addr = BBox(req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["X_Lambert72"],
                   req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["Y_Lambert72"],
                   req["LocationResult"][0]["BoundingBox"]["UpperRight"]["X_Lambert72"],
                   req["LocationResult"][0]["BoundingBox"]["UpperRight"]["Y_Lambert72"])

except IndexError:
    print(address, " :Address doesn't exist")
except:
    print("Something else went wrong")
    exit()

polygon = PolygonRequest(address)

# List all tiff files in directory using Path
# Search for the matched tiff
#Compare the BBox address to the BBox tiff file
files_in_data_dsm = (entry for entry in Path(data_dsm_path).iterdir() if entry.is_file())
for item in files_in_data_dsm:
    tiff_dsm = rasterio.open(data_dsm_path + item.name)
    if bb_addr.isIn(BBox(tiff_dsm.bounds.left, tiff_dsm.bounds.bottom, tiff_dsm.bounds.right, tiff_dsm.bounds.top)):
        tiff_dtm = rasterio.open(data_dtm_path + item.name.replace("DSM", "DTM"))
        break

# Crop tiff files
crop_dsm_img, crop_dsm_transform = mask(dataset=tiff_dsm, shapes=polygon, crop=True, indexes=1)
crop_dtm_img, crop_dtm_transform = mask(dataset=tiff_dtm, shapes=polygon, crop=True, indexes=1)
crop_chm_img = crop_dsm_img - crop_dtm_img


#3D plot
#fliplr: Reverse the order of elements in 'crop_chm_img' array horizontally
fig = go.Figure(data=go.Surface(z=np.fliplr(crop_chm_img), colorscale='plotly3'))
fig.update_layout(scene_aspectmode='manual', scene_aspectratio=dict(x=1, y=1, z=0.5))
fig.update_layout(
    title={
        'text': "3D Building at " + formattedaddress,
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    title_font_color="green")

fig.show()



#Construct a new Surface object
# The data the describes the coordinates of the surface is set in z.
# Data in z should be a 2D list. Coordinates in x and y can either be 1D lists or 2D lists
# (e.g. to graph parametric surfaces).
# If not provided in x and y, the x and y coordinates are assumed to be linear starting at 0 with a unit step.
