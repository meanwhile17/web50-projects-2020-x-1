import os
import requests

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

KEY = b8MRkyrrzhpSc8SZhtx2WA
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
