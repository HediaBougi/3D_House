import re
import requests
import rasterio
from rasterio.plot import show
from rasterio.mask import mask
from pathlib import Path
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import geopandas as gpd
from BBox import BBox
from getFeatures import getFeatures

#address = input("Please enter a string:\t")


# address = "Kortrijksebaan 57, 3220 Holsbeek"
# address = "Kortrijksebaan 75, 3220 Holsbeek"
# address = "Zomerlei 13, 2650 Edegem"
#address = "Benedenstraat 6, 3220 Holsbeek"
# address = "kruisveldweg 8, 2500 Lier"
# address = "Sint-Pietersvliet 7, 2000 Antwerpen"
# address = "Pareloesterlaan 15, 8400 Oostende"
address = "BELLEMANSHEIDE 78J 1640 SINT-GENESIUS-RODE"

# address_regx = re.compile("^([A-z-]+)\s(\d+),\s(\d+)\s([A-z]+)")
# result = address_regx.search(address)
# street = result.group(1)
# nb = result.group(2)
# pc = result.group(3)
# city = result.group(4)

req = requests.get(f"https://loc.geopunt.be/v4/Location?q={address}").json()
#print(json.dumps(req, indent=4, sort_keys=True))
city = req["LocationResult"][0]["Municipality"]
street = req["LocationResult"][0]["Thoroughfarename"]
nb = req["LocationResult"][0]["Housenumber"]
pc = req["LocationResult"][0]["Zipcode"]

data_dsm_path = "/home/becode/3D House Project/Data/DSM/GeoTIFF/"
data_dtm_path = "/home/becode/3D House Project/Data/DTM/GeoTIFF/"
cadastral_shape_file = "/home/becode/3D House Project/Data/ShapeFiles/" +city.upper()+ "_L72_2020/Bpn_CaPa.shp"
# cadastral_shape_file = "/media/hdd/dadou/3DHouse/data/ShapeFiles/Bpn_CaPa_VLA.shp"
#cadastral_shape_file = "/home/becode/3D House Project/Data/ShapeFiles/" +city.upper()+ "_L72_2020/Bpn_ReBu.shp"


req = requests.get(f"https://api.basisregisters.dev-vlaanderen.be/v1/adresmatch?gemeentenaam={city}&straatnaam={street}&huisnummer={nb}&postcode={pc}").json()
#print(req)
objectId = req["adresMatches"][0]["adresseerbareObjecten"][0]["objectId"]
print(objectId)
perceel = req["adresMatches"][0]["adresseerbareObjecten"][1]["objectId"].replace("-", "/")

req = requests.get(f"https://api.basisregisters.dev-vlaanderen.be/v1/gebouweenheden/{objectId}").json()
objectId = req["gebouw"]["objectId"]
print(objectId)

req = requests.get(f"https://api.basisregisters.dev-vlaanderen.be/v1/gebouwen/{objectId}").json()
print(json.dumps(req, indent=4, sort_keys=True))
polygon = [req["geometriePolygoon"]["polygon"]]
print(polygon)

req = requests.get(f"http://loc.geopunt.be/geolocation/location?q={address}&c=1").json()
print(json.dumps(req, indent=4, sort_keys=True))

# Get Bounding Box of the entered address
bb_addr = BBox(req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["X_Lambert72"],
               req["LocationResult"][0]["BoundingBox"]["LowerLeft"]["Y_Lambert72"],
               req["LocationResult"][0]["BoundingBox"]["UpperRight"]["X_Lambert72"],
               req["LocationResult"][0]["BoundingBox"]["UpperRight"]["Y_Lambert72"])

# List all tiff files in directory using Path
# Search for the matched tiff
files_in_data_dsm = (entry for entry in Path(data_dsm_path).iterdir() if entry.is_file())
for item in files_in_data_dsm:
    tiff_dsm = rasterio.open(data_dsm_path + item.name)
    if bb_addr.isIn(BBox(tiff_dsm.bounds.left, tiff_dsm.bounds.bottom, tiff_dsm.bounds.right, tiff_dsm.bounds.top)):
        print(item.name + " --> " + str(tiff_dsm.bounds))
        tiff_dtm = rasterio.open(data_dtm_path + item.name.replace("DSM", "DTM"))
        print("tiff", tiff_dsm)
        break
        # show(rio.open(f"{data_dsm_path+item.name}"), cmap="cividis")

# Filter GeoDataFrame using Cadastral Parcel Key
# Extract coordinates from GeoDataFrame
# Crop tiff file
df_shape = gpd.read_file(cadastral_shape_file)
coords = getFeatures(df_shape[df_shape.CaPaKey == perceel])

crop_dsm_img, crop_dsm_transform = mask(dataset=tiff_dsm, shapes=coords, crop=True, nodata=0, filled=True, indexes=1)
crop_dtm_img, crop_dtm_transform = mask(dataset=tiff_dtm, shapes=coords, crop=True, nodata=0, filled=True, indexes=1)
crop_chm_img1 = crop_dsm_img - crop_dtm_img
#print(tiff_dsm.meta)

crop_dsm_img, crop_dsm_transform = mask(dataset=tiff_dsm, shapes=polygon, crop=True, nodata=0, filled=True, indexes=1)
crop_dtm_img, crop_dtm_transform = mask(dataset=tiff_dtm, shapes=polygon, crop=True, nodata=0, filled=True, indexes=1)
crop_chm_img = crop_dsm_img - crop_dtm_img


# Copy the metadata
#crop_dsm_meta = tiff_dsm.meta.copy()
# Parse EPSG code
#epsg_code = int(tiff_dsm.crs.data['init'][5:])
# Update new metadata
'''crop_dsm_meta.update({"driver": "GTiff",
                 "height": crop_dsm_img.shape[1],
                 "width": crop_dsm_img.shape[2],
                 "transform": crop_dsm_transform,
                 "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
                )'''
#print(crop_dsm_meta)
#print(crop_dsm_img)

#crop_dsm_tif = "tmp.tiff"

#with rasterio.open(crop_dsm_tif, "w", **crop_dsm_meta) as dest:
   # dest.write(crop_dsm_img)

# Show cropped tiff
#show(rasterio.open(f"{crop_tif}"), cmap ='pink')
# Show tiff file
#show(rasterio.open(f"{data_dsm_path + item.name}"), cmap="cividis")
#show(crop_dsm_img)

'''fig = make_subplots(
    rows=1, cols=2,
    specs=[[{'type': 'surface'}, {'type': 'surface'}]])


fig.add_trace(
    go.Surface(z=np.flip(crop_chm_img, axis=1), colorscale='YlOrRd', showscale=False),
    row=1, col=1)

fig.add_trace(
    go.Surface(z=np.flip(crop_chm_img1, axis=1), colorscale='RdBu', showscale=False),
    row=1, col=2)
'''
#print(crop_chm_img)
print(crop_dsm_img)
fig = go.Figure(data=go.Surface(z=np.flip(crop_chm_img1, axis=1), colorscale='blackbody'))
fig.update_layout(scene_aspectmode='manual', scene_aspectratio=dict(x=1, y=1, z=0.5))
fig.show()

print(type(crop_chm_img))
print("Done")
