import os
import time
import arcpy
import numpy as np
import pandas as pd

script_folder = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_folder)


def main(args=None):
    arcpy.env.overwriteOutput = True

    # Start the overall timer
    total_time_s = time.time()

    # path to processed Process csvs
    path_to_csvs = r'.\data-unlabelled-fpc-scores-csv'
    # csvs = get_files(path_to_csvs)

    sorted_csv = sort_files(path_to_csvs)
    
    # print('Complete:\tCSVS Grabbed')
    csvs = process_csv(sorted_csv)

    # Build the Shapefiles on the indivdual score file
    out_workspace = os.path.join(script_folder,'fpc-points.gdb')
    x_field = 'lon'
    y_field = 'lat'
    spatial_ref = int(4326) # For some reason this needs to be in wgs 84 in order for raster to points when moving to class struct make super hidden

    if not out_workspace.split('\\')[-1].endswith('.gdb'):
        raise Exception("Out workspace needs to be point to a gdb")

    print("Starting:\t Building Shapefile")
    for table in csvs:
        print("Building:\t{0}".format(table))
        build_time_s = time.time()
        build_shapefile_from_csv(
            path_to_csv=os.path.join(script_folder, table),
            out_workspace=out_workspace,
            x=x_field,
            y=y_field,
            sr=spatial_ref
        )
        build_time_e = time.time()

        timer(
            time_start=build_time_s,
            time_end=build_time_e,
            message='Build Time {0}'.format(table)
            )

    total_time_e = time.time()

    # Calculate the total time
    timer(
        time_start=total_time_s,
        time_end=total_time_e,
        message='Total Run Time'
    )


def process_csv(fpaths: dict) -> list:
    """
    WARNING THIS IS A DESTRUCTUVE PROCESS OVERWRITES EXISTING DATA USE WITH CAUTION

    :param path_to_dir: path to the direcroty were the fpc scores for a given year is
    :return: a list of paths to the target csvs
    """
    print("Building:\tCSV's")
    outdir = os.path.join('.', 'output')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    proc = []
    csvpaths = []
    for year, polerizations in fpaths.items():
        for pol, fpath in polerizations.items():
            print(f"CSVs:\t{year} {pol}")
            dfs = [pd.read_csv(f) for f in fpath]
            for df in dfs:
                latlon = np.float64(df.master_lat_lon.str.split("_", expand=True))
                df['lat'] = latlon[0:, 0]
                df['lon'] = latlon[0:, 1]
                proc.append(df)
            stack = pd.concat(proc, axis=0, ignore_index=True)
            outpath = f'{outdir}\\_{year}_{pol}_stacked.csv'
            stack.to_csv(outpath)
            proc.clear()
            csvpaths.append(outpath)
    return csvpaths

def sort_files(path_to_dir):
    """
    EXAMPLE
    
    {
        YEAR: {
            VV:[csv paths],
            VH:[csv paths]
        }
    }
    
    """
 
    tmp = {}
    paths = {}
    files = [i for i in os.listdir(path_to_dir) if i.endswith('.csv')]
    year = list(set([i.split('-')[2] for i in files]))
    pol = list(set([i.split('-')[1] for i in files]))

    for y in year:
        for p in pol:
            f = list(filter(lambda x: y in x and p in x, files))
            fpath = [os.path.join(path_to_dir, i) for i in f]
            paths.update({p: fpath})
        tmp.update({y: paths})
        paths = {}

    return tmp

def build_shapefile_from_csv(path_to_csv: str, out_workspace: str, x=None, y=None, name=None, sr=None):
    arcpy.env.workspace = out_workspace

    if name is None:
        name = path_to_csv.split("\\")[-1].split('.')[0]
    else:
        pass

    # Set the ouput sptaial ref for shape file, if the sr is None, defaults to wgs84
    if sr is None:
        spaital_ref = arcpy.SpatialReference(int(4326))
    else:
        spaital_ref = arcpy.SpatialReference(sr)

    arcpy.XYTableToPoint_management(path_to_csv, name, x, y, "#", spaital_ref)


def timer(time_start, time_end, message=None):
    sec = time_end - time_start

    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60

    if message is None:
        print(f'Time Lapsed = {int(hours)}:{int(mins)}:{int(sec)}')
    else:
        print(f'{str(message)}:\t {int(hours)}:{int(mins)}:{int(sec)}')


if __name__ == '__main__':
    main()
