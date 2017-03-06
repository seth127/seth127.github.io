setwd('~/Documents/bigValley-Python')

library(ggplot2)

###################
## LOAD THE DATA ##
###################

files <- grep('.csv$', list.files('testData'), value=TRUE)

loadBigOnes <- function(folder) {
  # get files
  files <- grep('.csv$', list.files(folder), value=TRUE)
  # seperate out the ones that end in a 5000 run
  bigOnes <- list()
  for (file in files) {
    # load a file
    thisOne <- read.csv(paste(folder,file,sep='/'))
    if (max(thisOne[,2], na.rm = T) == 5000) {
      names(thisOne) <- c("tests", "maxYears",
                          "firstExt","firstExtStd","deadWorld", "deadWorldStd", "id",
                          "wolfEn", "wolfRe", "wolfFa", "rabbitEn", "rabbitRe", "rabbitFa",
                          "wolfNum", "rabbitNum", "grassNum", "rockNum")
      #
      model <- unlist(strsplit(file, "-"))[2]
      runId <- gsub('\\.csv', '', unlist(strsplit(file, "-"))[3])
      thisOne$model = rep(model,nrow(thisOne))
      thisOne$runId = rep(runId,nrow(thisOne))
      thisOne$iteration <- as.numeric(row.names(thisOne))
      #
      bigOnes[[length(bigOnes) + 1]] <- thisOne
    }
  }
  print(paste(length(bigOnes), 'bigOnes'))
  return(bigOnes)
}

bigOnes <- loadBigOnes('testData')
#
oneBig <- data.frame()
for (df in bigOnes) {
  oneBig <- rbind(oneBig, df)
}
#
ends <- oneBig[oneBig$maxYears==5000 & !is.na(oneBig$maxYears), ]
ends <- ends[grep('2',ends$model),]
#
simIDs <- gsub("[ \\']", "", as.character(ends$id)) # should get the simID for each 5,000 run

###########################
## PLOT THE SIM YOU WANT ##
###########################

#
theSimYouPicked <- simIDs[6] # either manually pick or just cycle through the simIDs
#
thisSim <- read.csv(paste("testData/YearStats/paramStats-", theSimYouPicked, ".csv", sep=""))
varCols <- names(thisSim)
thisSim$iteration <- as.numeric(row.names(thisSim))

lts <- reshape(thisSim, 
               varying = varCols, 
               v.names = "number",
               timevar = c("stat"), 
               times = varCols, 
               new.row.names = NULL,
               direction = "long")

# sub whatever you want for 'Count' below
ggplot(lts[grep('Count',lts$stat),], aes(x=iteration, y=number, colour = stat)) + geom_point()

# or for 'wolf' to see stats (but NOT count or fatigue)
ggplot(lts[grepl('wolf',lts$stat) & !grepl('Count|Fatigue', lts$stat),], aes(x=iteration, y=number, colour = stat)) + geom_point()

# (random examples)
ggplot(lts[grep('Repro',lts$stat),], aes(x=iteration, y=number, colour = stat)) + geom_point()
ggplot(lts[grep('Repro|Energy',lts$stat),], aes(x=iteration, y=number, colour = stat)) + geom_point()
ggplot(lts[grepl('rabbit',lts$stat) & !grepl('Count', lts$stat),], aes(x=iteration, y=number, colour = stat)) + geom_point()
ggplot(lts[grepl('grass',lts$stat) & !grepl('Count|Energy', lts$stat),], aes(x=iteration, y=number, colour = stat)) + geom_point()
