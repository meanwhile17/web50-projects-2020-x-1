import os
import requests

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_login import LoginManager, login_manager, login_user, logout_user
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine, cast, Numeric
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
from time import sleep
from decimal import Decimal

# from helpers import apology, lookup

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'



login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
#app.login_manager
# login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(alternative_id=user_id).first()

def get_id(self):
    return unicode(self.alternative_id)



# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Goodread credentials

KEY = "b8MRkyrrzhpSc8SZhtx2WA"
SECRET = "zT3nTIZe3dxOcGbOpIaC09Dt2cH9tTHiKCNlRdRERU"


# Setting Database url
# DATABASE_URL = postgres://iazikazarvclta:a111e36bace34b9cefd9051b33ae0e0c9d60f08d41ba5bced9ea6b0d50f5b02a@ec2-52-201-55-4.compute-1.amazonaws.com:5432/d3aik6deiev6a6

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"), pool_size=20)
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():

    return render_template("index.html")


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
        elif db.execute("SELECT * FROM users WHERE email = :email", {"email": request.form.get("email")}).rowcount > 0:
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
        db.execute("INSERT INTO users (email, hash, user_ip) VALUES(:email, :hash, :user_ip)", {"email" : request.form.get("email"), "hash" : generate_password_hash(request.form.get("reg_password")), "user_ip" : user_ip})
        db.commit()

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          {"email" : request.form.get("email")}).fetchall()


        print(rows)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"] , request.form.get("password")):
            return apology("invalid username and/or password", 403)

        #flash('Logged in successfully.')


        # Remember which user has logged in
        #user = str(rows[0]["id"])

        #login_user(remember=True, force=True)

        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Let's user search the isbn, title, author"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Getting user input from the form

        user_input_isbn = str('%' + request.form.get("user_input_isbn") + '%') if len(request.form.get("user_input_isbn")) > 0 else None

        user_input_title = str('%' + request.form.get("user_input_title") + '%') if len(request.form.get("user_input_title")) > 0 else None

        user_input_author = str('%' + request.form.get("user_input_author") + '%') if len(request.form.get("user_input_author")) > 0 else None

        print (user_input_isbn)
        print (user_input_title)
        print (user_input_author)



    # Query database for username
        rows = db.execute("SELECT isbn,title,author FROM books WHERE isbn LIKE :isbn   OR title LIKE :title OR author LIKE :author ",
        {"isbn" : user_input_isbn, "title" : user_input_title, "author" : user_input_author}).fetchall()

        if len(rows) < 1:
            response = "No books were found that matched your criteria"
        else:
            response = "This is what we found "

        return render_template("search.html", rows=rows, response=response)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")


@app.route('/book/<isbn>', methods=["POST", "GET"])
@login_required
def book(isbn):
    """ See selected book details """

    """ Get data to render the page """

    book_info = db.execute("SELECT isbn,title,author,year FROM books WHERE isbn = :isbn ",
    {"isbn" : isbn}).fetchall()

    # Check if the user already has left a review
    book_club_user_review = db.execute("SELECT rating, review_text FROM reviews WHERE book_isbn = :isbn AND reviewer_user_id = :reviewer_user_id",
    {"isbn" : isbn, "reviewer_user_id" : session["user_id"]}).fetchall()

    # Get all users reviews
    book_club_all_user_review = db.execute("SELECT rating, review_text FROM reviews WHERE book_isbn = :isbn",
    {"isbn" : isbn}).fetchall()

    goodreads_reviews = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": 'b8MRkyrrzhpSc8SZhtx2WA', "isbns": isbn})

    if not book_info:
        return apology("invalid book data", 403)
    else:
        book_info_list = book_info[0]
    print(book_info)


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # get data from the form

        reviewer_user_id = session["user_id"]

        review_text = request.form.get("review_text")

        rating = request.form.get("rating")


        # Else register new review
        db.execute("INSERT INTO reviews (reviewer_user_id, book_isbn, review_text, rating) VALUES(:reviewer_user_id, :book_isbn, :review_text, :rating)", {"reviewer_user_id" : reviewer_user_id, "book_isbn" : book_info_list.isbn, "review_text" : review_text, "rating" : rating})
        db.commit()
        db.close()

        print("post", book_club_user_review, review_text, session["user_id"])

        return render_template('book.html', book_info = book_info, book_info_list = book_info_list, goodreads_reviews = goodreads_reviews.json(), book_club_user_review=book_club_user_review, book_club_all_user_review=book_club_all_user_review)

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Check if the user already has left a review
        #book_club_user_review = db.execute("SELECT rating, review_text FROM reviews WHERE book_isbn = :isbn AND reviewer_user_id = :reviewer_user_id",
        #{"isbn" : isbn, "reviewer_user_id" : session["user_id"]}).fetchall()

        print("GET", book_club_user_review, session["user_id"])

        return render_template('book.html', book_info = book_info, book_info_list = book_info_list, goodreads_reviews = goodreads_reviews.json(), book_club_user_review=book_club_user_review, book_club_all_user_review=book_club_all_user_review)

@app.route('/book_review/<isbn>', methods=["POST", "GET"])
@login_required
def book_review(isbn):
    """ See selected book details """

    """ Get data to render the page """

    book_info = db.execute("SELECT isbn,title,author,year FROM books WHERE isbn = :isbn ",
    {"isbn" : isbn}).fetchall()
    db.close()

    # Check if the user already has left a review
    book_club_user_review = db.execute("SELECT rating, review_text FROM reviews WHERE book_isbn = :isbn AND reviewer_user_id = :reviewer_user_id",
    {"isbn" : isbn, "reviewer_user_id" : session["user_id"]}).fetchall()
    db.close()

    if not book_info:
        return apology("invalid book data", 403)
    else:
        book_info_list = book_info[0]
    print(book_info)

    # User reached route via POST (as by submitting a review via POST)
    if request.method == "POST":

        # get data from the form

        reviewer_user_id = session["user_id"]

        review_text = request.form.get("review_text")

        rating = request.form.get("rating")


        # Else register new review
        db.execute("INSERT INTO reviews (reviewer_user_id, book_isbn, review_text, rating) VALUES(:reviewer_user_id, :book_isbn, :review_text, :rating)", {"reviewer_user_id" : reviewer_user_id, "book_isbn" : book_info_list.isbn, "review_text" : review_text, "rating" : rating})
        db.commit()
        db.close()


        return render_template('book_review.html', book_info = book_info, book_info_list = book_info_list, book_club_user_review=book_club_user_review)


    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Check if the user already has left a review
        #book_club_user_review = db.execute("SELECT rating, review_text FROM reviews WHERE book_isbn = :isbn AND reviewer_user_id = :reviewer_user_id",
        #{"isbn" : isbn, "reviewer_user_id" : session["user_id"]}).fetchall()

        print("GET", book_club_user_review, session["user_id"])

        return render_template('book_review.html', book_info = book_info, book_info_list = book_info_list,  book_club_user_review=book_club_user_review)

@app.route('/book_review_success/<isbn>', methods=["POST"])
@login_required
def book_review_success(isbn):

    """ Get data to render the page """

    book_info = db.execute("SELECT isbn,title,author,year FROM books WHERE isbn = :isbn ",
    {"isbn" : isbn}).fetchall()
    db.close()

    if not book_info:
        return apology("invalid book data", 403)
    else:
        book_info_list = book_info[0]
    print(book_info)

    # get data from the form

    reviewer_user_id = session["user_id"]

    review_text = request.form.get("review_text")

    rating = request.form.get("rating")


    # Else register new review
    db.execute("INSERT INTO reviews (reviewer_user_id, book_isbn, review_text, rating) VALUES(:reviewer_user_id, :book_isbn, :review_text, :rating)", {"reviewer_user_id" : reviewer_user_id, "book_isbn" : book_info_list.isbn, "review_text" : review_text, "rating" : rating})
    db.commit()
    db.close()


    return render_template('book_review_success.html', book_info = book_info, book_info_list = book_info_list)

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    logout_user()

    session.clear()
    # old session.pop('user_id')

    # Redirect user to login form
    return redirect("/")

@app.route("/api/<isbn>", methods=["GET"])
#@login_required
def api(isbn):

    """ Get data to render the page """
    book_info = {}

    book_info = db.execute("SELECT books.title, books.author, books.year, books.isbn, COUNT(review_text), CAST(AVG(rating) AS VARCHAR(4)) AS average_rating FROM books JOIN reviews ON books.isbn = reviews.book_isbn WHERE isbn = :isbn GROUP BY books.title, books.author, books.year, books.isbn",
    {"isbn" : isbn}).fetchall()
    db.close()

    if not book_info:
        return apology("invalid book data", 404)
    else:
        book_info_list = book_info[0]

    print("book_info is :", book_info)
    print("book_info_list is :", book_info_list)


    #return jsonify(book_info)

    return jsonify({'book_info': [dict(row) for row in book_info]})
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

# Error
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
