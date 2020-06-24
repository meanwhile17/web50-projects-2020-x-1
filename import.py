from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import csv
import os
from time import time
from datetime import datetime


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

#Create the session
session = sessionmaker()
session.configure(bind=engine)
s = session()


csvf = '/Users/Sergey/Documents/cs50/project0/cs50project1/books.csv'

t = time()

#class Books(Base):
#    __tablename__ = "books"
#    book_id = Column(Integer, primary_key=True)
#    isbn = Column(String)
#    title = Column(String)
#    author = Column(String)
#    year = Column(Integer)

#db.execute("COPY books FROM '/Users/Sergey/Documents/cs50/project0/cs50project1/books.csv' DELIMITER ',' CSV HEADER");
#db.commit()

with open(csvf, mode='r') as csvfile:
    csv_header_pre = csv.reader(csvfile)
    data = list(csv_header_pre)
    length = len(data)

    print (length)

#"\copy books FROM '/Users/Sergey/Documents/cs50/project0/cs50project1/books.csv' DELIMITER ',' CSV HEADER"

#books_list_dicts = []

#for row in range(1,length):
#    row_dict = {}
#    row_dict['isbn'] = data[row][0]
#    row_dict['title'] = data[row][1]
#    row_dict['author'] = data[row][2]
#    row_dict['year'] = data[row][3]
#    books_list_dicts.append(row_dict)

#print(books_list_dicts)

#for book in books_list_dicts:
#    row = Books(**book)
#    s.add(row)

# db.commit()

# row by row import into DB
for row in range(1,length):

    isbn = data[row][0]
    title = data[row][1]
    author = data[row][2]
    year = data[row][3]
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {"isbn" : isbn, "title" : title, "author" : author, "year" : year})

db.commit()

#db.execute("INSERT INTO books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {"isbn" : isbn, "title" : title, "author" : author, "year" : year})
#db.commit()

time_elapsed = str(time() - t)

print ("import complete")
print ("Time elapsed: " + time_elapsed + " s.")



# Insert data into the Database

#db.execute("INSERT INTO users (email, hash, user_ip) VALUES(:email, :hash, :user_ip)", {"email" : request.form.get("email"), "hash" : generate_password_hash(request.form.get("reg_password")), "user_ip" : user_ip})
#db.commit()
