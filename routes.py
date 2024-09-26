# pip install flask
from flask import (
    Flask, render_template, request, session,
    redirect, url_for, flash, get_flashed_messages
)
from functools import wraps
import os
import sqlite3
app = Flask(__name__)


app.secret_key = os.urandom(24)

empty_query = None


def login_required(original_function):
    @wraps(original_function)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to log in to do this.')
            return redirect(url_for('login'))
        return original_function(*args, **kwargs)
    return decorated_function


def already_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            flash('You are already logged in.')
            return redirect(url_for('dashboard'))
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


def get_enemy_type(enemy_type_id):
    enemy_types = {
        1: 'Normal',
        2: 'Elite',
        3: 'Boss'
    }
    return enemy_types.get(enemy_type_id, '')


app.jinja_env.filters['get_enemy_type'] = get_enemy_type


@app.route('/')
def homepage():
    character_strategy = execute_query('''SELECT CharacterID, CharacterName,
                                       CharacterType, CharacterDescription,
                                       CharacterIcon FROM Character ORDER BY CharacterID''')
    if character_strategy == empty_query:
        return render_template('404.html')
    else:
        return render_template('select_character_strategy.html',
                               character_strategy=character_strategy,)


@app.route('/character/<int:id>')
def character(id):
    try:
        character = execute_query('''SELECT CharacterName, CharacterType,
                                  CharacterDescription, CharacterIcon
                                  FROM Character WHERE CharacterID=?''',
                                  (id,), fetchone=True)
        if character == empty_query:
            return render_template('404.html')
        else:
            return render_template('character.html', character=character)
    except OverflowError:
        return render_template('404.html')


@app.route('/allcharacters')
def all_characters():
    all_characters = execute_query('''SELECT CharacterID, CharacterName, CharacterType,
                                   CharacterDescription, CharacterIcon FROM Character''')
    return render_template('allcharacters.html', all_characters=all_characters)


@app.route('/allenemies')
def all_enemies():
    all_enemies = execute_query('''SELECT EnemyID, EnemyName, EnemyType,
                                EnemyDescription, EnemyIcon FROM Enemy''')
    return render_template('allenemies.html', all_enemies=all_enemies)


@app.route('/enemy/<int:id>')
def enemy(id):
    try:
        enemy = execute_query('''SELECT EnemyID, EnemyName, EnemyType,
                              EnemyDescription, EnemyIcon FROM Enemy
                              WHERE EnemyID=?''', (id,), fetchone=True)

        if enemy == empty_query:
            return render_template('404.html')
        else:
            return render_template('enemy.html', enemy=enemy)
    except OverflowError:
        return render_template('404.html', message="An unexpected error occurred.")


@app.route('/enemy/type/<int:id>')
def enemy_type(id):
    try:
        enemy_type = execute_query('''SELECT EnemyID, EnemyName, EnemyType,
                                   EnemyDescription, EnemyIcon FROM Enemy
                                   WHERE EnemyType=? ORDER BY EnemyID''', (id,))
        if not enemy_type:
            return render_template('404.html')
        else:
            return render_template('enemy_type.html', enemy_type=enemy_type)
    except OverflowError:
        return render_template('404.html')


@app.route('/strategy/character/<int:id>')
def character_all_strategy(id):
    try:
        character_all_strategy = execute_query('''SELECT
            Character.CharacterID,
            Character.CharacterName,
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

        if not character_all_strategy:
            return render_template('404.html')

        return render_template('character_strategies.html',
                               character_all_strategy=character_all_strategy)

    except OverflowError:
        return render_template('404.html')


@app.route('/strategy/<int:ch>/<int:en>', methods=['GET'])
def strategy(ch, en):
    try:
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

        if not strategy:
            return render_template('404.html')

        return render_template('strategy.html', strategy=strategy[0], **character_limits())

    except OverflowError:
        return render_template('404.html')


@app.route('/strategy/update/<int:ch>/<int:en>', methods=['POST'])
@login_required
def update_strategy(ch, en):
    new_strategy = request.form.get('strategy')
    new_difficulty = request.form.get('difficulty')

    execute_query(
        '''UPDATE Character_Enemy SET Strategy = ?, Difficulty = ? WHERE
        CharacterID = ? AND EnemyID = ?''',
        (new_strategy, new_difficulty, ch, en),
        commit=True
    )

    flash('Strategy and Difficulty updated successfully.')
    return redirect(url_for('strategy', ch=ch, en=en))


def character_limits():
    return {
        'username_min_length': 6,
        'username_max_length': 14,
        'password_min_length': 8,
        'password_max_length': 24,
        'strategy_max_length': 2000,
        'min_difficulty': 1,
        'max_difficulty': 10
    }


@app.route('/register', methods=['GET', 'POST'])
@already_logged_in
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")

        if password != password_repeat:
            flash("Password does not match")
            return redirect('/register')

        username_exists = execute_query(
            "SELECT username FROM ACCOUNTS WHERE username = ?",
            (username,),
            fetchone=True
        )

        if username_exists:
            flash('Username taken')
            return redirect('/register')

        check_type = username.isalnum() and username.isascii()
        if check_type is False:
            flash('Only letters and numbers are allowed')
            return redirect('/register')

        execute_query(
            "INSERT INTO accounts (username, password) VALUES (?, ?)",
            (username, password),
            commit=True
        )

        return redirect('/login')

    return render_template('register.html', **character_limits())


@app.route('/login', methods=['GET', 'POST'])
@already_logged_in
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = execute_query(
            '''SELECT userid, username, password FROM accounts WHERE username = ?
            AND password = ?''',
            (username, password),
            fetchone=True
        )

        if user:
            session['username'] = username
            session['userid'] = user[0]
            return redirect('/dashboard')
        else:
            flash('Invalid username or password')
            return redirect('/login')

    return render_template('login.html', **character_limits())


@app.route('/delete')
@login_required
def delete():
    get_flashed_messages()
    username = session['username']

    execute_query('DELETE FROM accounts WHERE username=?', (username,), commit=True)
    session.pop('username', None)
    flash('Account deleted')
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/sources')
def sources():
    enemy_query = "SELECT EnemyIcon FROM Enemy"
    character_query = "SELECT CharacterIcon FROM Character"

    enemy_icons = execute_query(enemy_query)
    character_icons = execute_query(character_query)

    # check if image is repeated from other table
    character_icon_set = {icon[0] for icon in character_icons}

    return render_template('sources.html', enemy_icons=enemy_icons,
                           character_icons=character_icons,
                           character_icon_set=character_icon_set)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.errorhandler(404)
def page_not_found(exception):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)