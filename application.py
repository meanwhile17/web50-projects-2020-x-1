import os
import requests

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Goodread credentials

KEY = b8MRkyrrzhpSc8SZhtx2WA
SECRET = zT3nTIZe3dxOcGbOpIaC09Dt2cH9tTHiKCNlRdRERU


# Setting Database url
# DATABASE_URL = postgres://iazikazarvclta:a111e36bace34b9cefd9051b33ae0e0c9d60f08d41ba5bced9ea6b0d50f5b02a@ec2-52-201-55-4.compute-1.amazonaws.com:5432/d3aik6deiev6a6

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"


@app.route("/register", methods=["GET", "POST"])
# 1. when requested via GET, should display registration form (pretty similar to login.html)
# 2. When form is submitted via POST, insert the new user into users table
# 3. Be sure to check for invalid inputs, and to hash the users password(check vs existing users, check the match of passwords)
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must enter email", 403)

        # Ensure username is not taken
        elif len(db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))) > 0:
            return apology("email already exists", 403)

        # Ensure password was submitted
        elif not request.form.get("reg_password"):
            return apology("must enter password", 403)

        # Ensure 2 passwords match
        elif request.form.get("reg_password") != request.form.get("check_reg_password"):
            return apology("passwords should match", 403)

        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            user_ip = request.environ['REMOTE_ADDR']
        else:
            user_ip = request.environ['HTTP_X_FORWARDED_FOR']


        # Else register new user
        #else:
        db.execute("INSERT INTO users (email, hash, user_ip) VALUES(:email, :hash, :user_ip)", email=request.form.get("email"), hash = generate_password_hash(request.form.get("reg_password")), user_ip = user_ip)

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
