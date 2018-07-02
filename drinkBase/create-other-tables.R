setwd("~/Documents/seth127.github.io/drinkBase")
suppressMessages(library(dplyr))
suppressMessages(library(ggplot2))
suppressMessages(library(tidyr))

# load data
print("loading data/recipe.csv")
recipe <- read.csv("data/recipe.csv", stringsAsFactors = F)
recipe$unit[grep("teas", recipe$unit)] <- 'tsp'

print("loading data/prep.csv")
prep <- read.csv("data/prep.csv", stringsAsFactors = F)
print("loading data/chemistry.csv")
chem <- read.csv("data/chemistry.csv", stringsAsFactors = F)
chem[is.na(chem)] <- 0

# create stats df
print("creating stats")
stats <- merge(recipe[grep("oz|tsp|tbl|cube", recipe$unit), 2:5], chem[, c(1,3:5)])

# convert all to oz
stats$oz <- stats$amount

for (i in 1:nrow(stats)) {
  if (stats$unit[i] == "tsp") {
    stats$oz[i] <- stats$oz[i] * 0.166667
  } else if (stats$unit[i] == "tbl") {
    stats$oz[i] <- stats$oz[i] * 0.5
  } else if (stats$unit[i] == "cube") {
    stats$oz[i] <- stats$oz[i] * 0.125
  }
}

# create df
df <- select(stats, -c(unit))

# multipy out oz by ingredients
df$alcohol <- df$alcohol * df$oz
df$sugar <- df$sugar * df$oz
df$acid <- df$acid * df$oz

# roll up to drink level
df <- group_by(df, name) %>% summarise(alcohol = sum(alcohol),
                                       sugar = sum(sugar),
                                       acid = sum(acid),
                                       oz = sum(oz))

# join in prep to get style
df <- merge(df, prep[,1:3], all.x=T, by.x="name", by.y='name')
# prettify
df$style <- as.factor(df$style)

# add ice melt
df$melt <- NA
for (i in 1:nrow(df)) {
  if (df$style[i] == "built") {
    df$melt[i] <- .2
  } else if (df$style[i] == "stirred") {
    df$melt[i] <- .3
  } else if (df$style[i] == "shaken") {
    df$melt[i] <- .35
  } else if (df$style[i] == "bubbly") {
    df$melt[i] <- 0.1
  } else if (df$style[i] == "fizz") {
    df$melt[i] <- 0.33
  } else if (df$style[i] == "swizzle") {
    df$melt[i] <- .4
  } else {
    df$melt[i] <- .28
  }
}
df$oz <- df$oz + (df$oz * df$melt)

# convert to percentages
df$alcohol <- df$alcohol / df$oz
df$sugar <- df$sugar / df$oz
df$acid <- df$acid / df$oz
df$acid <- ifelse(df$acid > quantile(df$acid, 0.99), quantile(df$acid, 0.99), df$acid) # acid hack

df$name <- as.factor(df$name)
df$name <- reorder(df$name, df$alcohol)

df <- df[order(df$alcohol, decreasing = F), ]

# add ingredient string for viz display
df$ingredients <- NA
for (i in 1:nrow(df)) {
  df$ingredients[i] <- paste(recipe[recipe$name==df$name[i], "ingredient"], collapse = "|")
}

# write out csv's
print("writing data/all_drinks.csv")
write.csv(df, "data/all_drinks.csv", row.names = F, quote = F)
print("writing data/style_drinks.csv")
write.csv(df[df$style != '', ], "data/style_drinks.csv", row.names = F, quote = F)

print("All done.")
