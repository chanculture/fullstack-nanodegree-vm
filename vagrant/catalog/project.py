from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from database_setup import Base, User, Category, Item

from sqlalchemy import create_engine
from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random, string, json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

# Imports for Image Upload
import os
from flask import send_from_directory, send_file

app = Flask(__name__)

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
# Upload max file size 4MB
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

ITEM_IMAGE_PATH = "images/"
CLIENT_ID = json.loads(open('g_client_secrets.json', 'r').read())['web']['client_id']

# which database are we connecting to
engine = create_engine('sqlite:///itemcatalog.db')

# bind engine to the Base class, makes connection between class definition
# and and their corresponding tables within the database
Base.metadata.bind = engine

# establishing link of communication between code execution and the engine
# created above
DBSession = sessionmaker(bind = engine)
session = DBSession()

# For a given file, return whether it's an allowed type or not

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def uploadItemImage(file, item):
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = renameItemFilename(file.filename, item)
        # Save the file to the static folder so flask can serve it later
        file.save(os.path.join("static/", ITEM_IMAGE_PATH, filename))
        return filename
    elif not allowed_file(file.filename):
        flash("Image File Type Not Allowed")
    return ""

def renameItemFilename(filename, item):
    extension = filename.rsplit('.', 1)[1]
    return str(item.id) + "." + extension

# Create anti-forgery state token

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', state=state)

# gConnect connect functions

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = "google"
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    checkUserExists()

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Facebook connect functions

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    checkUserExists()

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        print "User logged out"
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))

# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], profile_picture    =login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo():
    if 'user_id' not in login_session:
        user = None
    else:
        user_id = login_session['user_id']
        user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Returns the database user.id if the user already exists
# (determined by email address)
def checkUserExists():
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return user_id

def checkUserLoggedInStatus():
    if 'user_id' not in login_session:
        return False
    return True

# API Extensions

@app.route('/catalog/JSON')
def catalogJSON():
    items = session.query(Item).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/catalog/<string:categoryname>/JSON')
def categoryItemsJSON(categoryname):
    category = session.query(Category).filter_by(name=categoryname).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/catalog/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])

@app.route('/catalog/<string:categoryname>/<string:itemname>/JSON')
def itemJSON(categoryname, itemname):
    category = session.query(Category).filter_by(name=categoryname).one()
    item = session.query(Item).filter_by(category_id=category.id, name=itemname).one()
    return jsonify(Item=item.serialize)

@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).all()
    # TODO: order by descending
    items = session.query(Item).order_by(Item.date_added.desc()).limit(10)
    return render_template('catalog.html', categories=categories, items=items)

@app.route('/catalog/<string:categoryname>/items')
def showCategoryItems(categoryname):
    category = session.query(Category).filter_by(name=categoryname).one()
    items = session.query(Item).filter_by(category=category)
    user = getUserInfo()
    return render_template('items.html', items=items, category=category, user=user)

@app.route('/catalog/<string:categoryname>/<string:itemname>')
def showItem(categoryname, itemname):
    category = session.query(Category).filter_by(name=categoryname).one()
    item = session.query(Item).filter_by(name=itemname, category=category).one()
    user = getUserInfo()
    #print send_from_directory(app.config['UPLOAD_FOLDER'],item.image_url)
    return render_template('item.html', item=item, user=user, itemimagepath=ITEM_IMAGE_PATH)

@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category']).one()
        if session.query(Item).filter_by(name=request.form['name'], category=category).count() == 0:
            newItem = Item(
                name=request.form['name'],
                description=request.form['description'],
                category=category,
                user_id=login_session['user_id'])
            session.add(newItem)
            # need to generate item.id to rename the file
            session.commit()
            file = request.files['file']
            if file != None:
                newItem.image_url = uploadItemImage(file, newItem)
                session.add(newItem)
                session.commit()
            flash("Item Created")
        else:
            flash("Item with duplicate name already exists for the given category")

        if request.form['preselectedcat'] == "yes":
            return redirect(url_for('showCategoryItems', categoryname=category.name))
        else:
            return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).all()
        return render_template('newitem.html', categories=categories, selectedcategory="")

# This routing is used to have a preselected category
@app.route('/catalog/<string:categoryname>/item/new')
def newItemFromCategory(categoryname):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    return render_template('newitem.html', categories=categories, selectedcategory=categoryname)

@app.route('/catalog/<string:categoryname>/<string:itemname>/edit', methods=['GET', 'POST'])
def editItem(categoryname, itemname):
    if 'username' not in login_session:
        return redirect('/login')
    user = getUserInfo()
    category = session.query(Category).filter_by(name=categoryname).one()
    itemForEdit = session.query(Item).filter_by(name=itemname, category=category).one()
    if itemForEdit.user_id != user.id:
        flash("You are not authorized to edit that item")
        return redirect(url_for('showCategoryItems', categoryname=categoryname))
    if request.method == 'POST':
        if request.form['name']:
            itemForEdit.name = request.form['name']
        if request.form['description']:
            itemForEdit.description = request.form['description']
        if request.form['category']:
            newcategory = session.query(Category).filter_by(name=request.form['category']).one()
            itemForEdit.category = newcategory
        if request.files['file']:
            file = request.files['file']
            itemForEdit.image_url = uploadItemImage(file, itemForEdit)
        session.add(itemForEdit)
        session.commit()
        flash("Item Edited")
        return redirect(url_for('showCategoryItems', categoryname=categoryname))
    else:
        categories = session.query(Category).all()
        return render_template('edititem.html', item=itemForEdit, categories=categories, itemimagepath=ITEM_IMAGE_PATH)

@app.route('/catalog/<string:categoryname>/<string:itemname>/delete', methods=['GET', 'POST'])
def deleteItem(categoryname, itemname):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=categoryname).one()
    itemForDelete = session.query(Item).filter_by(name=itemname, category=category).first()
    user = getUserInfo()
    if itemForDelete.user_id != user.id:
        flash("You are not authorized to delete that item")
        return redirect(url_for('showCategoryItems', categoryname=categoryname))
    if request.method == 'POST':
        if itemForDelete.image_url != "":
            try:
                os.remove(os.path.join("static/", ITEM_IMAGE_PATH, itemForDelete.image_url))
            except OSError:
                print "file was not deleted"
        session.delete(itemForDelete)
        session.commit()
        flash("Item Deleted")
        return redirect(url_for('showCategoryItems', categoryname=categoryname))
    else:
        return render_template('deleteitem.html', item=itemForDelete)

# This method provides the user an option to remove an item's image without
# having to delete the image
@app.route('/catalog/<string:categoryname>/<string:itemname>/image/delete')
def removeItemImage(categoryname, itemname):
    category = session.query(Category).filter_by(name=categoryname).one()
    item = session.query(Item).filter_by(name=itemname, category=category).first()
    try:
        os.remove(os.path.join("static/", ITEM_IMAGE_PATH, item.image_url))
        item.image_url = ""
        session.add(item)
        session.commit()
        flash("Item's Image Was Deleted")
    except OSError:
        print "log: file was not deleted"
    categories = session.query(Category).all()
    return render_template('edititem.html', item=item, categories=categories, itemimagepath=ITEM_IMAGE_PATH)

# This was used for testing:
#@app.route('/users')
#def showUsers():
#    users = session.query(User).all()
#    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.secret_key = 'secret'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)