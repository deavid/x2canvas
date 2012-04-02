# encoding: UTF-8
import sys, os.path
import utils.whereami
import utils.fsdb
import dbscheme
from flask import Flask, request, session, g, redirect, url_for
from flask import abort, render_template, flash

USERNAME = 'admin'
PASSWORD = 'password'
SECRET_KEY = 'development key'
DATABASE = '../data'
app = Flask(__name__)
app.config.from_object(__name__)

dbTemplate = utils.fsdb.DatabaseTemplate(dbscheme)

@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = dbTemplate.connect(DATABASE)


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route("/")
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_user'] = request.form['username'] 
    if 'logged_user' in session:
        flash('You were logged in')
        return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    if 'logged_user' in session:
        flash('You have been logged out')
        del session['logged_user']
    return redirect(url_for('login'))




if __name__ == "__main__":
    if '--debug' in sys.argv:
        app.debug = True
    app.run()
    
