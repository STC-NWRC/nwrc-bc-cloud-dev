import ee

from pprint import pprint
from shapely.geometry import shape

ee.Initialize()

asset = "users/ryangilberthamilton/BC/williston/stacks/williston_sub_a_2019"
eeImage = ee.Image(asset)

bndryGeometry = ee.FeatureCollection(eeImage.geometry().bounds())

task = ee.batch.Export.table.toDrive(**{
    "collection": bndryGeometry,
    "description": "williston_sub_a_bndry",
    "folder": "Williston_BNDRY",
    "fileFormat": "SHP"
}).start()
