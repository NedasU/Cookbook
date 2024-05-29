from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

# initialising the connection for flask
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#making a connection to a database on sql
con = sqlite3.connect("recipes.db", check_same_thread=False)
con.row_factory = sqlite3.Row
#making a cursor to allow us to make execute statements
db = con.cursor()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    db.execute('SELECT * FROM Recipes ORDER BY id DESC LIMIT 6')
    data = [dict(row) for row in db.fetchall()]
    try:
            db.execute('SELECT recipeid FROM favourites WHERE id = ?', [session['user_id']])
            favourites = [x for row in db.fetchall() for x in row]
    except:
        favourites = []
    return render_template('index.html', data=data, favourites=favourites)


@app.route('/login', methods=['POST', 'GET'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db.execute('SELECT * FROM users WHERE username = ?', [username])
        data = [dict(row) for row in db.fetchall()]
        if len(data) != 1 or not check_password_hash(data[0]['hash'], password):
            return render_template('login.html', error='invalid username or password!')
        session['user_id'] = data[0]['id']
        return redirect("/")
    return render_template('login.html', error='')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        if not username or password != confirmation:
            return render_template('register.html', error='The passwords do not match, or no username was entered')
        usernames = db.execute('SELECT username FROM users')
        usernames = [name for user in usernames for name in user]
        if username in usernames:
            return render_template('register.html', error='The username is already in use!')
        db.execute('INSERT INTO users (username, hash) VALUES (?, ?)',[username, generate_password_hash(password)])
        con.commit()
        db.execute('SELECT id FROM users WHERE username = ?', [username])
        data = [x for row in db.fetchall() for x in row]
        session['user_id'] = data[0]
        return redirect('/')
    return render_template('register.html', error="")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/saverecipe', methods=['POST'])
def saverecipe():
    try:
        recipeid = request.form.get('recipeid')
        db.execute('SELECT * FROM Recipes WHERE id = ?', [recipeid])
        data = [dict(row) for row in db.fetchall()]
        exists = list(db.execute('SELECT * FROM favourites WHERE id = ? AND recipeid = ?',[session['user_id'], recipeid]))
        if not exists:
            db.execute('INSERT INTO favourites (id, recipeid, dishname, protein, vegetables) VALUES (?, ?, ?, ?, ?)',
                       [session['user_id'], recipeid, data[0]['name'], data[0]['protein'], data[0]['vegetables']])
            con.commit()
        else:
            db.execute('DELETE FROM favourites WHERE id = ? AND recipeid = ?', [session['user_id'], recipeid])
            con.commit()
        return redirect('/')
    except:
        return redirect('/login')


@app.route('/savedrecipes', methods=['GET','POST'])
def savedrecipes():
    db.execute('SELECT username FROM users WHERE id = ?', [session['user_id']])
    username = [x for name in db.fetchall() for x in name]
    if request.method == 'POST':
        recipeid = request.form.get('recipeid')
        db.execute('DELETE FROM favourites WHERE id = ? AND recipeid= ?', [session['user_id'], recipeid])
        con.commit()
    db.execute('SELECT recipeid FROM favourites WHERE id = ?', [session['user_id']])
    data = [x for row in db.fetchall() for x in row]
    if len(data) > 1:
        db.execute('SELECT * FROM Recipes WHERE id IN {}'.format(tuple(data)))
    elif len(data) >0:
        db.execute('SELECT * FROM Recipes WHERE id = ?',data)
    else:
        return render_template('savedrecipes.html', data=[], username=username)
    data2 = [dict(row) for row in db.fetchall()]
    return render_template('savedrecipes.html', data=data2, username=username)


@app.route('/randomrecipe', methods=['POST', 'GET'])
def randomrecipe():
    if request.method == 'POST':
        curid = request.form.get('curid')
        db.execute("SELECT * FROM Recipes WHERE id <> ? ORDER BY random() limit 1", [curid])
    else:
        db.execute("SELECT * FROM Recipes ORDER BY random() limit 1")
    info = [dict(row) for row in db.fetchall()][0]
    return render_template('randomrecipe.html', info=info)

def get_recipes(method, html=None, protein=None, recipeid=None):
    if method == 'GET':
        exists = list(db.execute('SELECT * FROM favourites WHERE id = ? AND recipeid = ?',[session['user_id'], recipeid]))
        if not exists:
            db.execute('SELECT * FROM Recipes WHERE id = ?', [recipeid])
            data = [dict(row) for row in db.fetchall()]
            db.execute('INSERT INTO favourites (id, recipeid, dishname, protein, vegetables) VALUES (?, ?, ?, ?, ?)',
                       [session['user_id'], recipeid, data[0]['name'], data[0]['protein'], data[0]['vegetables']])
            con.commit()
        else:
            db.execute('DELETE FROM favourites WHERE id = ? AND recipeid = ?', [session['user_id'], recipeid])
            con.commit()
        return ("", 204)
    db.execute('SELECT recipeid FROM favourites WHERE id = ?', [session['user_id']])
    favourites = [x for row in db.fetchall() for x in row]
    if protein == 'Dessert':
        db.execute("SELECT * FROM Recipes WHERE protein = 'None' AND vegetables = 'None'")
        data = [dict(row) for row in db.fetchall()]
    else:
        db.execute("SELECT * FROM Recipes WHERE protein = ?", [protein])
        data = [dict(row) for row in db.fetchall()]
    return render_template(html, data=data, favourites=favourites)

@app.route('/meatrecipes', methods=['GET', 'POST'])
def meatrecipes():
    if request.method == 'GET':
        recipeid = request.args.get('recipeid')
        return get_recipes('GET', recipeid=recipeid)
    protein = request.form.get('meat')
    return get_recipes('POST', protein.lower()+'recipes.html', protein)



@app.route('/allrecipes', methods=['POST', 'GET'])
def allrecipes():
    if request.method == 'POST':
        recipeid = request.form.get('recipeid')
        exists = list(
            db.execute('SELECT * FROM favourites WHERE id = ? AND recipeid = ?', [session['user_id'], recipeid]))
        if not exists:
            db.execute('SELECT * FROM Recipes WHERE id = ?', [recipeid])
            data = [dict(row) for row in db.fetchall()]
            db.execute(
                'INSERT INTO favourites (id, recipeid, dishname, protein, vegetables) VALUES (?, ?, ?, ?, ?)',
                [session['user_id'], recipeid, data[0]['name'], data[0]['protein'], data[0]['vegetables']])
            con.commit()
        else:
            db.execute('DELETE FROM favourites WHERE id = ? AND recipeid = ?', [session['user_id'], recipeid])
            con.commit()
        return ("", 204)
    db.execute('SELECT recipeid FROM favourites WHERE id = ?', [session['user_id']])
    favourites = [x for row in db.fetchall() for x in row]
    db.execute("SELECT * FROM Recipes")
    data = [dict(row) for row in db.fetchall()]
    return render_template('allrecipes.html', data=data, favourites=favourites)


@app.route('/search', methods=['POST', 'GET'])
def search():
    db.execute('SELECT recipeid FROM favourites WHERE id = ?', [session['user_id']])
    favourites = [x for row in db.fetchall() for x in row]
    if request.method == 'POST':
        search_value = request.form.get('search')
        db.execute('SELECT * FROM Recipes WHERE name LIKE ?', ["%"+search_value+'%'])
        data = [dict(row) for row in db.fetchall()]
        count = len(data)
        if count == 0:
            db.execute("SELECT * FROM Recipes ORDER BY random() LIMIT 3")
            info = [dict(row) for row in db.fetchall()]
            return render_template('search.html', data=data, count=count, favourites=favourites, randoms=info)
        return render_template('search.html', data=data, count=count, favourites=favourites)
    else:
        recipeid = request.args.get('recipeid')
        exists = list(
            db.execute('SELECT * FROM favourites WHERE id = ? AND recipeid = ?', [session['user_id'], recipeid]))
        if not exists:
            db.execute('SELECT * FROM Recipes WHERE id = ?', [recipeid])
            data = [dict(row) for row in db.fetchall()]
            db.execute(
                'INSERT INTO favourites (id, recipeid, dishname, protein, vegetables) VALUES (?, ?, ?, ?, ?)',
                [session['user_id'], recipeid, data[0]['name'], data[0]['protein'], data[0]['vegetables']])
            con.commit()
        else:
            db.execute('DELETE FROM favourites WHERE id = ? AND recipeid = ?', [session['user_id'], recipeid])
            con.commit()
        return ("", 204)


@app.route('/changepass', methods=['GET', 'POST'])
def changepass():
    if request.method == 'POST':
        curpass= request.form.get('curpass1')
        newpass1 = request.form.get('newpass1')
        newpass2 = request.form.get('newpass2')
        db.execute('SELECT hash FROM users WHERE id = ?', [session['user_id']])
        oldpass = [x for row in db.fetchall() for x in row]
        if not check_password_hash(oldpass[0], curpass) or newpass1 != newpass2 or newpass1 == curpass:
            return render_template('changepass.html', error='The passwords entered were either incorrect, didnt match, or already the current password!')
        db.execute('UPDATE users SET hash = ? WHERE id =?', [generate_password_hash(newpass1), session['user_id']])
        return redirect('/')
    return render_template('changepass.html', error="")

app.run()
