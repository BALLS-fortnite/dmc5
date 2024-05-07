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


# all characters page
@app.route('/characters')
def characters(id):
    conn = sqlite3.connect('dmc5.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Characters WHERE CharacterID=?', (id,))
    characters = cur.fetchone()
    return render_template('characters.html', characters=characters)


if __name__ == "__main__":
    app.run(debug=True)

fgffgdgdfuihuihui