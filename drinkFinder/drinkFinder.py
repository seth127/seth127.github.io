#! usr/bin/env python3
'''
drinkFinderGUI.py
Provides a list of drinks based on ingredients on hand

To use:
enter desired ingredients in boxes below "Included ingredients"
enter ingredients you don't want below "Excluded ingredients"
click "Get me drunk" to get drunk

'''
from tkinter import *
import sqlite3

# main:
window = Tk()
window.title('drinkFinder: getting you drunk since 2018')
window.configure(background='white')

# master variables
masterFont = ('didot', 18, 'bold roman')
drinkClickerFont = ('didot', 18, 'bold underline roman')

# formatting & alignment for included ingredient boxes
inclusionRow = 0
inclusionColumn = 0
inclusionWidth = 10 # width of text boxes
inclusionSticky = W # horizontal alignment
inclusionBg = 'white' # background color
inclusionRelief = 'flat'

# formatting & alignment for included ingredient boxes
exclusionRow = inclusionRow + 5
exclusionColumn = 0
exclusionWidth = 10 # width of text boxes
exclusionSticky = W # horizontal alignment
exclusionBg = 'white' # background color
exclusionRelief = inclusionRelief

# alignment for buttons, etc.
possibleDrinkRow = exclusionRow + 5
possibleDrinkHeight = 1
possibleDrinkColumn = 0
possibleDrinkSticky = W

recipeRow = possibleDrinkRow
recipeHeight = 10
recipeWidth = 25
recipeColumn = 1
recipeSticky = W

getMeDrunkRow = 6
getMeDrunkColumn = 1
getMeDrunkSticky = W

exitRow = possibleDrinkRow+possibleDrinkHeight+1
exitColumn = 0

# connection to drinkBase.db
drinkBase = sqlite3.connect('drinkBase.db')
drinkBase.row_factory = lambda cursor, row: row[0]
cursor = drinkBase.cursor()

# create drinkDictionary
cursor.execute('SELECT name FROM ingredients GROUP BY name')
drinkList = []
drinkList = cursor.fetchall()
drinkDictionary = {}
for name in drinkList:
    name = name,
    cursor.execute('SELECT ingredient FROM ingredients where name like ? GROUP BY ingredient', name)
    name = name[0]
    ingredientTuple = cursor.fetchall()
    drinkDictionary[name] = ingredientTuple

drinkNames = drinkDictionary.keys()  # a list of all drink names

# search function
def ingredientRegex(ingredient=''):
    '''finds all drink recipes containing a particular bar ingredient'''
    possibleDrinks = set()
    searchTermFixed = (r'\w*' + ingredient + r'\w*')
    searchTermRE = re.compile(searchTermFixed, re.IGNORECASE)
    for drink in drinkNames:
        ingredientList = drinkDictionary[drink]
        for ingredient in ingredientList:
            match = searchTermRE.search(ingredient)
            if match == None:
                continue
            else:
                possibleDrinks.add(drink)
    return (possibleDrinks)

def getRecipe(drinkName):
    '''looks up recipe using SQL and places in output box'''
    # recipeOutput.delete(0.0, END)

    #SQL query
    cursor.execute('SELECT ingredient FROM ingredients WHERE name =\'' + drinkName + '\'')
    ingredientList = cursor.fetchall()
    recipe = {}
    for i in ingredientList:
        cursor.execute('SELECT ingredient FROM ingredients WHERE name =\'' + drinkName + '\'')
        barIngredient = cursor.fetchall()
        cursor.execute('SELECT unit FROM ingredients WHERE name =\'' + drinkName + '\'AND ingredient =\'' + i + '\'')
        unit = cursor.fetchall()
        cursor.execute('SELECT amount FROM ingredients WHERE name =\'' + drinkName + '\'AND ingredient =\'' + i + '\'')
        amount = cursor.fetchall()
        quantity = str(amount[0] + ' ' + unit[0])
        # print(quantity)
        recipe[i] = quantity

    return recipe
    # output to text box
    # recipeOutput.insert(END, recipe)

recipeDict= {}
def printRecipe(drink):
    recipe = recipeDict[drink]
    recipeOutput.delete(0.0, END)
    recipeOutput.insert(END, recipe)


frame = Frame(window)
frame.grid(row=possibleDrinkRow + 2, column=possibleDrinkColumn)

def drinkLink(set):
    '''takes a set of drinks, converts to a list for sorting, makes each drink clickable to display the actual recipe in a text box'''
    # converts search results from set to list and sorts alphabetically
    resultList = []
    for drink in set:
        resultList.append(drink)
    # resultList.sort()

    # looks up recipe in SQL using getRecipe function and populates dictionary as 'drinkName': 'recipe'
    recipeDict.clear()
    for drink in resultList:
        recipeDict[drink] = getRecipe(drink)

    # create buttons
    buttonRow = possibleDrinkRow + 2    # GUI layout functions
    for result in resultList:
       Button(frame, text=result, width=30, font=drinkClickerFont, command=lambda n=result: printRecipe(n), background='white').grid(row=buttonRow, column=possibleDrinkColumn, sticky=possibleDrinkSticky)
       buttonRow +=1   # more layout functions

# key down function
def click():
    '''what happens when you click the 'Get me drunk' button'''
    # clear everything first
    possibleDrinkOutput.delete(0.0, END)

    # delete old buttons
    for Button in frame.winfo_children():
        Button.destroy()
    # except ()
    goodlist = set()
    badlist = set()
    badlist1 = set()
    badlist2 = set()
    badlist3 = set()

    included1 = inclusion1.get() # collects text from the text box
    goodlist1 = ingredientRegex(included1)
    goodlist = goodlist1
    included2 = inclusion2.get()
    if len(included2) >0:
        goodlist2 = ingredientRegex(included2)
        goodlist = goodlist1 & goodlist2
    else:
        goodlist = goodlist1
    included3 = inclusion3.get()
    if len(included3) >0:
        goodlist3 = ingredientRegex(included3)
        goodlist = goodlist & goodlist3
    excluded1 = exclusion1.get()
    if len(excluded1) >0:
        badlist1 = ingredientRegex(excluded1)
    excluded2 = exclusion2.get()
    if len(excluded2) >0:
        badlist2 = ingredientRegex(excluded2)
    excluded3 = exclusion3.get()
    if len(excluded3) >0:
        badlist3 = ingredientRegex(excluded3)
    badlist = badlist1 | badlist2 | badlist3
    drinkOptions = goodlist.difference(badlist)
    if len(drinkOptions) != 0:
        possibleDrinkOutput.insert(END, str(len(drinkOptions)) + ' drinks:\n')
        drinkLink(drinkOptions)

    else:
        noResults = 'Sorry, try some different ingredients'
        possibleDrinkOutput.insert(END, noResults)

    # TODO - remove all buttons when you click

# exit function
def close_window():
    window.destroy()
    exit()

# included ingredients boxes
Label (window, text='Included ingredients:', bg='white', fg='black', font=masterFont) .grid(row=inclusionRow, column=inclusionColumn, sticky=inclusionSticky)
inclusion1 = Entry(window, width=inclusionWidth, bg=inclusionBg, relief=inclusionRelief)
inclusion1.grid(row=inclusionRow+1, column=inclusionColumn, sticky=inclusionSticky)
inclusion2 = Entry(window, width=inclusionWidth, bg=inclusionBg, relief=inclusionRelief)
inclusion2.grid(row=inclusionRow+2, column=inclusionColumn, sticky=inclusionSticky)
inclusion3 = Entry(window, width=inclusionWidth, bg=inclusionBg, relief=inclusionRelief)
inclusion3.grid(row=inclusionRow+3, column=inclusionColumn, sticky=inclusionSticky)
includedIngredients = [inclusion1, inclusion2, inclusion3]


# excluded ingredients boxes
Label (window, text='Excluded ingredients:', bg='white', fg='black', font=masterFont) .grid(row=exclusionRow, column=exclusionColumn, sticky=exclusionSticky)
exclusion1 = Entry(window, width=exclusionWidth, bg=exclusionBg, relief=exclusionRelief)
exclusion1.grid(row=exclusionRow+1, column=inclusionColumn, sticky=exclusionSticky)
exclusion2 = Entry(window, width=exclusionWidth, bg=exclusionBg, relief=exclusionRelief)
exclusion2.grid(row=exclusionRow+2, column=inclusionColumn, sticky=exclusionSticky)
exclusion3 = Entry(window, width=exclusionWidth, bg=exclusionBg, relief=exclusionRelief)
exclusion3.grid(row=exclusionRow+3, column=exclusionColumn, sticky=exclusionSticky)
excludedIngredients = [exclusion1, exclusion2, exclusion3]

# create submit button
buttonText = 'Get me drunk'
Button (window, text=buttonText, width=len(buttonText)+1, font=masterFont, command=click). grid(row=getMeDrunkRow, column=getMeDrunkColumn, sticky=getMeDrunkSticky)

# create possible drinks label
Label (window, text='\nPossible drinks:', bg='white', fg='black', font=masterFont) .grid(row=possibleDrinkRow, column=possibleDrinkColumn, sticky=possibleDrinkSticky)

# create possible drinks box
possibleDrinkOutput = Text (window, width=20,height=possibleDrinkHeight, wrap=WORD, font=masterFont, bg='white')
possibleDrinkOutput.grid(row=possibleDrinkRow+1, column=possibleDrinkColumn, columnspan=1, sticky=W)

# create recipe label
Label (window, text='\nRecipe:', bg='white', fg='black', font=masterFont) .grid(row=recipeRow, column=recipeColumn, sticky=recipeSticky)

# create recipe box
recipeOutput = Text (window, width=recipeWidth, height=recipeHeight, wrap=WORD, font=masterFont, bg='white')
recipeOutput.grid(row=recipeRow+1, column=recipeColumn, columnspan=1, sticky=recipeSticky)

# # exit label
# Label (window, text='Click to exit', bg='white', fg='black', font=masterFont) .grid(row=exitRow, column=exitColumn, sticky=E)
#
# # exit button
# Button (window, text='Exit', font=masterFont, width=14, command=close_window). grid(row=exitRow, column=exitColumn, sticky=E)

####run the main loop
window.mainloop()


'''
TODO: learn tkinter.place for easier alignment of items
TODO: print available drinks in single file line
TODO: add functionality to click on each drink to get exact recipe
TODO: increase database to larger file 

'''