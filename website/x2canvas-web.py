import sys, os, os.path
# Determine current script directory
SCRIPT_DIR = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = os.path.realpath(os.path.join(SCRIPT_DIR, "../libraries"))
# Search for libraries . . . 
LIBRARIES = []
for dirname in sorted(os.listdir(LIBRARY_DIR)):
    dirpath = os.path.join(LIBRARY_DIR,dirname)
    if not os.path.isdir(dirpath): continue
    LIBRARIES.append(dirpath)
sys.path[:0] = LIBRARIES 
# ;;

## ============================================== 
## ============================================== 
## ============================================== 


from flask import Flask, request, session, g, redirect, url_for
from flask import abort, render_template, flash

USERNAME = 'admin'
PASSWORD = 'password'
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)



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
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)




if __name__ == "__main__":
    if '--debug' in sys.argv:
        app.debug = True
    app.run()
    
