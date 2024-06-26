# pip install flask
from flask import Flask, render_template
import sqlite3
app = Flask(__name__)


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
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Character WHERE CharacterID=?', (id,))
    character = cur.fetchone()
    return render_template('character.html', character=character)


# all characters
@app.route('/allcharacters')
def all_characters():
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Character ORDER BY CharacterID')
    all_characters = cur.fetchall()
    return render_template('allcharacters.html', all_characters=all_characters)


# all enemies
@app.route('/allenemies')
def all_enemies():
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute('SELECT EnemyName, EnemyIcon FROM Enemy ORDER BY EnemyID')
    all_enemies = cur.fetchall()
    return render_template('allenemies.html', all_enemies=all_enemies)


# enemy page
@app.route('/enemy/<int:id>')
def enemy(id):
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Enemy WHERE EnemyID=?', (id,))
    enemy = cur.fetchone()
    return render_template('enemy.html', enemy=enemy)



@app.route('/enemy/type/<int:id>')
def enemy_type(id):
    conn = sqlite3.connect('dmc5.db')       
    cur = conn.cursor()
    cur.execute('SELECT * FROM Enemy WHERE EnemyType=? ORDER BY EnemyID', (id,))
    enemy_type = cur.fetchall()
    return render_template('enemy_type.html', enemy_type=enemy_type)

# @app.route('/triangles/<int:size>')
# def triangle(size):
#     result = ""
#     size += 1
#     for number in range(size):
#         result += "*" * number + "<br>"
#     return result


if __name__ == "__main__":
    app.run(debug=True)
