from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash
)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Weapon, ItemInfo, User
from flask import session as login_session
from collections import OrderedDict
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import random
import string
import requests
import httplib2
import json

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']
APPLICATION_NAME = "Udacity Item Catalog"

# Connect to Database and create database session
engine = create_engine('sqlite:///fortniteitems.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Check if User already exists, if not create new row
def get_or_create(sesion, model, **kwargs):
    instance = sesion.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Login
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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    get_or_create(session, User, email=login_session['email'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;' +
               'border-radius: 150px;-webkit-border-radius: 150px;' +
               '-moz-border-radius: 150px;"> ')
    print "done!"
    return output


# Disconnect google user
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
                                 'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        login_session['access_token']
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print json.dumps(result, indent=2)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Location'] = '/weapons'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token' +
                                 ' for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Index page to show all categories
@app.route('/')
@app.route('/weapons/')
def showWeapons():
    weapons = session.query(Weapon).order_by(asc(Weapon.name))
    if 'username' not in login_session:
        return render_template('index.html', weapons=weapons)
    else:
        return render_template('index.html', weapons=weapons,
                               login_state=login_session['username'])


# Show all item info for category
@app.route('/weapons/<int:weapon_class_id>/')
@app.route('/weapons/<int:weapon_class_id>/list')
def weaponList(weapon_class_id):
    weapon_class = session.query(Weapon).filter_by(
                                 id=weapon_class_id).first()
    items = session.query(ItemInfo).filter_by(
                          weapon_id=weapon_class.id)
    return render_template('weapon_templ.html',
                           weapon_class=weapon_class,
                           items=items)


# Show all info for item
@app.route('/details/<int:weapon_id>/')
def weaponDetails(weapon_id):
    items = session.query(ItemInfo).filter_by(
                          weapon_id=weapon_id).one()
    weapon_class = session.query(Weapon).filter_by(
                                 id=items.weapon_id).first()
    return render_template('weapon_templ.html',
                           weapon_class=weapon_class,
                           items=[items])


# Create new item
@app.route('/weapons/<int:weapon_class_id>/new', methods=['GET', 'POST'])
def newItem(weapon_class_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        user = session.query(User).filter_by(
                             email=login_session['email']).first()

        newItem = ItemInfo(name=request.form['name'],
                           description=request.form['description'],
                           damage=request.form['damage'],
                           dps=request.form['dps'],
                           weapon_id=weapon_class_id,
                           user_id=user.id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('weaponList',
                                weapon_class_id=weapon_class_id))
    else:
        category = session.query(Weapon)
        return render_template('newItem.html',
                               weapon_class_id=weapon_class_id,
                               category=category)


# Create new category
@app.route('/weapons/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        user = session.query(User).filter_by(
                             email=login_session['email']).first()

        newCategory = Weapon(name=request.form['name'], user_id=user.id)
        session.add(newCategory)
        session.commit()
        weapon_class = session.query(Weapon).filter_by(
                                     name=request.form['name']).one()
        items = session.query(ItemInfo).filter_by(weapon_id=weapon_class.id)
        return render_template('weapon_templ.html',
                               weapon_class=weapon_class,
                               items=items,
                               redirect="1")
    else:
        weapon_class = session.query(Weapon).first()
        return render_template('newCategory.html',
                               weapon_class_id=weapon_class.id)


# Edit item
@app.route('/weapons/<int:weapon_class_id>/<int:weapon_id>/edit',
           methods=['GET', 'POST'])
def editItemInfo(weapon_class_id, weapon_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Weapon)
    editedItem = session.query(ItemInfo).filter_by(id=weapon_id).one()

    if login_session["email"] != editedItem.user.email:
        return render_template('error.html')
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['damage']:
            try:
                float(request.form['damage'])
            except ValueError:
                flash("expecting a number but received a non-numerical \
                        value for the 'Damage' field")
                return render_template('editItemInfo.html',
                                       weapon_class_id=weapon_class_id,
                                       weapon_id=weapon_id,
                                       item=editedItem,
                                       category=category)
            editedItem.damage = request.form['damage']
        if request.form['dps']:
            try:
                float(request.form['dps'])
            except ValueError:
                flash("expecting a number but received a non-numerical " +
                      "value for the 'DPS' field")
                return render_template('editItemInfo.html',
                                       weapon_class_id=weapon_class_id,
                                       weapon_id=weapon_id,
                                       item=editedItem,
                                       category=category)
            editedItem.dps = request.form['dps']
        if request.form['weapon_class']:
            editedItem.weapon_id = request.form['weapon_class']
        session.add(editedItem)
        session.commit()
        return redirect(
            url_for('weaponList', weapon_class_id=editedItem.weapon_id))
    else:
        return render_template(
            'editItemInfo.html', weapon_class_id=weapon_class_id,
            weapon_id=weapon_id, item=editedItem, category=category)


# Edit category
@app.route('/weapons/<int:weapon_class_id>/edit',
           methods=['GET', 'POST'])
def editCategoryInfo(weapon_class_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedCategory = session.query(Weapon).filter_by(id=weapon_class_id).one()
    items = session.query(ItemInfo).filter_by(weapon_id=editedCategory.id)

    if login_session["email"] != editedCategory.user.email:
        return render_template('error.html')

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        return render_template('weapon_templ.html',
                               weapon_class=editedCategory,
                               items=items, redirect="1")
    else:
        return render_template('editCategory.html',
                               weapon_class_id=weapon_class_id,
                               item=editedCategory)


# Delete item
@app.route('/weapons/<int:weapon_class_id>/<int:weapon_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(weapon_class_id, weapon_id):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(ItemInfo).filter_by(id=weapon_id).first()

    if login_session["email"] != itemToDelete.user.email:
        return render_template('error.html')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('weaponList', weapon_class_id=weapon_class_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# Delete category
@app.route('/weapons/<int:weapon_class_id>/delete',
           methods=['GET', 'POST'])
def deleteCategory(weapon_class_id):
    if 'username' not in login_session:
        return redirect('/login')
    catToDelete = session.query(Weapon).filter_by(id=weapon_class_id).one()

    if login_session["email"] != catToDelete.user.email:
        return render_template('error.html')
    if request.method == 'POST':
        itemsToDelete = session.query(ItemInfo).filter_by(
                                      id=catToDelete.id).delete()
        session.delete(catToDelete)
        session.commit()
        nextCat = session.query(Weapon).first()
        items = session.query(ItemInfo).filter_by(id=nextCat.id)
        return render_template('weapon_templ.html', weapon_class=nextCat,
                               items=items, redirect="1")
    else:
        return render_template('deleteCategory.html', category=catToDelete)


# Return list of all categories and items in JSON
@app.route('/catalog.json')
def showall_JSON():
    itemList = []
    weapon = session.query(Weapon).all()
    for w in weapon:
        items = session.query(ItemInfo).filter_by(
            weapon_id=w.id).all()
        itemList += [{"id": w.id, "name": w.name,
                      "weapons": [i.serialize for i in items]}]
    return jsonify(Category=itemList)


# Return list of all items for category in JSON
@app.route('/weapons/<int:weapon_class_id>/json')
def weaponInfoJSON(weapon_class_id):
    weapon = session.query(Weapon).filter_by(id=weapon_class_id).one()
    items = session.query(ItemInfo).filter_by(
                            weapon_id=weapon_class_id).all()
    return jsonify(Category=[{"id": weapon.id, "name": weapon.name,
                             "weapons:": [i.serialize for i in items]}])


# Return details for item in JSON
@app.route('/details/<int:weapon_id>/json')
def specificWeaponInfoJSON(weapon_id):
    items = session.query(ItemInfo).filter_by(
                            weapon_id=weapon_id).all()
    return jsonify(Item=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
