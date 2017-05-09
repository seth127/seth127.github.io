setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
library(tidyr)
library(ggplot2)
library(dplyr)


df <- read.csv('plotDataRF/epochStats.csv')

## returns df, with stats summarised by groups of scaleFactor
scaleEpochs <- function(df, scaleFactor=10, learningCutoff=1) {
  df <- df[learningCutoff:nrow(df),]
  # create label vector (scale Factor is number of groups created)
  labels <- numeric()
  for (num in 1:scaleFactor) {
    labels <- c(labels, rep(num,ceiling(nrow(df)/scaleFactor)))
  }
  # assign label vector to column
  df$labels <- labels[1:nrow(df)]
  # convert to long format
  df <- gather(df[,c(5,8:18)], 'stat','value',-labels)
  # summarise each stat by label
  df <- summarise(group_by(df, labels, stat), value=mean(value))
  #
  df
}

# ggplot(newDF[scaleEpochs(df,10), aes(x=labels, y=value, colour=stat)) + geom_point()

# looking at number and deadWorld only
newDF <- scaleEpochs(df,10)
ggplot(newDF[grep('dead|Num',newDF$stat),], aes(x=labels, y=value, colour=stat)) + geom_point()

# write back to csv
#write.csv(newDF, 'plotDataRF/epochStats-long.csv')

##### change all files in this directory
f <- list.files('plotData-epochs')

for (file in f) {
  df <- read.csv(paste('plotData-epochs', file, sep='/'))
  print(nrow(df))
  names(df) <- c('tests','years','firstExt','firstExtSTD','deadWorld','deadWorldSTD','id','wolfEn','wolfRe','wolfFa','rabbitEn','rabbitRe','rabbitFa','wolfNum','rabbitNum','grassNum','debrisNum')
  newDF <- scaleEpochs(df,10,475)
  newName <- paste('plotData-epochs/epochStats-', unlist(strsplit(file, '-'))[3], sep='')
  write.csv(newDF, newName, row.names=F)
}