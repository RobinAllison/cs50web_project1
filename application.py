import os

from flask import Flask, session, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from csv import reader

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystemf
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/logout")
def logout():
    session["username"] = None
    return render_template("index.html")


@app.route("/", methods=["POST", "GET"])
def index():
    if session.get("username") == None:
        username = request.form.get("username")
        session["username"] = username
    if session.get("username") == None:
        return render_template("index.html")
    else:
        username = session["username"]
        searched_for = request.form.get("searched_for")
        if searched_for != None:
            books = db.execute(
                "SELECT * FROM books WHERE title LIKE (:variable)", {"variable": '%'+searched_for+'%'}).fetchall()
            for book in books:
                infile = book
                for line in reader(infile):
                    print(line)
        else:
            books = []
        return render_template("search.html", books=books)


@app.route("/register", methods=["POST", "GET"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if username != None and password != None:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                   {"username": username, "password": password})
        db.commit()
        session["username"] = username
    return render_template("registration.html", username=username)


@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")


@app.route("/<string:name>")
def hello(name):
    return f"hello, {name}"
