# Build Raster
This package will take csvs as input. csv's must represent an image. each row in the csv corresponds to the centroid of a cell in an image. To use this you will need to point the run.bat to the directory that holds the csv's. by running this bat file it takes the csv's and convert them into correspoinding feature classes.

After run.bat has finished running. you will need to run build-components.bat this will build the individual bands of the fpc images.

# <em>NOTE!!!</em> 
<em>These sets of batch files is entended to run on a computer that has ARCGIS PRO installed on it. If you do not have ARCGIS Pro install on your machine this will not run as expected</em>
