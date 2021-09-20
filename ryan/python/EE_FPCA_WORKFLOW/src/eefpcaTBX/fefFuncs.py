
import os

class FeatureEngineFmt:
    """Class for formatting data into format for feature engine"""
    def __init__(self, file_path: str, class_column=None) -> None:
        self._file_path     = file_path
        self._dfs           = None
        self._files         = None
        self._ordered_files = None
        self._class_column  = class_column

        # step 1: test if the input is a dir or a zip file
        if os.path.isdir(self._file_path):
            # want to accumulate all the geojson files
            self._files = [os.path.join(self._file_path, i) for i in os.listdir(self._file_path) if i.endswith('.geojson')]
        elif os.path.isfile(self._file_path) and self._file_path.endswith('.zip'):
            # if the input is a zip want to extact all geojson files and move them to ./data/geojson
            self.__extract_zip_archive()
        else:
            # rasie error if a vailid input has not been entered
            pass

        # step 2: sort the input files into the year that they blong to
        self.__sort_geojson()

    def __sort_geojson(self) -> dict:
        """helper func to sort geojson into there years"""
        
        # this is to be run after files have been extracted
        # files_list = [os.path.join(self._file_path, i) for i in os.listdir(self._file_path)]
        unique_years = set(i.split("/")[-1].split('_')[0] for i in self._files)
        self._ordered_files = {k: [v for v in self._files if k in v] for k in unique_years}

    def __extract_zip_archive(self):
        """unpacks zip archive and accumulates all geojson files that are under the top most specified directory"""
        import zipfile
        rel_dir = os.path.dirname(os.path.realpath(self._file_path))
        with zipfile.ZipFile(self._file_path, 'r') as z:
            # self._files = [os.path.join(self._file_path.replace('.zip', ''), name) for name in z.namelist()]
            z.extractall(rel_dir)
            self._files = [
                os.path.join(root, file) for root, dir, files in os.walk(rel_dir) for file in files if file.endswith(".geojson")
            ]

    def __formatter(self, key:str, values:list, out_dir=None, to_shapefile=False):
        """this is the core fun for processing and foramting csvs"""
        # Private function to do all the dataframe processing
        import numpy as np
        import pandas as pd
        import geopandas as gpd
        
        # this block handles processing of the input geojsons as well as grabbing the col names we need for later
        dfs = []
        colnames = []
        for index, file in enumerate(values):
            gdf = gpd.GeoDataFrame.from_file(file)
            if index == 0:
                drop_cols = [i for i in gdf.columns if 'angle' in i or 'S1' not in i and self._class_column not in i]
            elif index == len(values) -1:
                drop_cols = [i for i in gdf.columns if 'angle' in i or 'S1' not in i and 'geometry' not in i]
            else:
                drop_cols = [i for i in gdf.columns if 'angle' in i or 'S1' not in i]
            gdf.drop(drop_cols, inplace=True, axis=1)
            colnames.append(gdf.columns)
            dfs.append(gdf)

        # this formats all the dataframes into one dataframe
        combined = gpd.GeoDataFrame(pd.concat(dfs, ignore_index=True, axis=1))
        flattened = np.array([item for sublist in colnames for item in sublist])
        combined.columns = flattened
        
        # sort the data frame by column name
        # further process the df
        combined = combined.reindex(sorted(combined.columns), axis=1)

        # Rearange the dataframe so that a POINT_x, POINT_Y are included in the first two columns
        combined['POINT_X'], combined['POINT_Y'] = combined['geometry'].x, combined['geometry'].y
        columns = combined.columns.tolist()
        columns.insert(0, columns.pop(columns.index('POINT_X')))
        columns.insert(1, columns.pop(columns.index('POINT_Y')))
        columns.insert(2, columns.pop(columns.index(self._class_column)))

        combined = combined[columns]
        unique_class = combined[self._class_column].unique().tolist()

        # TODO make beam_mode and relative orbit dynamic
        beam_mode = 'IW'
        orbit = 4

        if out_dir == None:
            out_dir = f'./output/csv/Sentinel-1/{beam_mode}/{orbit}' # this will need to be made dynamic
        else:
            out_dir = f'{out_dir}/csv/Sentinel-1/{beam_mode}/{orbit}'

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for c in unique_class:
            query = combined.loc[combined[self._class_column] == c]
            query = query.drop([self._class_column, 'geometry'], axis=1)
            csv_name = f'{c}_{beam_mode}_{key}_{orbit}.csv'
            query.to_csv(os.path.join(out_dir, csv_name))

        if to_shapefile:
            self.__mk_shapefile(combined, out_dir)

    def __mk_shapefile(dataframes, out_dir=None):
        if out_dir == None:
            out_dir = f'./output/shapefile/Sentinel-1'
        else:
            out_dir = f'{out_dir}/shapefile/Sentinel-1'

    def export(self, to_shapefile=False, out_dir=None):
        """[summary]

        Args:
            to_shape_file (bool, optional): [description]. Defaults to False.
        """
        for k, v in self._ordered_files.items():
                self.__formatter(k, v, out_dir, to_shapefile)
