"Macintosh HD/⁨Users/⁨Seth/⁨Documents/⁨seth127.github.io/⁨drinkBase/⁨data"

## add drinks
seth_root = "~/Documents/seth127.github.io/drinkBase/data/"
seth_path = paste0(seth_root, "recipe.csv")
db_root = "~/Documents/drinkbase/deployment/pgsql/data/"
db_path = paste0(db_root, "recipes.csv")
seth_df = read.csv(seth_path, stringsAsFactors = F)
db_df = read.csv(db_path, stringsAsFactors = F)

new_df = seth_df[!(seth_df$name %in% db_df$name), ]
new_drinks = unique(new_df$name)
print(new_drinks)
naw = c("Bourbon Manhattan","Champs Elysees","20th Century Cocktail","Original Cosmopolitan","Classic Daiquiri","Blood and Sand")
new_df = new_df[!(new_df$name %in% naw), names(db_df)]

db_df = rbind(db_df, new_df)

#write.csv(db_df, db_path, quote = F, row.names = F)

## add ingredients
seth_ing = read.csv(paste0(seth_root, "chemistry.csv"), stringsAsFactors = F)
db_ing = read.csv(paste0(db_root, "ingredients.csv"), stringsAsFactors = F)
new_ing = seth_ing[!(seth_ing$name %in% db_ing$name), ]
new_ing_names = unique(new_ing$name)
print(new_ing_names)

## prep
seth_prep = read.csv(paste0(seth_root, "prep.csv"), stringsAsFactors = F)
prep_path = paste0(db_root, "prep.csv")
db_prep = read.csv(prep_path, stringsAsFactors = F)
new_prep = seth_prep[(seth_prep$name %in% new_df$name), ]
new_prep_names = unique(new_prep$name)
print(new_prep_names)

# add garnishes

new_prep$garnish = NA
for (i in 1:nrow(new_prep)) {
  d = new_prep$name[i]
  new_prep$garnish[i] = paste(new_df[(new_df$name==d) & (new_df$unit=='garnish'), 'ingredient'], collapse = " & ")
  if (grepl("Pour all ingredients except garnishes", new_prep$notes[i])) {
    new_prep$notes[i] = ''
  }
  
}
new_prep = new_prep[, names(db_prep)]

db_prep = rbind(db_prep, new_prep)

#write.csv(db_prep, prep_path, quote = F, row.names = F)
