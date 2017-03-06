setwd('~/Documents/bigValley-Python')

library(ggplot2)

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
      id <- gsub('\\.csv', '', unlist(strsplit(file, "-"))[3])
      thisOne$model = rep(model,nrow(thisOne))
      thisOne$id = rep(id,nrow(thisOne))
      thisOne$iteration <- as.numeric(row.names(thisOne))
      #
      bigOnes[[length(bigOnes) + 1]] <- thisOne
    }
  }
  print(paste(length(bigOnes), 'bigOnes'))
  return(bigOnes)
}

bigOnes <- loadBigOnes('testData')

########
oneBig <- data.frame()
for (df in bigOnes) {
  oneBig <- rbind(oneBig, df)
}
#######
ends <- oneBig[oneBig$maxYears==5000 & !is.na(oneBig$maxYears), ]
df <- oneBig


##############################
######   end plots   #########
##############################
endsWeWant <- ends[ends$model=='LM2' | ends$model=='RF2', ]
endsWeWant$model <- ifelse(endsWeWant$model=='LM2', 'Linear Model', 'Random Forest')

# iterations until big run
ggplot(endsWeWant, aes(x=id, y= iteration - 500, fill=model)) + geom_bar(stat='identity') + ggtitle("Iterations to Stabilize") + ylab('number of learning iterations') + xlab('')

# big runs, length
ggplot(endsWeWant, aes(x=id, y= deadWorld, fill=model)) + geom_bar(stat='identity') + ggtitle("Final Runs") + ylab('years until first extinction') + xlab('')


##############################
######   multiplot   ######### http://www.cookbook-r.com/Graphs/Multiple_graphs_on_one_page_(ggplot2)/
##############################
source('markdown-and-plotting/multiplot.R')
##
endsWeWant <- ends[ends$model=='LM2', ]
#
full <- list()
critters <- list()
counts <- list()

for (id in endsWeWant$id) {
  l <- reshape(df[df$id==id, 8:19],  ###### http://www.ats.ucla.edu/stat/r/faq/reshape.htm
               varying = c("wolfEn", "wolfRe", "wolfFa", "rabbitEn", "rabbitRe", "rabbitFa",
                           "wolfNum", "rabbitNum", "grassNum", "rockNum"), 
               v.names = "number",
               timevar = c("stat"), 
               times = c("wolfEn", "wolfRe", "wolfFa", "rabbitEn", "rabbitRe", "rabbitFa",
                         "wolfNum", "rabbitNum", "grassNum", "rockNum"), 
               new.row.names = NULL,
               direction = "long")
  
  ln <- l[grep('Num', l$stat),]
  lc <- l[grep('En|Re|Fa', l$stat),]
  print(head(l))
  full[[length(full) + 1]] <- ggplot(l, aes(x=iteration, y=number, colour=stat)) + geom_line() + xlim(400,max(l$iteration)) + ylab("starting value") + theme(legend.position="none") + ggtitle(id)
  counts[[length(counts) + 1]] <- ggplot(ln, aes(x=iteration, y=number, colour=stat)) + geom_line() + xlim(400,max(l$iteration)) + theme(legend.position="none") + ggtitle(id)
  critters[[length(critters) + 1]] <- ggplot(lc, aes(x=iteration, y=number, colour=stat)) + geom_line() + xlim(400,max(l$iteration)) + ylab("starting value") + theme(legend.position="none") + ggtitle(id)
}

###### four plot squares
multiplot(plotlist=counts, cols=2)

##############################
###### semi-animated #########
##############################
#
full <- list()
critters <- list()
counts <- list()

for (id in ends$id) {
  l <- reshape(df[df$id==id, 8:19], 
               varying = c("wolfEn", "wolfRe", "wolfFa", "rabbitEn", "rabbitRe", "rabbitFa",
                           "wolfNum", "rabbitNum", "grassNum", "rockNum"), 
               v.names = "number",
               timevar = c("stat"), 
               times = c("wolfEn", "wolfRe", "wolfFa", "rabbitEn", "rabbitRe", "rabbitFa",
                         "wolfNum", "rabbitNum", "grassNum", "rockNum"), 
               new.row.names = NULL,
               direction = "long")
  
  ln <- l[grep('Num', l$stat),]
  lc <- l[grep('En|Re|Fa', l$stat),]
  print(head(l))
  full[[length(full) + 1]] <- ggplot(l, aes(x=iteration, y=number, colour=stat)) + geom_line() + xlim(400,max(l$iteration)) + ggtitle(paste(id, "-", l$model[1]))
  counts[[length(counts) + 1]] <- ggplot(ln, aes(x=iteration, y=number, colour=stat)) + geom_line() + xlim(400,max(l$iteration)) + ggtitle(paste(id, "-", l$model[1]))
  critters[[length(critters) + 1]] <- ggplot(lc, aes(x=iteration, y=number, colour=stat)) + geom_line() + xlim(400,max(l$iteration)) + ggtitle(paste(id, "-", l$model[1]))
}
#
plots <- function(pick = 'full', sleep = 3) { #'full' 'critters' or 'counts'
  if (pick == 'full') {
    for (plot in full) {
      suppressWarnings(print(plot))
      Sys.sleep(sleep)
    }
  } else if (pick == 'critters') {
    for (plot in critters) {
      suppressWarnings(print(plot))
      Sys.sleep(sleep)
    }
  } else if (pick == 'counts') {
    for (plot in counts) {
      suppressWarnings(print(plot))
      Sys.sleep(sleep)
    }
  } else {
    print("INVALIDED PICK: only 'full' 'critters' or 'counts'")
  }
  print("%%%%%%%%% all done. %%%%%%%%%")
}

#plots('full')
plots('critters')
plots('counts')


##########################
###### MANUAL PLOTS ######
##########################
# 
# # wolves vs. rabbits RF2
# g <- ggplot(df[df$model=='RF2', ], aes(x=iteration)) + xlim(499,1000) + ylim(0,max(df$wolfRe)) 
# g <- g + geom_point(aes(x=iteration, y = wolfEn, colour = id), shape = 24)
# g <- g + geom_point(aes(x=iteration, y = rabbitEn, colour = id), shape = 21)
# #g <- g + geom_point(aes(x=iteration, y = wolfRe, colour = id), shape = 2)
# #g <- g + geom_point(aes(x=iteration, y = rabbitRe, colour = id), shape = 1)
# g
# 
# #
# g <- ggplot(df[df$model=='RF2', ], aes(x=iteration)) + xlim(499,1000) + ylim(0,max(df$wolfRe)) 
# 
# for (df in bigOnes){
#   g <- g + geom_line(aes(x=iteration, y = wolfEn, colour = model))
# }
# g
# 
# g <- ggplot(df[df$model=='RF2' | df$model=='LM2', ], aes(x=iteration)) + xlim(400,1000) + ylim(0,max(df$wolfRe)) 
# g <- g + geom_point(aes(x=iteration, y = wolfEn, colour = id), shape = 24)
# g <- g + geom_point(aes(x=iteration, y = rabbitEn, colour = id), shape = 21)
# g
# 
# ###
# g <- ggplot(df[df$model=='RF2', ], aes(x=iteration)) + xlim(400,1000) + ylim(0,max(df$wolfRe))+ ggtitle("RF2 energy")
# g <- g + geom_line(aes(x=iteration, y = wolfEn, colour = id))
# g <- g + geom_line(aes(x=iteration, y = rabbitEn, colour = id))
# g
# 
# g <- ggplot(df[df$model=='LM2', ], aes(x=iteration)) + xlim(400,1000) + ylim(0,max(df$wolfRe)) + ggtitle("LM2 energy")
# g <- g + geom_line(aes(x=iteration, y = wolfEn, colour = id))
# g <- g + geom_line(aes(x=iteration, y = rabbitEn, colour = id))
# g
# 
# #number
# g <- ggplot(df[df$model=='RF2', ], aes(x=iteration)) + xlim(400,1000) + ylim(0,75) + ggtitle("RF2 number")
# g <- g + geom_point(aes(x=iteration, y = wolfNum, colour = id), shape = 24)
# g <- g + geom_point(aes(x=iteration, y = rabbitNum, colour = id), shape = 21)
# g
# 
# g <- ggplot(df[df$model=='LM2', ], aes(x=iteration)) + xlim(400,1000) + ylim(0,75) + ggtitle("LM2 number")
# g <- g + geom_point(aes(x=iteration, y = wolfNum, colour = id), shape = 24)
# g <- g + geom_point(aes(x=iteration, y = rabbitNum, colour = id), shape = 21)
# g
# 
# # plants and rabbits
# g <- ggplot(df[df$model=='RF2', ], aes(x=iteration)) + xlim(400,1000) + ylim(0,max(df$grassNum)) + ggtitle("RF2 number")
# g <- g + geom_point(aes(x=iteration, y = grassNum, colour = id), shape = 8)
# g <- g + geom_jitter(aes(x=iteration, y = rockNum, colour = id), shape = 12, size=3)
# g <- g + geom_point(aes(x=iteration, y = rabbitNum, colour = id), shape = 21)
# g
# 
# g <- ggplot(df[df$model=='LM2', ], aes(x=iteration)) + xlim(400,1000) + ylim(0,max(df$grassNum)) + ggtitle("LM2 number")
# g <- g + geom_point(aes(x=iteration, y = grassNum, colour = id), shape = 8)
# g <- g + geom_jitter(aes(x=iteration, y = rockNum, colour = id), shape = 12, size=3)
# g <- g + geom_point(aes(x=iteration, y = rabbitNum, colour = id), shape = 21)
# g
# 
