# encoding: UTF-8
import sys, os.path
sys.path.insert(0,"..")
from config import Config
import utils.whereami 
import utils.fsdb
import dbscheme
import json
import threading 
import subprocess
import time
import random
from base64 import b64encode

from Queue import Queue, Empty
from utils import passwords

from flask import Flask, request, session, g, redirect, url_for, Response
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


# ---------------- HOME --------------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- LOGIN --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = g.db.Users.read(name = request.form['username'])
        if user is None:
            error = 'Invalid username'
        elif not passwords.check(user.password,request.form['password']):
            error = 'Invalid password'
        else:
            session['logged_user'] = request.form['username'] 
    if 'logged_user' in session:
        flash('You have been logged in')
        return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    if 'logged_user' in session:
        flash('You have been logged out')
        del session['logged_user']
    return redirect(url_for('login'))

# ------------------------------------------

def login_required(fn):
    def f1(*args,**kwargs):
        if 'logged_user' not in session:
            flash('Login is required to access that section')
            return redirect(url_for('login'))
        else:
            return fn(*args,**kwargs)
    f1.__name__ = fn.__name__
    return f1

# ------------------ CONNECT -----------------
@app.route("/connect")
@login_required
def connect():
    return render_template("connect.html")

@app.route("/vnc")
def vnc():
    return render_template("vnc_auto.html")


@app.route("/json-query/<functionname>")
@login_required
def jsonquery(functionname):
    method = request.args["method"]
    args = request.args.getlist("args[]")
    return json.dumps({"html":"<p>%s:data</p>" % functionname})

@app.route("/json-query/connection/<functionname>")
@login_required
def connection_jsonquery(functionname):
    conn = Connection.get(session['logged_user'])
    fn = getattr(conn,functionname)
    result = fn(**request.args)
    txt_result = "\n".join( [ "<p>%s</p>" % x for x in result] ) 
    
    return json.dumps({"html":txt_result, "port" : conn.websocketport, "passwd" : conn.password, "ready" : conn.ready})

class Connection:
    _known_connections = {}
    @classmethod
    def get(cls,username):
        if username in cls._known_connections:
            try:
                cls._known_connections[username].validate()
                return cls._known_connections[username]
            except Exception:
                pass
        c = cls(username)
        return c
    
    def __init__(self, username):
        self._known_connections[username] = self
        self.thread = threading.Thread(target=self._thread)
        self.display = random.randint(1000,1100)
        self.xvfb = None
        self.openbox = None
        self.x11vnc = None
        self.novnc = None
        self.password = b64encode(os.urandom(6))
        self.vncport = random.randint(10000,15000)
        self.websocketport = random.randint(20000,25000)
        self.thread.start()
        self.ready = False
        time.sleep(0.1)
        
        
    def status(self):
        if self.xvfb:
            for klass, line in self.xvfb.read():
                yield "XVFB %s: %s" % (klass,line)

        if self.openbox:
            for klass, line in self.openbox.read():
                yield "OPENBOX %s: %s" % (klass,line)
        """
        if self.x11vnc:
            for klass, line in self.x11vnc.read():
                yield "X11VNC %s: %s" % (klass,line)
        
        if self.novnc:
            for klass, line in self.novnc.read():
                yield "NOVNC %s: %s" % (klass,line)
        """
    def validate(self):
        assert(self.xvfb)
        if self.ready:
            ret = self.x11vnc.popen.poll()
            if ret is not None: raise ValueError, "vnc terminated"
            
        
    def _thread(self):
        

        # Xvfb :30 -screen 0 1024x768x24 -pixdepths 1,4,8,12,16,24,32 -shmem
        self.xvfb = ExternalProcess(
            [
            "/usr/bin/Xvfb",
            ":%d" % self.display,
            "-screen", "0", "1024x768x24",
            "-pixdepths", "1,4,8,12,16,24,32",
            "-shmem",
            ],
            
            )
        time.sleep(1)
        
        # DISPLAY=:30; openbox
        self.openbox = ExternalProcess(
                [
                    "/usr/bin/openbox",
                ],
                env = {'DISPLAY':":%d" % self.display},
            )
        # x11vnc -display :30 -many -speeds 50,500,15 -nowf -shared
        self.x11vnc = ExternalProcess(
                [
                    "/usr/bin/x11vnc",
                    "-display", ":%d" % self.display,
                    "-speeds","10,100,20",
                    "-nowf",
                    "-passwd", self.password,
                    "-autoport", str(self.vncport),
                ],
            )
        # ./utils/launch.sh --listen 10001 --vnc 127.0.0.1:5900
        self.novnc = ExternalProcess(
                [
                    "/usr/local/bin/noVNC-launch",
                    "--listen", str(self.websocketport),
                    "--vnc", "127.0.0.1:%d" % self.vncport,
                ],
            )
        time.sleep(1)
        self.ready = True

class ExternalProcess(object):
    def __init__(self, args, env = {}):
        ON_POSIX = 'posix' in sys.builtin_module_names
        self.args = args
        self.env = env
        self.name = args[0]
        self.popen = subprocess.Popen(self.args, 
            stdout = subprocess.PIPE, stderr = subprocess.PIPE, bufsize=1, close_fds=ON_POSIX, env = env)
        self.q = Queue()
        self.t1 = threading.Thread(target=self.enqueue_output, args=(self.popen.stdout, self.q, "STDOUT"))
        self.t1.daemon = True # thread dies with the program
        self.t1.start()            

        self.t2 = threading.Thread(target=self.enqueue_output, args=(self.popen.stderr, self.q, "STDERR"))
        self.t2.daemon = True # thread dies with the program
        self.t2.start()            
        
        self.output = []
        self.q.put( ("BEGIN"," ".join(args)) )
        
    def enqueue_output(self,out, queue, klass):
        for line in iter(out.readline, b''):
            queue.put( (klass,line) )
        out.close()
    
    def read(self):
        try:
            while True:
                output = self.q.get(True,0.02)
                self.output.append(output)
                yield output
        except Empty:
            pass
            
    def __del__(self):
        try: self.popen.terminate()
        except Exception, e: print e
        
        
        

# -----------------------

@app.route("/favicon.ico")
def logo():
    return redirect(url_for('static', filename='images/icon.png'))


@app.route("/include/<filename>")
def novncinclude(filename):
    mimetype = "text/html"
    if filename.endswith(".css"):
        mimetype = "text/css"
    elif filename.endswith(".js"):
        mimetype = "text/javascript"
        
    response = Response(response = open(os.path.join(Config.Global.novnc,"include",filename)).read()
            #        , status=None, headers=None, mimetype=None, content_type=None, direct_passthrough=False
            , content_type=mimetype)
            
    return response
    # return redirect(url_for('static', filename='novnc-include/' + filename))

if __name__ == "__main__":
    if '--debug' in sys.argv:
        app.debug = True
    app.run(host="0.0.0.0")
    
