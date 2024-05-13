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


@app.route('/allcharacters')
def all_characters():
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute('SELECT CharacterName, CharacterIcon FROM Character ORDER BY CharacterID')
    all_characters = cur.fetchall()
    return render_template('allcharacters.html', all_characters=all_characters)


if __name__ == "__main__":
    app.run(debug=True)
