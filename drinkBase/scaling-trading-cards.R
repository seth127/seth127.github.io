library(ggplot2)

old <- function(thisNum, mult) {
  min(570, max(30, 630-(thisNum*mult)))
}

new <- function(thisNum, mult) {
  min(130, max(0, (thisNum*mult)))
}


thePick = 'alcohol'
#df$tempold <- sapply(df[, thePick], old, 1800)
df$tempnew <- sapply(df[, thePick], new, 375)

#ggplot(df, aes(x=tempold)) + geom_histogram()
ggplot(df, aes(x=tempnew)) + geom_histogram()


thePick = 'sugar'
#df$tempold <- sapply(df[, thePick], old, 5000)
df$tempnew <- sapply(df[, thePick], new, 800)

#ggplot(df, aes(x=tempold)) + geom_histogram()
ggplot(df, aes(x=tempnew)) + geom_histogram()


thePick = 'acid'
#df$tempold <- log(sapply(df[, thePick], old, 100000))
df$tempnew <- sapply(df[, thePick], new, 9000)

#ggplot(df, aes(x=acid)) + geom_histogram()
ggplot(df, aes(x=tempnew)) + geom_histogram()
