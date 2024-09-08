# pip install flask
from flask import Flask, render_template, request, session, redirect, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import sqlite3
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 megabytes
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


app.secret_key = os.urandom(24)

empty_query = None


# do queries
def execute_query(query, query_value=(), fetchone=False,  commit=False,):
    conn = sqlite3.connect('dmc5.db')  # connect to the specified database
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
    return render_template('layout.html')


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
WHERE Character.CharacterID = ?''', (id,))
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

    strategy = execute_query(query, (ch, en))

    # checks if a result was returned
    if not strategy:
        return render_template('404.html')

    return render_template('strategy.html', strategy=strategy[0])


# error page
@app.errorhandler(404)
def page_not_found(exception):
    return render_template('404.html'), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File is too large. The maximum file size allowed is 2MB.')
    return redirect(request.url)


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
            fetchone=True
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
def delete():
    get_flashed_messages()
    username = session['username']

    execute_query('DELETE FROM accounts WHERE username=?', (username,), commit=True)
    session.pop('username', None)
    flash('Account deleted')
    return redirect('/')


# logs out and then redirects back to home page
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


@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if 'username' not in session:
        flash('You need to log in to upload images.')
        return redirect('/login')

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            userid = session.get('userid')  # Make sure to set 'userid' during login
            description = request.form.get('description', '')

            query = '''
            INSERT INTO UserImages (userid, ImageName, ImagePath, Description)
            VALUES (?, ?, ?, ?)
            '''
            execute_query(query, query_value=(userid, filename, filepath, description), commit=True)

            flash('Image successfully uploaded')
            return redirect(url_for('upload_image'))

    return render_template('upload.html')


@app.route('/img_board')
def img_board():
    # Query to get all images from UserImages table
    query = "SELECT * FROM UserImages"
    images = execute_query(query)

    return render_template('img_board.html', images=images)


if __name__ == "__main__":
    app.run(debug=True)
