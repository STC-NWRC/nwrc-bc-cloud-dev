FROM continuumio/miniconda3

RUN apt-get update \
    && apt-get --yes install wget jq git \
    && rm -rf /var/lib/apt/lists/*

# Default environment
RUN conda install --quiet --yes \
      -c conda-forge \
      "r-cowplot" \
      "r-dplyr" \
      "r-fda" \
      "r-ggplot2" \
      "r-logger" \
      "r-ncdf4" \
      "r-R6" \
      "r-readr" \
      "r-stringr" \
      "r-tidyr" \
      "r-doParallel" \
      "r-foreach" \
      "r-openssl" \
      "r-units" \
      "r-base64enc" \
      "r-gdalUtils" \
      "r-httr" \
      "r-magick" \
      "r-png" \
      "r-raster" \
      "r-sf" \
    && conda clean --all -f -y

    # "r-arrow" \

COPY fpcFeatures_0.0.0.0001.tar.gz /fpcFeatures_0.0.0.0001.tar.gz
RUN R CMD INSTALL --clean --no-html --no-docs --use-vanilla fpcFeatures_0.0.0.0001.tar.gz

#COPY terrainr_0.5.0.tar.gz /terrainr_0.5.0.tar.gz
#RUN R CMD INSTALL --clean --no-html --no-docs --use-vanilla terrainr_0.5.0.tar.gz

