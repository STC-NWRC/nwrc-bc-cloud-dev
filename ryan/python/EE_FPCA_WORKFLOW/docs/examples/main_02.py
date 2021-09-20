
import os

from fpcaTBX.fefFuncs import *

# change the working dir
os.chdir(os.path.abspath(os.path.dirname(__file__)))

def main():
    # create a FeatureEngineFmt object
    # this object will handle formating the exported 
    # geojsons from main_01.py
    path_to_zip = 'path/to/zip/file'
    obj = FeatureEngineFmt(file_path=path_to_zip)
    
    # export prediction to csv
    obj.export(to_shapefile=False)

if __name__ == '__main__':
    main()