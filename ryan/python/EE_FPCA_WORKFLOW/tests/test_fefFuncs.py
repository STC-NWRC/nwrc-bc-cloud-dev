
import unittest

from eefpcaTBX.fefFuncs import *

class TestFormatter(unittest.TestCase):
    def test_inital_construction_from_zip_archive(self):
        import os
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        
        ZIP_PATH = './test_data/zip/eeTrend_Analysis_20210820_101025-20210820T150124Z-001.zip'
        FeatureEngineFmt(ZIP_PATH, class_column='dDesc').export(to_shape_file=False)

    def test_initial_construction_from_geojson_dir(self):
        pass