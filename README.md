# CookBook using JavaScript, Python, and SQL
#### Video Demo:  <https://youtu.be/BYuKrFcArCo>
#### Description:
The purpose of this project was to make an interactive web application that acts as a recipe book. 
There are various actions that you can do within the website. This recipe book
would take recipes from various other sites, and be saved into the SQL for the user to see.
The way we went about this, was by using SQLite3 as a database to store vital information such as recipes (including
images and urls) and user log in details. In Python, we used the Flask framework to act as our backend, in which was
responsible for switching urls, and performing various actions within it. We used JavaScript to change certain images 
upon an action (liking and removing). We used various content from BootStrap and We used the navigation bar from the
CS50 Week 9 exercises. We declared several classes in the css document to style our html pages.

The first service that we offer is a registration and log 
in, to ensure the user can create an account that is unique to them. The way this is performed is through routing in
Flask, in which we use the 'get' method to load the page (login.html or register.html) in which allows the user
to either register or log in. Upon the user entering in their details (Username and password), The site sends a post
method to a app.route in python, which is responsible for storing or checking user entered data, and either comparing
it to existing data in an sql database or creating a new instance within it. All the information is stored within the 
users table in our recipes.db database. Upon loging in or registering, the user is redirected to the front page
(known as the index, in our case) which is also done through app.route. Within this page, there is yet again a new
service, which displays the 6 newest recipes that have been added to the database. This is quite cool as it keeps
the user updated on new recipes that are added.

Upon the homepage, there are several other services that are offered at the navigation bar and more. One of our favourite
features, is the save or favourite a recipe. There are plus signs (or minus if the user already favourited the recipe)
to add or remove the recipe from the users saved recipes. There is a saved recipes tab within the navigation bar, so the
user has quick access to their favourite recipes. The way that we done this, is by implementing an initial image (plus
if the recipe is not already in favourites or minus if it is) and we used Javascript to perform the changes to the image
if the user clicks on it. Furthermore, this calls a get or a post method to python, in order to add or delete the recipe
from the users favourites database.  This is done by getting the recipeid and checking if the recipeid is already in the
users favourites through the favourites table in the recipes.db.

There are several tabs that offer each a unique function. The first tab is the 'All Recipes' tab which is responsible for
displaying all the recipes within the database if the user wants to see through all the recipes. The 'save/favourite'
feature is also within each tab. This is useful if the user just wants to browse through all recipes without any filters
. This is done by sending data and favourites to a html page, in which it displays all the information. The next tab,
uses a dropdown menu, in order to make the website consumer friendlier. The options displayed within this menu, are 
'Recipes', which acts as a filter for the user if they wish to search for a particular protein or just desserts. This was
done through the select tag in html and a form tag in which makes a call to the pythons function of meatrecipes, in
which is responsible for displaying the correct information.

The next tab is the 'Saved Recipes' which displays the recipes that the user favourited. The user still gets the option
unsave the recipes. We have made a base case, if the user doesnt have any saved recipes, there is a text displayed on
the screen that informs the user that there are no saved recipes. The next tab, is one of our personal favourites, the
'Feeling Adventurous'. This is responsible for displaying a random recipe from the database in order to suprise the user.
A cool feature of this, is that it doesnt display a repeat (back to back) recipes as we have coded it purposely for this.

We have a search bar at the top right of the navigation bar, in which allows the user to search for any recipe with a
keyword. If there are no results, the webpage displays that there are no results and offers the user 3 random recipes
that may interest them. We have used the percentage signs on our sql query to check for either side of mention of the
keyword. Lastly, We have added a function, that allows the user to change their password. This is done by overiding the
current password in the sql users table after all error checking is done. The passwords are saved as hashes to make them
more secure.

Authors: Nedas Urba https://github.com/NedasU and Benas Urba https://github.com/BenasUrba