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
    cur.execute('SELECT CharacterName, CharacterIcon FROM Character ORDER BY CharacterID')
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


# normal enemy page
@app.route('/enemy/normal')
def normal_enemy():
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Enemy WHERE EnemyType= "Normal" ORDER BY EnemyID')
    normal_enemy = cur.fetchall()
    return render_template('normal_enemy.html', normal_enemy=normal_enemy)



# elite enemy page
@app.route('/enemy/elite')
def elite_enemy():
    conn = sqlite3.connect('dmc5.db')       
    cur = conn.cursor()
    cur.execute('SELECT * FROM Enemy WHERE EnemyType= "Elite" ORDER BY EnemyID')
    elite_enemy = cur.fetchall()
    return render_template('elite.html', elite_enemy=elite_enemy)


# boss enemy page
@app.route('/enemy/boss')
def boss_enemy():
    conn = sqlite3.connect('dmc5.db')       
    cur = conn.cursor()
    cur.execute('SELECT * FROM Enemy WHERE EnemyType= "Boss" ORDER BY EnemyID')
    boss_enemy = cur.fetchall()
    return render_template('boss.html', boss_enemy=boss_enemy)


# @app.route('/triangles/<int:size>')
# def triangle(size):
#     result = ""
#     size += 1
#     for number in range(size):
#         result += "*" * number + "<br>"
#     return result


if __name__ == "__main__":
    app.run(debug=True)
