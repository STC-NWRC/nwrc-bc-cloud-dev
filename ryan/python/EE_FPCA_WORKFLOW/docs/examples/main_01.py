
import fpcaTBX.geeFuncs as tbx

# Example workflow for getting data for Data extraction for Google Earth Engine FPCA
def main(args=None):
    # step one is to define the area you are intresed in
    aoi = 'point_feature_collection' 
    
    # step two: create some variable that define the time series you are intresed in
    years = [2018, 2019, 2020]
    months = ['04-01', '09-30']

    # this will be the query we will use to view all the
    collection = tbx.S1Collection(
        aoi=aoi,
        years=years,
        months=months
    )

    # step 3: select the images that will be used in the trend analysis. 
    # NOTE: that only homogenous orbits shuold be used no mixing, and ensure that 
    # all of the data is totally located within the footprint of the relative orbit swath 
    # you go with.
    final_collection = tbx.S1Collection(
        aoi=aoi,
        years=years,
        months=months,
        relative_orbit=4
    )

    # step 5: extract the systme ids of the returned collection. 
    system_ids = final_collection.getSystemIds()

    # step 6: pass the system ids to the processing class, this handles all of the 
    # pre - processing de speckling, co - reg, and formatting band names
    ee_processing = tbx.eePreProcessing(system_ids)
    ee_processed = ee_processing.runPreProcessing() # this runs the pre processing

    # step 7: Sampled the input images
    # this will generate a feature collection of samples for each image that 
    smpObj = tbx.eeSampling(aoi, images=ee_processed)

    # step 8: is to export to all feature collections to drive
    # configuration is set internally
    smpObj.exportSamplesToDrive(monitor_task=True, project_name='A_Project_Name')

if __name__ == '__main__':
    main()