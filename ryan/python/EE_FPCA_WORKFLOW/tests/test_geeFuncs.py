
from pprint import pprint
import unittest

from fpcaTBX.geeFuncs import * 


class TestFeatureCollection(unittest.TestCase):
    assetid = "users/ryangilberthamilton/randForestTrain_bq"
    
    def test_featureCollection_valid_shapefile(self):
        import os
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        
        shp = './test_data/shp/bq_test.shp'
        fc_obj = FeatureCollection(shp)
        pprint(fc_obj.first().getInfo())

    def test_featureCollection_valid_assetId(self):
        from pprint import pprint
        fc_obj = FeatureCollection('users/ryangilberthamilton/randForestTrain_bq')
        pprint(fc_obj.first().getInfo())
    
    def test_featureCollection_non_valid_shapefile_wrongs_crs(self):
        pass

    def test_featureCollection_greater_than_5000_rows(self):
        pass

class TestS1Collection(unittest.TestCase):
    
    def test_image_collection_construction(self):
        collection = S1Collection(
            aoi='users/ryangilberthamilton/bq-trend-analysis/subset_BoQ_for_Ken_v2',
            years=[2018],
            months=['04-01', '05-31']
        )

    def test_image_collection_construction_fmtCollection(self):
        collection = S1Collection(
            aoi='users/ryangilberthamilton/bq-trend-analysis/subset_BoQ_for_Ken_v2',
            years=[2018],
            months=['04-01', '05-31']
        )
        
        fmt = collection.fmtCollections()
        assert isinstance(fmt, dict) == True

    def test_image_collection_access_system_ids(self):
        collection = S1Collection(
            aoi='users/ryangilberthamilton/bq-trend-analysis/subset_BoQ_for_Ken_v2',
            years=[2018, 2019],
            months=['04-01', '05-31']
        )
        system_id = collection.getSystemIds()
        
        assert isinstance(system_id, dict)

    def test_image_collection_access_system_ids_with_relative_orbit_query(self):
        collection = S1Collection(
            aoi='users/ryangilberthamilton/bq-trend-analysis/subset_BoQ_for_Ken_v2',
            years=[2018, 2019],
            months=['04-01', '05-31'],
            relative_orbit=4
        )
        system_id = collection.getSystemIds()
        
        
        
        import ee
        from pprint import pprint
        ee.Initialize()
        
        collection = ee.ImageCollection([ee.Image(i) for i in system_id.get(2018)])
        pprint(collection.aggregate_array('relativeOrbitNumber_start').distinct().getInfo())
        
        assert isinstance(system_id, dict)

class TestPreprocessing(unittest.TestCase):

    def test_eePreprocessing_construction(self):
        collection = S1Collection(
            aoi='users/ryangilberthamilton/bq-trend-analysis/subset_BoQ_for_Ken_v2',
            years=[2018, 2019],
            months=['04-01', '09-30'],
            relative_orbit=4
        )

        new_collection = collection.getSystemIds()


        procObj = eePreProcessing(
            system_ids=new_collection
        )
        
        # procObj.runPreProcessing()

    def test_eePreprocessing_run_preprocessing(self):
        collection = S1Collection(
            aoi='users/ryangilberthamilton/bq-trend-analysis/subset_BoQ_for_Ken_v2',
            years=[2018, 2019],
            months=['04-01', '09-30'],
            relative_orbit=4
        )

        new_collection = collection.getSystemIds()


        procObj = eePreProcessing(
            system_ids=new_collection
        )
        
        procObj.runPreProcessing()

class TestSampleing(unittest.TestCase):

    def test_sample_construction(self):
        import os
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        
        shp = './test_data/shp/bq_test.shp'
        fc_obj = FeatureCollection(shp)

        bbox = fc_obj.geometry().bounds()
        
        collection = S1Collection(
            aoi=bbox,
            years=[2018],
            months=['04-01', '05-31'],
            relative_orbit=4
        )

        system_ids = collection.getSystemIds()

        ee_pre_processing = eePreProcessing(
            system_ids=system_ids
        )

        pre_processed = ee_pre_processing.runPreProcessing()

        sampling = eeSampling(fc_obj, pre_processed)

    def test_generate_samples_toDrive(self):

        import os
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        
        shp = './test_data/shp/bq_test.shp'
        fc_obj = FeatureCollection(shp)

        bbox = fc_obj.geometry().bounds()
        
        collection = S1Collection(
            aoi=bbox,
            years=[2018],
            months=['04-01', '05-31'],
            relative_orbit=4
        )

        system_ids = collection.getSystemIds()

        ee_pre_processing = eePreProcessing(
            system_ids=system_ids
        )

        pre_processed = ee_pre_processing.runPreProcessing()

        sampling = eeSampling(fc_obj, pre_processed)
        sampling.exportSamplesToDrive(monitor_task=True)

    def test_add_relorbit_to_collection(self):
        import os
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        
        shp = './test_data/shp/bq_test.shp'
        fc_obj = FeatureCollection(shp)

        bbox = fc_obj.geometry().bounds()
        
        collection = S1Collection(
            aoi=bbox,
            years=[2018],
            months=['04-01', '05-31'],
            relative_orbit=4
        )

        system_ids = collection.getSystemIds()

        ee_pre_processing = eePreProcessing(
            system_ids=system_ids
        )

        pre_processed = ee_pre_processing.runPreProcessing()

        sampling = eeSampling(fc_obj, pre_processed)
        samples = sampling.samples[2018]
        pprint(samples[0].first().getInfo())

    def test_export_multi_year_sampels(test):
        import os
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        
        shp = './test_data/shp/bq_test.shp'
        fc_obj = FeatureCollection(shp)

        bbox = fc_obj.geometry().bounds()
        
        collection = S1Collection(
            aoi=bbox,
            years=[2018, 2019, 2020],
            months=['04-01', '09-30 '],
            relative_orbit=4
        )

        system_ids = collection.getSystemIds()

        ee_pre_processing = eePreProcessing(
            system_ids=system_ids
        )

        pre_processed = ee_pre_processing.runPreProcessing()

        sampling = eeSampling(fc_obj, pre_processed)
        sampling.exportSamplesToDrive()