
preprocess.training.data <- function(
    DF.input = NULL
    ) {

    thisFunctionName <- "preprocess-training-data";

    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###");
    cat(paste0("\n# ",thisFunctionName,"() starts.\n"));

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    DF.output <- DF.input;

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    colnames(DF.output) <- tolower(colnames(DF.output));
    colnames(DF.output) <- gsub(x = colnames(DF.output), pattern = "^class$", replacement = "land.cover");
    colnames(DF.output) <- gsub(x = colnames(DF.output), pattern = "^point_x$", replacement = "longitude");
    colnames(DF.output) <- gsub(x = colnames(DF.output), pattern = "^point_y$", replacement =  "latitude");
    colnames(DF.output) <- gsub(x = colnames(DF.output), pattern = "^vv$", replacement = "VV");
    colnames(DF.output) <- gsub(x = colnames(DF.output), pattern = "^vh$", replacement = "VH");

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    DF.output[,'date']       <- as.Date(DF.output[,'date']);
    DF.output[,'land.cover'] <- factor(DF.output[,'land.cover']);

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    colnames.to.retain <- c(
        'latitude',
        'longitude',
        'land.cover',
        'date',
        'VV',
        'VH'
        );

    DF.output <- DF.output[,colnames.to.retain];

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    DF.output <- DF.output[order(DF.output$latitude,DF.output$longitude,DF.output$date),];

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    cat(paste0("\n# ",thisFunctionName,"() exits."));
    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###\n");
    return( DF.output );

    }

##################################################
