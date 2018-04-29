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

# key down function
def click():
    '''what happens when you click the 'Get me drunk' button'''
    output.delete(0.0, END)
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
        definition = drinkOptions
    else:
        definition = 'Sorry, no drinks match those parameters'
    output.insert(END, str(len(drinkOptions)) + ' drinks:\n')
    output.insert(END, definition)


# TODO - enter a photo?
# photo1 = PhotoImage(file='insertfilename.gif')
# Label (window, image=photo1, bg='black') .grid(row=0, column=0, sticky=W)

# exit function
def close_window():
    window.destroy()
    exit()

# main:
window = Tk()
window.title('drinkFinder: getting you drunk since 2018')
window.configure(background='white')

# TODO - enter a photo?
# photo1 = PhotoImage(file='insertfilename.gif')
# Label (window, image=photo1, bg='black') .grid(row=0, column=0, sticky=W)

# master variables
masterFont = ('didot', 18, 'bold roman')

# formatting & alignment for included ingredient boxes
inclusionRow = 0
inclusionColumn = 0
inclusionWidth = 20 # width of text boxes
inclusionSticky = W # horizontal alignment
inclusionBg = 'white' # background color
inclusionRelief = 'flat'


# formatting & alignment for included ingredient boxes
exclusionRow = inclusionRow + 5
exclusionColumn = 0
exclusionWidth = 20 # width of text boxes
exclusionSticky = W # horizontal alignment
exclusionBg = 'white' # background color
exclusionRelief = inclusionRelief

# alignment for buttons, etc.
possibleDrinkRow = exclusionRow + 5
possibleDrinkHeight = 6
possibleDrinkColumn = 0
getMeDrunkRow = 6
getMeDrunkColumn = 0
getMeDrunkSticky = E
exitRow = possibleDrinkRow+possibleDrinkHeight+1
exitColumn = 0

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

# create output label
Label (window, text='\nPossible drinks:', bg='white', fg='black', font=masterFont) .grid(row=possibleDrinkRow, column=possibleDrinkColumn, sticky=W)

# create output box
output = Text (window, width=75,height=possibleDrinkHeight, wrap=WORD, font=masterFont, bg='white')
output.grid(row=possibleDrinkRow+1, column=possibleDrinkColumn, columnspan=2, sticky=W)

# exit label
Label (window, text='Click to exit', bg='white', fg='black', font=masterFont) .grid(row=exitRow, column=exitColumn, sticky=E)

# exit button
Button (window, text='Exit', font=masterFont, width=14, command=close_window). grid(row=exitRow, column=exitColumn, sticky=E)

####run the main loop
window.mainloop()


'''
TODO: learn tkinter.place for easier alignment of items
TODO: print available drinks in single file line
TODO: add functionality to click on each drink to get exact recipe
TODO: increase database to larger file 

'''