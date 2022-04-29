
persist.fpc.scores <- function(
    dir.scores = NULL
    ) {

    thisFunctionName <- "persist.fpc.scores";
    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###");
    cat(paste0("\n",thisFunctionName,"() starts.\n"));

    require(arrow);
    require(terrainr);

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    years <- gsub(
        x = unique(stringr::str_extract(
            string  = list.files(path = dir.scores, pattern = "^scores-"),
            pattern = "-[0-9]{4}-"
            )),
        pattern     = "-",
        replacement = ""
        );
    years <- sort(as.integer(years));

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    for ( temp.year in years ) {

        temp.pattern <- paste0("^scores-",temp.year,"-");
        score.files  <- list.files(path = dir.scores, pattern = temp.pattern);

        ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
        parquet.scores <- paste0("DF-scores-",temp.year,".parquet");
        if ( file.exists(parquet.scores) ) {
            # DF.scores <- arrow::read_parquet(file = parquet.scores);
        } else {
            DF.scores <- data.frame();
            for ( temp.score.file in score.files ) {
                DF.batch  <- arrow::read_parquet(file = file.path(dir.scores,temp.score.file));
                DF.scores <- rbind(DF.scores,DF.batch);
                base::remove(list = c('DF.batch'));
                base::gc();
                }
            arrow::write_parquet(
                sink = parquet.scores,
                x    = DF.scores
                );
            base::remove(list = c('DF.scores'));
            base::gc();
            } # if ( file.exists(parquet.scores) ) { ... } else { ... }
        } # for ( temp.year in years ) { ... }

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    cat(paste0("\n",thisFunctionName,"() quits."));
    cat("\n### ~~~~~~~~~~~~~~~~~~~~ ###\n");
    return( NULL );

    }

##################################################