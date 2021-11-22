import os
import sys
import arcpy

script_folder = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_folder)


def main(args=None):
    arcpy.env.workspace = os.path.join(script_folder, 'fpc-points.gdb')
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3005)


    pts = [i for i in arcpy.ListFeatureClasses(feature_type='Point')]

    for index, i in enumerate(pts):
        print(f"Building Components:\t{i}")

        components = [i.name for i in arcpy.ListFields(i, 'fpc_*')]

        if i.endswith('.shp'):
            outname = i.split('.')[0].split("_")[1:3]
            outname = f'{outname[1]}-{outname[0]}'

        else:
            outname = i.split("_")[1:3]
            outname = f'{outname[1]}-{outname[0]}'

        # force the coordinate system to UTM 18N -> this needs to be set inorder for the cell
        # size to be generated


        # create the ouput bucket
        #TODO dir creation make this dynamic
        out_dir = os.path.join('.', outname, 'components')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for comp in components:
            out = f'{out_dir}\\{comp}.tif'
            print(f"Building:\t{comp}")
            arcpy.PointToRaster_conversion(i, comp, out, 'MEAN', "", 15)

        print("All FPC Components Built...")


if __name__ == '__main__':
    main()
