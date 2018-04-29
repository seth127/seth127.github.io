#! usr/bin/env python3
# drinkFinder.py

import sqlite3

drinkBase = sqlite3.connect('drinkBase.db')
SQL = drinkBase.cursor()

# populates table where drink includes an ingredient
print('Welcome to drinkFinder!')
included = (input('Enter an ingredient you\'d like to include:\n'),)
SQL.execute("SELECT DISTINCT name FROM drinkIngredients WHERE ingredient like ?", included)
grouping = SQL.fetchall()
drinkList = set()
for i in grouping:
    drinkList.add(i[0],)

# intersect original list with added drinks
added = (input('Enter another ingredient you\'d like to include (or type "next" to move on):\n'),)
addList = set()
while added != ('next',):
    SQL.execute("SELECT DISTINCT name FROM drinkIngredients WHERE ingredient like ?", added)
    addGrouping = SQL.fetchall()
    for i in addGrouping:
        addList.add(i[0],)
    added = (input('Enter another ingredient you\'d like to include (or type "next" to move on):\n'),)
newDrinkList = set()
if len(addList)==0:
    newDrinkList = drinkList
else:
    newDrinkList = (drinkList & addList)


# TODO - create optional ingredients


#TODO - write script to create list of unwanted ingredients
excluded = (input('What do you want to exclude? (or type "next" to move on): \n'),)
excludeList = set()
while excluded != ('next',):
    SQL.execute("SELECT DISTINCT name FROM drinkIngredients WHERE ingredient like ?", excluded)
    excludedGrouping = SQL.fetchall()
    for i in excludedGrouping:
        excludeList.add(i[0],)
    excluded = (input('What do you want to exclude? (or type "next" to move on): \n'),)
finalDrinkList = set()
finalDrinkList = newDrinkList.difference(excludeList)
if len(finalDrinkList)==0:
    print('Your search returned no results')
else: print('finalDrinkList (the end product!): ', finalDrinkList)

# use these outputs for testing & debugging
# print('original drinkList: ', drinkList)
# print('addList: ', addList)
# print('newDrinkList: ', newDrinkList)
# print('excludeList: ', excludeList)
# print('finalDrinkList (the end product!): ', finalDrinkList)
