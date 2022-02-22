
getData.colour.scheme <- function() {
    DF.colour.scheme <- data.frame(
        land_cover = c("marsh",  "swamp",  "water",  "forest", "ag",     "shallow_water"),
        colour     = c("#000000","#E69F00","#56B4E9","#009E73","#F0E442","red"          )
        );
    rownames(DF.colour.scheme) <- DF.colour.scheme[,"land_cover"];
    return(DF.colour.scheme);
    }
