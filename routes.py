# pip install flask
from flask import Flask, render_template, request, session, redirect, g, url_for, flash, get_flashed_messages
import os
import sqlite3
app = Flask(__name__)

app.secret_key = os.urandom(24)

empty_query = None


# do queries
def execute_query(query, query_value=(), fetchone=False,  commit=False, database=''):
    conn = sqlite3.connect(database)  # connect to the specified database
    cur = conn.cursor()
    cur.execute(query, query_value)

    if commit:
        conn.commit()

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
        character = execute_query('SELECT * FROM Character WHERE CharacterID=?', (id,), fetchone=True, database='dmc5.db')
        if character == empty_query:
            return render_template('404.html')
        else:
            return render_template('character.html', character=character)
    except OverflowError:
        return render_template('404.html')


# all characters
@app.route('/allcharacters')
def all_characters():
    all_characters = execute_query('SELECT * FROM Character ORDER BY CharacterID', database='dmc5.db')
    return render_template('allcharacters.html', all_characters=all_characters)


# all enemies
@app.route('/allenemies')
def all_enemies():
    all_enemies = execute_query('SELECT * FROM Enemy ORDER BY EnemyID', database='dmc5.db')
    return render_template('allenemies.html', all_enemies=all_enemies)


# enemy page
@app.route('/enemy/<int:id>')
def enemy(id):
    try:
        # gets one enemy from db
        enemy = execute_query('SELECT * FROM Enemy WHERE EnemyID=?', (id,), fetchone=True, database='dmc5.db')

        # check if the result is empty
        if enemy == empty_query:
            return render_template('404.html')
        else:
            return render_template('enemy.html', enemy=enemy)
    except OverflowError:
        # handles the very large numbers sql can't handle
        return render_template('404.html', message="An unexpected error occurred.")


# enemies by type
@app.route('/enemy/type/<int:id>')
def enemy_type(id):
    try:
        enemy_type = execute_query('SELECT * FROM Enemy WHERE EnemyType=? ORDER BY EnemyID', (id,), database='dmc5.db')
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
    character_strategy = execute_query('SELECT * FROM Character ORDER BY CharacterID', database='dmc5.db')
    if character_strategy == empty_query:
        return render_template('404.html')
    else:
        return render_template('select_character_strategy.html', character_strategy=character_strategy,)


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
WHERE Character.CharacterID = ?''', (id,), database='dmc5.db')
        if character_all_strategy == empty_query:
            return render_template('404.html')
        else:
            return render_template('character_strategies.html', character_all_strategy=character_all_strategy)
    except OverflowError:
        return render_template('404.html')


@app.route('/strategy/<int:ch>/<int:en>')
def strategy(ch, en):
    # executes the query with both parameters
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

    strategy = execute_query(query, (ch, en), database='dmc5.db')

    # checks if a result was returned
    if not strategy:
        return render_template('404.html')

    return render_template('strategy.html', strategy=strategy[0])


# error page
@app.errorhandler(404)
def page_not_found(exception):
    return render_template('404.html'), 404


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # check if the username exists and the password matches
        user = execute_query(
            "SELECT * FROM accounts WHERE username = ? AND password = ?",
            (username, password),
            fetchone=True,
            database='account.db'
        )

        if user:
            # successful login
            session['username'] = username
            return redirect('/dashboard')
        else:
            # login failed
            flash('Invalid username or password')
            return redirect('/login')

    return render_template('login.html')


# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")

        # check for matching passwords
        if password != password_repeat:
            flash("Password does not match")
            return redirect('/register')

        # check for unique username
        unique_username = execute_query(
            "SELECT username FROM ACCOUNTS WHERE username = ?",
            (username,),
            database='account.db',
            fetchone=True
        )

        # username already exists
        if unique_username:
            flash('Username taken')
            return redirect('/register')

        # checks for if it is a letter or number
        check_type = username.isalnum()
        if check_type is False:
            flash('Only letters and numbers are allowed')
            return redirect('/register')

        # add new user into the database
        execute_query(
            "INSERT INTO accounts (username, password) VALUES (?, ?)",
            (username, password),
            database='account.db',
            commit=True  # saves to the db
        )

        return redirect('/login')

    return render_template('register.html')


@app.route('/delete')
def delete():
    get_flashed_messages()
    username = session['username']

    execute_query('DELETE FROM accounts WHERE username=?', (username,), database='account.db', commit=True)
    session.pop('username', None)
    flash('Account deleted')
    return redirect('/')


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
