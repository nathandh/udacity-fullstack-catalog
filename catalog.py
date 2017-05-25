"""
Nathan D. Hernandez
Udacity FullStack NanoDegree

Item Catalog Application:
    - ver: 0.1  05/2017
"""

import os, hashlib, httplib2, requests, json

from flask import (Flask, render_template, request, redirect, flash, 
                   url_for, make_response, session as login_session)

app = Flask(__name__)

from sqlalchemy import create_engine, desc, exc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# OAuth2 related imports
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

CLIENT_ID = json.loads(
                   open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Helper functions

def getUser():
    user = ""
    try:
        email = login_session['email']
        user = session.query(User).filter(
                            User.email==email).one()
    except LookupError:
        user = None
        print "User doesn't exist, or error retrieving, from our database."
    finally:
        return user

def checkAdmin(user):
    is_admin = False
    if user is not None:
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

@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategory():
    print "In newCategory()"
    user = getUser()
    is_admin = checkAdmin(user)

    if request.method == 'POST':
        print "In Post"

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']

        if name != "" and desc != "":
            try:
                # Create our Category
                new_categ = Category(name=name, description=desc,
                            created_by=user.email, last_update_by=user.email)

                session.add(new_categ)
                session.commit()

                flash("Catalog CATEGORY added successfully!")
            except exc.IntegrityError as e:
                session.rollback()
                flash("""Cannot Add, Category with chosen NAME 
                      already exists...""")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get called"
        return render_template("new-category.html")

@app.route('/catalog/<category>/edit/', methods=['GET', 'POST'])
def editCategory(category):
    print "In editCategory()"
    user = getUser()
    is_admin = checkAdmin(user)

    curr_categ = session.query(
                        Category).filter(Category.name==str(category)).one()

    if request.method == 'POST':
        print "In Post"

        # Grab our values
        name = request.form['name']
        desc = request.form['desc']
        categ = request.form['category']

        # Lookup actual category object for verification of submit
        category = session.query(Category).filter(
                                            Category.name==str(categ)).one()

        if category and (category == curr_categ):
            # Edit our existing Category
            try:
                curr_categ.name = name
                curr_categ.description = desc
                curr_categ.last_update_by = user.email

                session.commit()

                msg = "Edited category %s successfully!" % curr_categ.name
                flash(msg)
            except exc.IntegrityError as e:
                session.rollback()
                flash("Cannot Edit: Category Name already exists...")
            finally:
                return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("edit-category.html", category=curr_categ)

@app.route('/catalog/<category>/delete/', methods=['GET', 'POST'])
def deleteCategory(category):
    print "In deleteCategory()"
    user = getUser()
    is_admin = checkAdmin(user)

    curr_categ = session.query(
                        Category).filter(Category.name==str(category)).one()

    if request.method == 'POST':
        print "In Post"

        # Grab our hidden form values
        frm_name = request.form['name']

        if (curr_categ.name == frm_name):

            # We should be good to DELETE our category
            for item in curr_categ.items:
                session.delete(item)
                
            session.delete(curr_categ)
            session.commit()

            msg = "Deleted %s successfully!" % curr_categ.name
            flash(msg)
            return redirect(url_for('catalogHome'))
    else:
        print "Get request called"
        return render_template("delete-category.html", category=curr_categ)


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

"""
Login Specific
"""

@app.route('/login/')
def showLogin():
    state = hashlib.sha256(os.urandom(1024)).hexdigest() 
    login_session['state'] = state
    return render_template("login.html", STATE=state)
    # return "The current login session state is %s" % login_session['state']

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        print "request args: %s" % request.args.get('state')
        print "login_session: %s" % login_session['state']
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        code = request.data
        try:
            # Upgrade auth code into credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(json.dumps("""Failed to upgrade the 
                                     authorization code."""), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that access token is valid
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
                % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # Check result for errors
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'        
            return response

        # Verify access token is for intended user
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(json.dumps("""Token's user ID doesn't 
                                    match given user ID."""), 401)
            response.header['Content-Type'] = 'application/json'
            return response

        # Verify access token is valid for this app
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("""Token's client ID doesn't 
                                     match the app."""), 401)
            print "Token's client ID does not match the app's."
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check if user is already LOGGED IN
        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps("""Current user is already 
                                     connected."""), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store access token in session for later use
        login_session['credentials'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # Get Google User info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']

        # See if user is already in our database
        user = getUser()
        if user is None:
            # Set Google login type
            logintype = session.query(LoginType).filter(source=="google").one()

            # 1st time User, grab default 'contrib' Role
            c_role = session.query(Role).filter(permission=="contrib").one()
            # Admin role
            a_role = session.query(Role).filter(permission=="admin").one()
            # UNCOMMENT to apply Admin and Contrib roles
            # new_user_roles = [c_role, a_role]
            # COMMENT next line if you uncomment preceding line
            new_user_roles = [c_role]
            # Store our User info to recall later
            new_user = User(name=data['name'], picture=data['picture'],
                            email=data['email'],roles=new_user_roles,
                            logintype_id=logintype.id)
            
            session.add(new_user)
            session.commit()
        elif user.email == data['email']:
            # Just update our stored data in case something changed:
            user.name = data['name']
            user.picture = data['picture']
            session.commit()
            
        output = ""
        output += "<h1>Welcome, "
        output += login_session['username']
        output += "!</h1>"
        output += "<img src='"
        output += login_session['picture']
        output += """ ' style='width: 300px; height: 300px; 
                  border-radius: 150px; -webkit-border-radius: 150px; 
                  -moz-border-radius: 150px;'> """
        flash("You are now logged in as %s" % login_session['username'])
        print "Done with Google Login!"
        return output

@app.route("/logout/")
@app.route("/gdisconnect/")
def gdisconnect():
    # Disconnect a logged in / connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # Execute GET to revoke current token
        access_token = credentials
        url = ("https://accounts.google.com/o/oauth2/revoke?token=%s" % 
               access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]

        if result['status'] == '200':
            # Reset the user's session
            del login_session['credentials']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['picture']
            del login_session['email']
              
            response = make_response(json.dumps("Successfully disconnected."),
                                    200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            # Other than 200 response
            response = make_response(json.dumps(
                                 "Failed to revoke token for the given user."), 
                                 400)
            response.headers['Content-Type'] = 'application/json'
            return response
            
if __name__ == '__main__':
    app.secret_key = "secret"
    app.template_folder = 'templates'
    app.debug = True
    app.run(host = '0.0.0.0', port = 9090)
