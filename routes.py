# pip install flask
from flask import Flask, render_template
import sqlite3
app = Flask(__name__)

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
    character = execute_query('SELECT * FROM Character WHERE CharacterID=?', (id,), fetchone=True)
    if character == empty_query:
        return render_template('404.html')
    else:
        return render_template('character.html', character=character)


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
    enemy = execute_query('SELECT * FROM Enemy WHERE EnemyID=?', (id,), fetchone=True)
    if enemy == empty_query:
        return render_template('404.html')
    else:
        return render_template('enemy.html', enemy=enemy)


# enemies by type
@app.route('/enemy/type/<int:id>')
def enemy_type(id):
    enemy_type = execute_query('SELECT * FROM Enemy WHERE EnemyType=? ORDER BY EnemyID', (id,))
    if enemy_type == empty_query:
        return render_template('404.html')
    else:
        return render_template('enemy_type.html', enemy_type=enemy_type)

# @app.route('/triangles/<int:size>')
# def triangle(size):
#     result = ""
#     size += 1
#     for number in range(size):
#         result += "*" * number + "<br>"
#     return result


# select character to see all strategies for said character
@app.route('/strategy/character/<int:id>')
def character_strategy(id):
    character_strategy = execute_query('SELECT * FROM Character WHERE CharacterID=?', (id,))
    if character_strategy == empty_query:
        return render_template('404.html')
    else:
        return render_template('layout.html', character_strategy=character_strategy)


# error page
@app.errorhandler(404)
def page_not_found(exception):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
