# pip install flask
from flask import Flask, render_template, request, session, redirect, g, url_for, flash
import os
import sqlite3
app = Flask(__name__)

app.secret_key = os.urandom(24)

empty_query = None


# do queries
def execute_query(query, query_value=(), fetchone=False):
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute(query, query_value)

    if fetchone:
        result = cur.fetchone()
    else:
        result = cur.fetchall()

    conn.close()
    return result




# base page
@app.route('/')
def homepage():
    return render_template('home.html')


# about page
@app.route('/about')
def about():
    return render_template('about.html')


# character page
@app.route('/character/<int:id>')
def character(id):
    try:
        character = execute_query('SELECT * FROM Character WHERE CharacterID=?', (id,), fetchone=True)
        if character == empty_query:
            return render_template('404.html')
        else:
            return render_template('character.html', character=character)
    except OverflowError:
        return render_template('404.html')


# all characters
@app.route('/allcharacters')
def all_characters():
    all_characters = execute_query('SELECT * FROM Character ORDER BY CharacterID')
    return render_template('allcharacters.html', all_characters=all_characters)


# all enemies
@app.route('/allenemies')
def all_enemies():
    all_enemies = execute_query('SELECT * FROM Enemy ORDER BY EnemyID')
    return render_template('allenemies.html', all_enemies=all_enemies)


# enemy page
@app.route('/enemy/<int:id>')
def enemy(id):
    try:
        # Execute the query and fetch one record
        enemy = execute_query('SELECT * FROM Enemy WHERE EnemyID=?', (id,), fetchone=True)

        # Check if the result is empty
        if enemy == empty_query:
            return render_template('404.html')
        else:
            # Render the template with the enemy details if found
            return render_template('enemy.html', enemy=enemy)
    except OverflowError:
        # Handles the very large numbers sql can't handle
        return render_template('404.html', message="An unexpected error occurred.")


# enemies by type
@app.route('/enemy/type/<int:id>')
def enemy_type(id):
    try:
        enemy_type = execute_query('SELECT * FROM Enemy WHERE EnemyType=? ORDER BY EnemyID', (id,))
        if not enemy_type:
            return render_template('404.html')
        else:
            return render_template('enemy_type.html', enemy_type=enemy_type)
        # prevent large numbers from breaking website
    except OverflowError:
        return render_template('404.html')


# select character to see all strategies for said character
@app.route('/strategy/character/')
def character_strategy():
    character_strategy = execute_query('SELECT * FROM Character ORDER BY CharacterID')
    if character_strategy == empty_query:
        return render_template('404.html')
    else:
        return render_template('select_character_strategy.html', character_strategy=character_strategy)


# one character, all strategies
@app.route('/strategy/character/<int:id>')
def character_all_strategy(id):
    try:
        character_all_strategy = execute_query('''SELECT
    Character.CharacterID,
    Character.CharacterName,
    Character.CharacterIcon,
    Character_Enemy.Difficulty,
    Character_Enemy.Strategy,
    Enemy.EnemyID,
    Enemy.EnemyName,
    Enemy.EnemyIcon,
    Enemy.EnemyType
FROM Character
JOIN Character_Enemy ON Character.CharacterID = Character_Enemy.CharacterID
JOIN Enemy ON Enemy.EnemyID = Character_Enemy.EnemyID
WHERE Character.CharacterID = ?''', (id,))
        if character_all_strategy == empty_query:
            return render_template('404.html')
        else:
            return render_template('character_strategies.html', character_all_strategy=character_all_strategy)
    except OverflowError:
        return render_template('404.html')

@app.route('/strategy/<int:ch>/<int:en>')
def strategy(ch, en):
    # Execute the query with both parameters
    query = '''
    SELECT
        Character.CharacterID,
        Character.CharacterName,
        Character.CharacterIcon,
        Character_Enemy.Difficulty,
        Character_Enemy.Strategy,
        Enemy.EnemyID,
        Enemy.EnemyName,
        Enemy.EnemyIcon,
        Enemy.EnemyType
    FROM Character
    JOIN Character_Enemy ON Character.CharacterID = Character_Enemy.CharacterID
    JOIN Enemy ON Enemy.EnemyID = Character_Enemy.EnemyID
    WHERE Character.CharacterID = ? AND Enemy.EnemyID = ?
    '''

    # Execute the query
    strategy = execute_query(query, (ch, en))

    # Check if a result was returned
    if not strategy:
        return render_template('404.html')

    # Pass the first row (tuple) to the template
    return render_template('strategy.html', strategy=strategy[0])


# error page
@app.errorhandler(404)
def page_not_found(exception):
    return render_template('404.html'), 404


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect('account.db')
        cur = conn.cursor()
        cur.execute(f"SELECT username, password FROM accounts WHERE username ='{username}';")
        user = cur.fetchone()
        # correct username and password
        if user and password == user[1]:
            session['username'] = user[0]
            return redirect('/confirm')
        else:
            flash('Login attempt failed')
        conn.commit()
        conn.close()

    return render_template('login.html')


# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")
        # print(username, password, password_repeat)
        conn = sqlite3.connect('account.db')
        cur = conn.cursor()
        # check for matching password
        if password != password_repeat:
            flash("Password does not match")
            return redirect('/register')
        unique_username = cur.execute(f"SELECT username FROM ACCOUNTS WHERE username ={'username'}")
        # Username is already in database
        if not unique_username:
            flash('Username taken')
            return redirect('/register')
        cur.execute(f"INSERT INTO accounts (username, password) values ('{username}', '{password}')")
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/confirm')
def confirm():
    return render_template('confirm.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)
