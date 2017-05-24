"""
Nathan D. Hernandez
Udacity FullStack NanoDegree

Item Catalog Application:
    - ver: 0.1  05/2017
"""

from flask import (Flask, render_template, request, redirect, flash, url_for)

app = Flask(__name__)

from sqlalchemy import create_engine, desc, exc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Helper functions

def getUser():
    user = session.query(User).filter(
                                User.email=='nathandhernandez@gmail.com').one()

    return user

def checkAdmin(user):
    is_admin = False
    for role in user.roles:
        if role.permission == "admin":
            is_admin = True
            break

    return is_admin

# Route Specific

@app.route('/')
@app.route('/catalog/')
def catalogHome():
    print "In catalogHome()"
    user = getUser()
    is_admin = checkAdmin(user)

    categories = session.query(Category).all()
    latest_items = session.query(Item).order_by(
                                            desc(Item.created)).limit(10).all()

    return render_template("catalog.html", user=user, is_admin=is_admin,
                            categories=categories, latest_items=latest_items)

"""
Category Specific
"""
@app.route('/catalog/<category>/')
def categoryInfo(category):
    print "In categoryInfo(category) for %s" % category
    user = getUser()
    is_admin = checkAdmin(user)

    curr_categ = session.query(Category).filter(
                                            Category.name==str(category)).one()

    return render_template("category.html", curr_categ=curr_categ)


"""
Item Specific
"""

@app.route('/catalog/<category>/items/')
def categItems(category):
    print "In categItems(category) for %s" % category
    user = getUser()
    is_admin = checkAdmin(user)

    categories = session.query(Category).all()
    curr_categ = session.query(Category).filter(
                                            Category.name==str(category)).one()
    
    categ_items = session.query(Item).filter(
                           Item.category==curr_categ).order_by(Item.name).all()

    return render_template("categ-items.html", user=user, is_admin=is_admin,
                            categories=categories, curr_categ=curr_categ,
                            categ_items=categ_items)


@app.route('/catalog/<category>/<item>/')
def itemInfo(category, item):
    print "In itemInfo(category, item) for %s | %s" % (category, item)
    user = getUser()
    is_admin = checkAdmin(user)

    curr_categ = session.query(Category).filter(
                                            Category.name==str(category)).one()

    curr_item = session.query(Item).filter(Item.name==str(item)).one()

    return render_template("item.html", curr_item=curr_item)

@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def newCatalogItem():
    print "In newCatalogItem()"
    user = getUser()
    is_admin = checkAdmin(user)

    categories = session.query(Category).order_by(Category.name).all()

    if request.method == 'POST':
        print "In Post"

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']
        categ = request.form['category']

        # Lookup actual category object
        category = session.query(Category).filter(
                                            Category.name==str(categ)).one()

        if category:
            try:
                # Create our Item
                new_item = Item(name=name, description=desc, category=category,
                            created_by=user.email, last_update_by=user.email)

                session.add(new_item)
                session.commit()

                flash("Catalog ITEM added successfully!")
            except exc.IntegrityError as e:
                session.rollback()
                flash("""Cannot Add, ITEM Name/Chosen Category combination
                       already exists...""")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get called"
        return render_template("new-item.html", categories=categories)

@app.route('/catalog/<category>/<item>/edit/', methods=['GET', 'POST'])
def editCatalogItem(category, item):
    print "In editCatalogItem()"
    user = getUser()
    is_admin = checkAdmin(user)

    curr_categ = session.query(
                        Category).filter(Category.name==str(category)).one()
    curr_item = session.query(Item).filter(Item.name==str(item)).one()
    categories = session.query(Category).order_by(Category.name).all()

    if request.method == 'POST':
        print "In Post"

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']
        categ = request.form['category']

        # Lookup actual category object
        category = session.query(Category).filter(
                                            Category.name==str(categ)).one()

        if category and (category == curr_categ):
            # Edit our existing Item
            try:
                curr_item.name = name
                curr_item.description = desc
                curr_item.category = category
                curr_item.last_update_by = user.email

                session.commit()

                msg = "Edited %s successfully!" % curr_item.name
                flash(msg)
            except exc.IntegrityError as e:
                session.rollback()
                flash("""Cannot Edit: Item Name/Chosen Category combination
                       already exists...""")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("edit-item.html", item=curr_item, 
                                categories=categories)

@app.route('/catalog/<category>/<item>/delete/', methods=['GET', 'POST'])
def deleteCatalogItem(category, item):
    print "In deleteCatalogItem()"
    user = getUser()
    is_admin = checkAdmin(user)

    curr_categ = session.query(
                        Category).filter(Category.name==str(category)).one()
    curr_item = session.query(Item).filter(Item.name==str(item)).one()

    if request.method == 'POST':
        print "In Post"

        # Grab our hidden
        frm_name = request.form['name']
        frm_categ = request.form['category']

        if (curr_item.name == frm_name and curr_categ.name == frm_categ):
            
            # We should be good to DELETE our item
            session.delete(curr_item)
            session.commit()

            msg = "Deleted %s successfully!" % curr_item.name
            flash(msg)
            return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("delete-item.html", item=curr_item)

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
