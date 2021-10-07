# Import Moduels

library(dplyr)
library(tidyr)
library(data.table)
library(raster)
library(rgdal)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# read in file names of csvs
files <- list.files(path = "./data", full.names = TRUE)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# read in csvs by apllying a read.csv functions to the files list
dfs <- lapply(files, read.csv)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# combine data frames into a single one
combine <- data.table::rbindlist(dfs)

sorted <- combine[order(master_lat_lon),]

# Step 4: Split the master_lat_lon col into lat and lon
lat_lon <- sorted %>% separate(master_lat_lon, c("lat", "lon"), "_")

# Step 5: cast lat lon columns to float
lat_lon$x <- as.numeric(lat_lon$x)
lat_lon$y <- as.numeric(lat_lon$y)

ch1 <- lat_lon[, c(1,2,4)]

# Step 6: use rasterFromXZY to cast dataframe to Raster object
r <- rasterFromXYZ(ch1, res = c(10, 10), digits = 10)

rdf <- as.data.frame(r)

# Step 7: Write Raster out to disk
#rf <- writeRaster(r, filename = './test.tif', format = 'GTiff', overwrite = TRUE)  
