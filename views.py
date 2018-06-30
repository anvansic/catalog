from flask import (Flask, render_template, Markup, request, redirect, url_for,
                   jsonify)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from models import Base, Book
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = (json.loads(open('client_secrets.json', 'r')
             .read())['web']['client_id'])

engine = create_engine('sqlite:///books.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)
app = Flask(__name__)
app.config['SECRET_KEY'] = "L0cMW5fcd48dbhcNr8EQkSkd"

@app.route('/', methods=['GET'])
def go_home():

    welcome_message = "This is the Encyclopedia of Books homepage. <br><br>"
    welcome_message += "From here, you can view lists of books sorted by their "
    welcome_message += "genres. If you'd like, you can also login using your "
    welcome_message += "Google account credentials, "
    welcome_message += "which will then give you the privilege to add, edit or "
    welcome_message += "delete titles. Thank you for visiting, and enjoy!"
    welcome_message += "<br><br>"
    welcome_message += "<em>DISCLAIMER:</em> The Encyclopedia of Books has "
    welcome_message += "neither the ability nor the interest to verify the "
    welcome_message += "book information entered by its users."

    # Sets up which links are visible based on login status.
    if login_session.get('credentials') is not None:
        loginout = ("<a id='logout-link' href="+
                    url_for('gdisconnect')+">Logout</a>")
        create_entry_html = ("<a id='link-create-entry' href="+
                             url_for('create_entry')+">New Entry</a>")
    else:
        loginout = ("<a id='login-link' href="+url_for('login_user')+
                    ">Login with Google+</a>")
        create_entry_html = ""

    entry_list = session.query(Book).all()

    return render_template('index.html', welcome_message=welcome_message,
                           loginout=loginout,
                           create_entry_html=create_entry_html,
                           entry_list=entry_list)

@app.route('/login')
def login_user():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # gconnect code and functionality courtesy of Udacity.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps("State doesn't match."), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                             scope='openid email',
                                             redirect_uri='http://localhost:8000')
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("No credentials object created."),
                                 401)
        response.headers['Content-type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s" %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match."),
                                 401)
        response.headers['Content-type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID doesn't match."),
                                 401)
        response.header['Content-type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("User already connected."), 200)
        response.headers['Content-type'] = 'application/json'

    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    if data['name'] == '':
        login_session['username'] = data['email']
        return ("You have signed in with the e-mail %s"
                % login_session['username'])

    else:
        login_session['username'] = data['name']
        return "You are now signed in as %s" % login_session['username']

@app.route('/gdisconnect')
def gdisconnect():
    # gdisconnect code and functionality also courtesy of Udacity.
    access_token = login_session.get('credentials')
    if access_token is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        login_session['credentials'] = None
        login_session['gplus_id'] = None
        login_session['username'] = None

        welcome_message = "<p>You have successfully logged out.</p><br>"
        welcome_message += ("<a href="+url_for('go_home')+">Return to home " +
                            "page</a>")
        return render_template('index.html', welcome_message=welcome_message)
    else:
        # If an error occurs, the login_session fields are nullified anyway
        # to get the application "back on track".
        response = make_response(json.dumps("Could not revoke token. "+
                                 "Credentials will be nullified."), 400)
        login_session['credentials'] = None
        login_session['gplus_id'] = None
        login_session['username'] = None
        response.headers['Content-type'] = 'application/json'
        return response

@app.route('/view_entry/<int:id>/', methods=['GET'])
def view_entry(id):
    entry = session.query(Book).filter_by(id=id).one()
    # Change the year to be B.C. if < 0 and A.D. if >= 0.
    if entry.year < 0:
        displayed_year = str(entry.year * -1) + " B.C."
    else:
        displayed_year = str(entry.year) + " A.D."

    logged_in_options = ""
    if login_session.get('credentials') is not None:
        logged_in_options += ("<a href="+ url_for('edit_entry', id=id)
                              +">Edit</a> ")
        logged_in_options += ("<a href="+ url_for('delete_entry', id=id)
                              +">Delete</a>")

    return render_template('view_book_info.html', entry=entry,
                           displayed_year=displayed_year,
                           logged_in_options=logged_in_options)

@app.route('/view_entry/<int:id>/json', methods=['GET'])
def view_json(id):
    entry = session.query(Book).filter_by(id=id).one()
    entry_json = jsonify(Book=entry.serialize)
    return entry_json

@app.route('/view_entry/<int:id>/edit/', methods=['GET', 'POST'])
def edit_entry(id):
    entry = session.query(Book).filter_by(id=id).one()
    if request.method == 'POST':
        entry.title = request.values['title']
        entry.author = request.values['author']
        entry.year = request.values['year']
        entry.genre = request.values['genre']
        entry.synopsis = request.values['synopsis']
        session.add(entry)
        session.commit()
        return redirect(url_for('go_home'))

    return render_template('edit_entry.html', entry=entry)

@app.route('/view_entry/<int:id>/delete/', methods=['GET', 'POST'])
def delete_entry(id):
    entry = session.query(Book).filter_by(id=id).one()

    if request.method == 'POST':
        request_json = jsonify(request.values)
        if "Yes" in request_json.get_data():
            session.delete(entry)
            session.commit()
            return redirect(url_for('go_home'))
        elif "No" in request_json.get_data():
            print(entry.id)
            return redirect(url_for('view_entry', id=entry.id))
    return render_template('delete_entry.html', entry=entry)

@app.route('/new_entry', methods=['GET', 'POST'])
def create_entry():
    if request.method == 'POST':
        newEntry = Book(title=request.values['title'],
                        author=request.values['author'],
                        year=int(request.values['year']),
                        genre=request.values['genre'],
                        synopsis=request.values['synopsis'])
        session.add(newEntry)
        session.commit()
        return redirect(url_for('go_home'))

    else:
        return render_template('create_entry.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
