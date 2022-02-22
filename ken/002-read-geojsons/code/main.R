
command.arguments <- commandArgs(trailingOnly = TRUE);
data.directory    <- normalizePath(command.arguments[1]);
code.directory    <- normalizePath(command.arguments[2]);
output.directory  <- normalizePath(command.arguments[3]);

print( data.directory );
print( code.directory );
print( output.directory );

print( format(Sys.time(),"%Y-%m-%d %T %Z") );

start.proc.time <- proc.time();

# set working directory to output directory
setwd( output.directory );

##################################################
require(fpcFeatures);

require(arrow);
require(jsonlite);
# require(doParallel);
# require(foreach);
# require(ggplot2);
# require(ncdf4);
# require(openssl);
# require(parallel);
# require(raster);
# require(terra);
# require(terrainr);
# require(sf);
# require(stringr);
# require(tidyr);

# source supporting R code
code.files <- c(
    "getData-geojson.R",
    "preprocess-training-data.R"
    );

for ( code.file in code.files ) {
    source(file.path(code.directory,code.file));
    }

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
dir.geoson <- file.path(data.directory,"training-data-geojson");

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
DF.training <- getData.geojson(
    input.directory = dir.geoson,
    parquet.output  = "DF-training.parquet"
    );

DF.training <- preprocess.training.data(
    DF.input = DF.training
    );

cat("\nstr(DF.training)\n");
print( str(DF.training)   );

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

##################################################
print( warnings() );

print( getOption('repos') );

print( .libPaths() );

print( sessionInfo() );

print( format(Sys.time(),"%Y-%m-%d %T %Z") );

stop.proc.time <- proc.time();
print( stop.proc.time - start.proc.time );
