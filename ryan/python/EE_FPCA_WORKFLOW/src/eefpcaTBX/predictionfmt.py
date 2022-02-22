import ee
import os
import rasterio
import numpy as np

from datetime import datetime

# internal classes
from .geeFuncs import FeatureCollection, eePreProcessing

class ExportImages:
    """Used to Export images you want to predict on addes pixel lat lon to the image"""
    def __init__(self, system_ids_dict: dict, aoi) -> None:
        self._aoi              = aoi
        self._system_ids_dict  = system_ids_dict
        self._for_export       = self.__process_ee_images()

    def __export_name(self, image: ee.Image):
        date = image.date().format('YYYYMMdd')
        mode = image.get('instrumentMode')
        
        date_str = ee.String(date)
        mode_str = ee.String(mode)
        
        fmt1 = ee.String('S1_').cat(date_str)
        fmt2 = fmt1.cat('_')
        fmt3 = fmt2.cat(mode_str)
        
        return image.set({'export_name': fmt3})

    def __process_ee_images(self):
        """This will take in the list of consturcted eeImage or a list of asset ids
            images MUST be from the same relative orbit number and fall over the same
            geographic area
            
            processing
                - Formatting bands
                - applying 5x5 boxcar de - speckling
                - co - registering all images in the list
                - add Pixel lat lon bands to each image (important if converting to)
            """

        def copy_poperties(image:ee.Image, prop, prop2) -> dict:
            lat_lon_bands = image.pixelLonLat()
            
            return image.set({
                prop: image.get(prop),
                prop2: image.get(prop2)
            }).addBands(lat_lon_bands)


        processing = eePreProcessing(self._system_ids_dict).runPreProcessing()
        
        # add Pixel Lat Lon to each image

        return {k: [self.__export_name(copy_poperties(x, "instrumentMode", "system:time_start")) for x in v] \
             for k,v in processing.items()}

    def exportToGoogleCloud(self, cloud_bucket, crs=None):

        bounds = ee.FeatureCollection(self._aoi).geometry()

        conf = {
            'image': None,
            'description': None,
            'bucket': cloud_bucket,
            'fileNamePrefix': "img/",
            'crs': f"EPSG:{crs}",
            'region': bounds,
            'fileFormat': "GeoTIFF",
            'maxPixels': 1e13,
            'scale': 10,
            'formatOptions': {
                'cloudOptimized': True
            }
        }

        for array in self._for_export.values():
            for image in array:
                conf["image"] = image
                conf['description'] = ee.String(image.get('export_name')).getInfo()
                task = ee.batch.Export.image.toCloudStorage(**conf)
                task.start()

    def exportToGoogleDrive(self, project_name=None, crs=None):

        bounds = ee.FeatureCollection(self._aoi).geometry().bounds()
        
        conf = {
            'image': None, 
            'description': None,
            'folder': None,
            'fileFormat': 'GeoTIFF',
            'scale': 10,
            'region': bounds,
            'maxPixels': 1e13
        }

        # create the folder name
        now = datetime.now()
        fmt_time = now.strftime("%Y%m%d_%H%I%M")
        if project_name == None:
            folder = f'eeTrend_Analysis__GeoTIFFS_{fmt_time}'
        else:
            folder = f'{project_name}_GeoTIFFS_{fmt_time}'

        conf['folder'] = folder
        # function to help defult proj
        def getCrs():
            img = list(self._for_export.values())[0][0]
            return img.projection().crs()

        # Add CRS 
        conf['crs'] = f'EPSG:{crs}' if crs is not None else None

        for array in self._for_export.values():
            for image in array:
                conf['image'] = image
                image.getInfo()
                conf['description'] = ee.String(image.get('export_name')).getInfo()
                task = ee.batch.Export.image.toDrive(**conf)
                task.start()

class Tiff2CSV:
    """Takes in a GeoTIFF and converts it to a CSV"""
    def __init__(self, dir_name: str, bands: dict, outdir=None) -> None:
        self.dir_name = dir_name
        self.bands    = bands
        self.outdif   = outdir
        self.tifs     = None

        # find all tifs 
        self.__find_tifs()

    # private functions
    def __find_tifs(self):
        """Helper functions to extract all tiff files in a directory tree"""
        tif_paths = []
        for root, dirs, files in os.walk(self.dir_name):
            for file in files:
                if file.endswith(".tif"):
                    tif_paths.append(os.path.join(root, file))
                else:
                    continue
        self.tifs = tif_paths

    def __extract_bands(self, tif):
        ds = rasterio.open(tif)
        name = tif.split("/")[-1]

        if not os.path.exists(self.outdif):
            os.makedirs(self.outdif)

        for k,v in self.bands.items():
            li = name.split("\\")[-1].split("_")
            date = li[1]
            mode = li[2]
            fmt = f'_{date}_{mode}_{k}.csv'
            out_path = os.path.join(self.outdif, fmt)
            data = ds.read(v)
            np.savetxt(out_path, data, delimiter=',')

    # public fucntions
    def tif2csv(self):
        """Converts Tifs to CSV"""
        if len(self.tifs) == 0:
            raise Exception("Specified Dir is clean... Nothing to Extract")

        for i in self.tifs:
            self.__extract_bands(i)