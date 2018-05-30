setwd("~/Documents/seth127.github.io/drinkFinder")
library(dplyr)
library(ggplot2)
library(tidyr)

recipe <- read.csv("data/recipe.csv", stringsAsFactors = F)
recipe$unit[grep("teas", recipe$unit)] <- 'tsp'

prep <- read.csv("data/prep.csv", stringsAsFactors = F)
chem <- read.csv("data/chemistry.csv", stringsAsFactors = F)
chem[is.na(chem)] <- 0

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
df <- merge(df, prep[,1:3], all.x=T, by.x="name", by.y='drink')
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

write.csv(df, "data/all_drinks.csv", row.names = F, quote = F)
write.csv(df[df$style != '', ], "data/style_drinks.csv", row.names = F, quote = F)

#### then plot
#temp_df <- df
#temp_df <- df[order(df$acid, decreasing = T)[1:20], ] # the 20 most acidic
temp_df <- df[df$name %in% unique(recipe[grep("whiskey", recipe$ingredient), 'name']), ]
#temp_df <- df[df$name %in% unique(recipe[grep("gin", recipe$ingredient), 'name']), ]
#temp_df <- df[df$name %in% unique(recipe[grep("tequila", recipe$ingredient), 'name']), ]
ggplot(temp_df, aes(x = name, y = alcohol)) + 
  geom_point(aes(size=oz, colour = style)) + 
  geom_point(aes(size=oz*0.25, alpha=acid), shape=8) + 
  geom_point(aes(size=sugar*100), shape=1, alpha=0.5) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) + 
  scale_size(range=c(3,18)) + xlab("") + ylab("ABV") + scale_y_continuous(labels = scales::percent) +
  ggtitle("Whiskey drinks")

write.csv(temp_df[order(temp_df$alcohol, decreasing = F), ], "data/whiskey_drinks.csv", row.names = F, quote = F)

##### extra pieces
df$ingredients <- NA
for (i in 1:nrow(df)) {
  df$ingredients[i] <- paste(recipe[recipe$name==df$name[i], "ingredient"], collapse = "|")
}

df$selected <- rep(0, nrow(df))
df$selected[df$name %in% unique(recipe[grep("whiskey", recipe$ingredient), 'name'])] <- 1
write.csv(df, "data/selected_whiskey.csv", row.names = F, quote = F)

df$selected <- rep(0, nrow(df))
df$selected[df$name %in% unique(recipe[grep("gin", recipe$ingredient), 'name'])] <- 1
write.csv(df, "data/selected_gin.csv", row.names = F, quote = F)

df$selected <- rep(0, nrow(df))
df$selected[df$name %in% unique(recipe[grep("lime", recipe$ingredient), 'name'])] <- 1
write.csv(df, "data/selected_lime.csv", row.names = F, quote = F)

