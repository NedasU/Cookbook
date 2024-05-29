import panda as pd

con = sqlite3.connect("recipes.db", ch)
con.row_factory = sqlite3.Row
#making a cursor to allow us to make execute statements
db = con.cursor()