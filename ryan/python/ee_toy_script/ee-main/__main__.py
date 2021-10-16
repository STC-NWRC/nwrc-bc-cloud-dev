import os
import shapefile
from eefpcaTBX.geeFuncs import *
from eefpcaTBX.predictionfmt import *

def main(args=None):

    # Step 1: define bucket names
    ee_bucket_1 = 'ee-bucket-one'
    ee_bucket_2 = 'ee-bucket-two'

    buckets = [ee_bucket_1, ee_bucket_2]

    # Step 4: grab and convert bounding geometry of the area
    spath = "..\\shapefile\\willistonA_split.shp"
    sfeatures = shapefile.Reader(spath).__geo_interface__
    west, south, east, north = sfeatures['bbox']

    eeGeometry = {
        index: ee.Geometry(i['geometry']) for index, i in enumerate(sfeatures['features'], start=1)
    }
    eeBBox = ee.Geometry.BBox(west, south, east, north)

    # Step 5: get all images for a given orbit number
    s1_collection = S1Collection(
        aoi=eeBBox,
        years=['2019', '2020'],
        months=['04-01', '10-01'],
        relative_orbit=166
    )
    system_ids = s1_collection.getSystemIds()

    # Step 6: pre-process images
    preprocessed = eePreProcessing(system_ids)
    processed = preprocessed.runPreProcessing()
    
    # Step 7: interate over each side of the split bounding geometry
    for index, geometry in enumerate(eeGeometry.items()):
        for year, images in processed.items():
            stack = ee.Image.cat(images)
            # create the task config
            cloud_conf = {
                'image': stack,
                'description': f'ee_stack_{year}_side_{geometry[0]}',
                'bucket': buckets[index],
                'region': geometry[1],
                'scale': 10,
                'crs': 'EPSG:3005',
                'fileFormat': 'GeoTIFF',
                'maxPixels': 1e13,
                'formatOptions': {'cloudOptimized': True}
            }
            task = ee.batch.Export.image.toCloudStorage(**cloud_conf)
            
            # start the task
            task.start()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()