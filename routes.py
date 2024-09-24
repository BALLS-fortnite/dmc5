# pip install flask
from flask import Flask, render_template, request, session, redirect, url_for, flash, get_flashed_messages
from functools import wraps
import os
import sqlite3
app = Flask(__name__)


app.secret_key = os.urandom(24)

empty_query = None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to log in to do this.')
            return redirect(url_for('login'))  # Redirect to login if not logged in
        return f(*args, **kwargs)
    return decorated_function


def already_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:  # Check if the user is already logged in
            flash('You are already logged in.')
            return redirect(url_for('dashboard'))  # Redirect to dashboard if logged in
        return f(*args, **kwargs)
    return decorated_function


# function for queries
def execute_query(query, query_value=(), fetchone=False,  commit=False,):
    conn = sqlite3.connect('dmc5.db')
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


# Function to map enemy types to their names
def get_enemy_type(enemy_type_id):
    enemy_types = {
        1: 'Normal',
        2: 'Elite',
        3: 'Boss'
    }
    return enemy_types.get(enemy_type_id, '')


# Register the filter
app.jinja_env.filters['get_enemy_type'] = get_enemy_type


# Displays characters to select one to see all their strategies
@app.route('/')
def homepage():
    character_strategy = execute_query('SELECT * FROM Character ORDER BY CharacterID')
    if character_strategy == empty_query:
        return render_template('404.html')
    else:
        return render_template('select_character_strategy.html', character_strategy=character_strategy,)


# character page
@app.route('/character/<int:id>')
def character(id):
    # Gets character's details according to CharacterID
    try:
        character = execute_query('SELECT * FROM Character WHERE CharacterID=?', (id,), fetchone=True)
        if character == empty_query:
            return render_template('404.html')
        else:
            return render_template('character.html', character=character)
    except OverflowError:
        return render_template('404.html')


# Displays all characters by CharacterID
@app.route('/allcharacters')
def all_characters():
    # Displays all characters by CharacterID
    all_characters = execute_query('SELECT * FROM Character ORDER BY CharacterID')
    return render_template('allcharacters.html', all_characters=all_characters)


# Displays all enemies by EnemyID
@app.route('/allenemies')
def all_enemies():
    all_enemies = execute_query('SELECT * FROM Enemy ORDER BY EnemyID')
    return render_template('allenemies.html', all_enemies=all_enemies)


# enemy page
@app.route('/enemy/<int:id>')
def enemy(id):
    try:
        # gets one enemy from db
        enemy = execute_query('SELECT * FROM Enemy WHERE EnemyID=?', (id,), fetchone=True)

        # check if the result is empty
        if enemy == empty_query:
            return render_template('404.html')
        else:
            return render_template('enemy.html', enemy=enemy)
    except OverflowError:
        # handles the very large numbers sql can't handle
        return render_template('404.html', message="An unexpected error occurred.")


# Enemies by type
@app.route('/enemy/type/<int:id>')
def enemy_type(id):
    try:
        enemy_type = execute_query('SELECT * FROM Enemy WHERE EnemyType=? ORDER BY EnemyID', (id,))
        if not enemy_type:
            return render_template('404.html')
        else:
            return render_template('enemy_type.html', enemy_type=enemy_type)
        # Prevent large numbers from breaking website
    except OverflowError:
        return render_template('404.html')


# Get all strategies for one CharacaterID
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
        
        # Check if the query result is empty
        if not character_all_strategy:
            return render_template('404.html')  # No results, return a 404 page

        return render_template('character_strategies.html', character_all_strategy=character_all_strategy)
    
    except OverflowError:
        return render_template('404.html')



# Gets all the strategy info for a given character when fightng a given enemy
@app.route('/strategy/<int:ch>/<int:en>', methods=['GET'])
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

    strategy = execute_query(query, (ch, en))

    # checks if a result was returned
    if not strategy:
        return render_template('404.html')

    return render_template('strategy.html', strategy=strategy[0])


@app.route('/strategy/update/<int:ch>/<int:en>', methods=['POST'])
@login_required
def update_strategy(ch, en):
    new_strategy = request.form.get('strategy')

    # Update the strategy in the database
    execute_query(
        '''UPDATE Character_Enemy SET Strategy = ? WHERE CharacterID = ? AND EnemyID = ?''',
        (new_strategy, ch, en),
        commit=True
    )

    flash('Strategy updated successfully.')
    return redirect(url_for('strategy', ch=ch, en=en))


# login
@app.route('/login', methods=['GET', 'POST'])
@already_logged_in
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # check if the username exists and the password matches
        user = execute_query(
            "SELECT * FROM accounts WHERE username = ? AND password = ?",
            (username, password),
            fetchone=True
        )

        if user:
            # successful login
            session['username'] = username
            session['userid'] = user[0]
            return redirect('/dashboard')
        else:
            # login failed
            flash('Invalid username or password')
            return redirect('/login')

    return render_template('login.html')


# register
@app.route('/register', methods=['GET', 'POST'])
@already_logged_in
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
            commit=True  # saves to the db
        )

        return redirect('/login')

    return render_template('register.html')


@app.route('/delete')
@login_required  # Account logged in is required to delete account
def delete():
    get_flashed_messages()
    username = session['username']

    execute_query('DELETE FROM accounts WHERE username=?', (username,), commit=True)
    session.pop('username', None)
    flash('Account deleted')
    return redirect('/')


# logs out and then redirects back to home page
@app.route('/logout')
@login_required  # Account loged in is required to logout
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# error page
@app.errorhandler(404)
def page_not_found(exception):
    return render_template('404.html'), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File is too large. The maximum file size allowed is 2MB.')
    return redirect(request.url)


if __name__ == "__main__":
    app.run(debug=True)
