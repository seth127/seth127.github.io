recipe <- read.csv("~/Documents/drinkBase-Seth/drinkBase-Seth-edits1.csv", stringsAsFactors = F)

drink <- recipe[!duplicated(recipe$name),]
write.csv(drink[,'name'], "~/Documents/drinkBase-Seth/prep.csv", row.names = F, quote = F)

ing <- recipe[!duplicated(recipe$ingredient),]
ing <- ing[-grep("garnish|top|dash|each|rim|slice", ing$unit), ]
write.csv(ing[,'ingredient'], "~/Documents/drinkBase-Seth/chemistry.csv", row.names = F, quote = F)

