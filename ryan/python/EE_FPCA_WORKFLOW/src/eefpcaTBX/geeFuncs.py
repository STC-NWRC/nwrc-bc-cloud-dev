
import ee

ee.Initialize()

class FeatureCollection(ee.FeatureCollection):
    """This Class us used to serialize collection ids or shapefiles
    into 
    """
    def __init__(self, args, opt_column=None):
        self.args = args
        self.opt_column = opt_column
        super().__init__(self.args, opt_column=opt_column)

    @property
    def args(self):
        return self.__args

    @args.setter
    def args(self, args):
        # first block is for inhertance
        if isinstance(args, dict):
           self.__args = args

        # This handles if the constructor is a instance of the custom class
        elif isinstance(args, FeatureCollection):
            self.__args = args

        # this block gets exicuted initally and validates the constructor before
        # inhertence takes place
        else:
            if args.endswith('.shp'):
                self.__args = self.__cast_to_ee_feature(args)
            else:
                self.__args = args

    def __cast_to_ee_feature(self, arg:str) -> list:
        """Helper function to help cast shapefile to ee Feature"""
        import shapefile
        
        with shapefile.Reader(arg) as shp:
            geojson = shp.__geo_interface__

            # test to make sure we can indeed serialize the file to EE sucessfully
            if len(geojson['features']) > 5000:
                raise ValueError("Shapefile needs to have less than 5000 rows")

            # Make sure the projection is usin lat lon
            coords = geojson['features'][0]['geometry']['coordinates']
            x,y = abs(coords[0]), abs(coords[1])
            if x > float(180) or x < float(0):
                raise ValueError
            elif y > float(90) or y < float(0):
                raise ValueError

            features = geojson['features']
            
            return [ee.Feature( _ ) for _ in features]

class S1Collection(ee.ImageCollection):
    """This Class is used to extract the inital Collection to be used in Trend Analysis"""
    def __init__(self, aoi, years:list, months:list, relative_orbit=None):
        super().__init__('COPERNICUS/S1_GRD')
        self.aoi            = aoi
        self.years          = years
        self.months         = months
        self.relative_orbit = relative_orbit
        
        # TODO add documentation to this class and explain what the paramaters are for

    @property
    def years(self):
        return self.__years

    @years.setter
    def years(self, years):
        self.__years = years

    @property
    def months(self):
        return self.__months

    @months.setter
    def months(self, months):
        self.__months = months

    @property
    def aoi(self):
        return self.__aoi

    @aoi.setter
    def aoi(self, aoi):
        if isinstance(aoi, str):
            self.__aoi = ee.FeatureCollection(aoi).geometry().bounds()
        else:
            self.__aoi = aoi

    @property
    def relative_orbit(self):
        return self.__relative_orbit

    @relative_orbit.setter
    def relative_orbit(self, relative_orbit:int):
        self.__relative_orbit = relative_orbit

    @property
    def dates(self) -> list:
        # need to turn this into a list of tuples
        fmt = []
        for year in self.years:
            for month in self.months:
                fmt.append(f'{year}-{month}')
        return list(zip(fmt[::2], fmt[1::2]))

    @property
    def eefilters(self):
        """This is where the base filters are serialzed to ee objs"""
        filters =  {
            'orbit': ee.Filter.eq('orbitProperties_pass', 'ASCENDING'),
            'mode': ee.Filter.eq('instrumentMode', 'IW')
        }
        
        filters['rel_orb'] = ee.Filter.eq('relativeOrbitNumber_start', self.relative_orbit)\
            if self.relative_orbit is not None else None

        return ee.Filter(list(filters.values()))

    @property
    def image_collection(self) -> dict:
        collections = {}
        for index, date in enumerate(self.dates):
            imgCol = self.filterBounds(self.aoi).\
                filterDate(*date).filter(self.eefilters).\
                    select(['VV', 'VH'])
            collections.update({self.years[index]: imgCol})
        return collections

    @property
    def relativeOrbitNumbers(self):
        orbitNumbers = lambda x: x.aggregate_array('relativeOrbitNumber_start').distinct()
        orbits = [orbitNumbers(v) for v in self.image_collection.values()]
        client_side = [orb.getInfo() for orb in orbits]
        flatten = [item for sublist in client_side for item in sublist]
        return list(set(flatten))

    # Private functions
    def __cast_to_list(self, collection:dict) -> dict:
        """Used to extract image system:ids from each image returned in the query"""
        _ = {}
        for year, collection in collection.items():
            img_list = collection.toList(collection.size())
            id_list = img_list.map(lambda x: ee.Image(x).get('system:id'))
            _.update({year:id_list})

        return {k:v.getInfo() for k,v in _.items()}

    # Public Acessors
    def fmtCollections(self):
        """This returns a python list of image collection there will be one collection
            for every date step that was specified in the construction of the object
        """
        return self.image_collection

    def getSystemIds(self):
        """Returns system ids for the entire returned collection"""
        return self.__cast_to_list(self.image_collection)

class eePreProcessing:
    """class for handleing Pre processing of ee images"""
    def __init__(self, system_ids:dict) -> None:
        self.system_ids      = system_ids
        self._formated_bands = {}
        self._de_speckeled   = {}
        self._co_regiseterd  = {}

    @property
    def system_ids(self):
        return self.__system_ids

    @system_ids.setter
    def system_ids(self, system_ids:dict):
        """convert the system id to a python list of ee.Image"""
        self.__system_ids = {k: [ee.Image(i) for i in v] for k,v in system_ids.items()}

    @property
    def speckel_filter(self):
        return ee.Kernel().square(5)

    def __format_bands(self):
        for k,v in self.system_ids.items():
            fmt = [self.__formatter(x) for x in v]
            self._formated_bands.update({k: fmt})

    def __formatter(self, image:ee.Image):
        
        bandNames = image.bandNames()
        date = image.date().format('YYYY_MMdd')
        mode = image.get('instrumentSwath')
        rel  = ee.Number(image.get('relativeOrbitNumber_start')).int().format('%1d')

        # nested function to map to the image
        def formatBandNames(element):
            date_str = ee.String(date)
            mode_str = ee.String(mode)
            rel_str  = ee.String(rel)
            
            Sensor   = ee.String('S1_')
            date_fmt = date_str.cat('_')
            mode_fmt = mode_str.cat('_')
            rel_fmt  = rel_str.cat('_')
            
            fmt1 = Sensor.cat(mode_fmt)
            fmt2 = fmt1.cat(date_fmt)
            fmt3 = fmt2.cat(rel_fmt)
            
            return fmt3.cat(element)

        fmt_bands = bandNames.map(formatBandNames)
        
        return image.select(bandNames, fmt_bands)

    def __co_regester_images(self):
        tmp = {}
        for k, v in self._de_speckeled.items():
            foreman  = v.pop(0)

            config = {
                'referenceImage': foreman,
                'maxOffset': 1.0,
            }
            
            register = lambda x: x.register(**config)
            
            workers = [register( _ ) for _ in v]
            workers.insert(0, foreman)
            self._co_regiseterd.update({k: workers})

    def __apply_de_speckling(self):
        boxcar = ee.Kernel.square(5)
        self._de_speckeled.update({k: [x.convolve(boxcar) for x in v] for k,v in self._formated_bands.items()})

    def runPreProcessing(self) -> dict:
        """Formats bands, applies 5x5 boxcar spatial filter and coregisters images"""
        # format the band names
        self.__format_bands()
        # apply speckle filter
        self.__apply_de_speckling()
        # coregister images
        self.__co_regester_images()

        return self._co_regiseterd

class eeSampling(FeatureCollection):
    """
    1) sample all images in the input images dict -> feature collection for each image
    2) try to convert to client side dict like object -> extract just the features
    3) add method to write out return a properly formatted geojson
    """

    def __init__(self, args, images:dict, opt_column=None):
        self.images = images
        super().__init__(args, opt_column=opt_column)

    @property
    def sampleConf(self):
        conf = {
            'collection': self,
            'properties': None,
            'scale': 10,
            'tileScale': 16,
            'geometries':True
        }
        return conf

    @property
    def samples(self):
        return self.__generate_samples()

    def __generate_samples(self) -> dict:
        """Helper function to generate samples"""
        samples = {}
        for k,v in self.images.items():
            
            # k = year
            # v = list of images
            fc = [image.sampleRegions(**self.sampleConf) for image in v]
            
            # add a relorbit prop each feature collection
            prop_to_add = [image.get('relativeOrbitNumber_start') for image in v]
            
            mapped = []
            for index, f in enumerate(fc):
                prop = prop_to_add[index]
                f.map(lambda element: element.set({'relObit': prop}))
                mapped.append(f)

            samples.update({k: mapped})
        return samples

    def getSamples(self, to_client=False) -> dict:
        if not to_client:
            return self.samples
        else:
            pass
            # try to convert feature collection to client side object
            # _ = {}
            # for k,v in self.__sample.items():
            #     fc = [col.getInfo() for col in v]
            #     _.update({k: fc})
            # return _

    def exportSamplesToDrive(self, monitor_task=False, project_name=None):
        from datetime import datetime
        # this is the base configuration for table to drive
        conf = {
            'collection': None, 
            'description': None,
            'folder': None,
            'fileFormat': 'GeoJSON',
            'selectors': None,
        }

        # create the folder name
        now = datetime.now()
        fmt_time = now.strftime("%Y%m%d_%H%I%M")
        if project_name == None:
            folder = f'eeTrend_Analysis_{fmt_time}'
        else:
            folder = f'{project_name}_{fmt_time}'
    
        conf['folder'] = folder

        task_que = []
        # create a task for each collection in each year
        for k,v in self.samples.items():
            total = len(v)
            for index, collection in enumerate(v, start=1):
                desc = f'{k}_{index}_of_{total}'
                # update the config
                conf['collection']  = collection
                conf['description'] = desc

                task = ee.batch.Export.table.toDrive(**conf)
                task.start()
                task_que.append(task)

        if monitor_task:
            self.__monitor(task_que)

    def exportSamplesToCloud(self, bucket):
        
        conf = {
            'collection': None,
            'desciption': None, 
            'bucket': bucket,
            'fileNamePrefix': 'TrainingData/',
            'fileFormat': 'GeoJSON'
        }

        for k,v in self.samples.items():
            total = len(v)
            for index, collection in enumerate(v,start=1):
                desciption = f'{k}_{index}_of_{total}'
                conf['collection'] = collection
                conf['desciption'] = desciption
                task = ee.batch.Export.table.toCloudStorage(**conf)
                task.start()

    def __monitor(self, que: list):
        import time
        print("Tasks Exporting to Drive")
        while(any([t.active() for t in que])):
            time.sleep(30)
        print('All Exports Complete')
