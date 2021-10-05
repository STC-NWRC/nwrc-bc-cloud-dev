
library(raster)

# access rasterfile
filename <- "/home/rhamilton/projects/nwrc-bc-cloud-dev/ryan/R/raster/data/S1_20180411_IW.tif"

# create a raster brick
b <- brick(filename)

# cast brick obj to data frame
brickdf <- as.data.frame(b)


