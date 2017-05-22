"""
Nathan D. Hernandez
Udacity FullStack NanoDegree

Item Catalog Application:
    - ver: 0.1  05/2017
"""

from flask import (Flask, render_template, request, redirect, flash, url_for)

app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def catalogHome():
    print "In catalogHome()"
    categories = session.query(Category).all()
    
    return render_template("catalog.html", categories=categories)

@app.route('/users/')
def getUsers():
    print "In getUsers()"
    users = session.query(User).all()

    return render_template("users.html", users=users)

if __name__ == '__main__':
    app.secret_key = "secret"
    app.template_folder = 'templates'
    app.debug = True
    app.run(host = '0.0.0.0', port = 9090)
