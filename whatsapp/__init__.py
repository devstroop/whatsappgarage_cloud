import pyrebase
from flask import Flask
from datetime import datetime
from flask import render_template, redirect, url_for, request, make_response
import docker

docker_client = docker.from_env()
app = Flask(__name__)
app.secret_key = "abcdefghijklmnopqrstuvwxyz"

config = {
    "apiKey": "AIzaSyC8XExTtVUJud7h3I77uKsTk1qUniqWyPs",
    "authDomain": "whatsappgarage.firebaseapp.com",
    "databaseURL": "https://whatsappgarage-default-rtdb.firebaseio.com",
    "projectId": "whatsappgarage",
    "storageBucket": "whatsappgarage.appspot.com",
    "messagingSenderId": "49122558182",
    "appId": "1:49122558182:web:e13a4243db78ccc2cfbb27",
    "measurementId": "G-445QG7JB3S"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


def get_user(token):
    try:
        _response = auth.get_account_info(token)
        _user = None
        if _response is not None and 'users' in _response.keys():
            if len(_response['users']) > 0:
                _db = firebase.database()
                firebase.storage()
                _user = _response['users'][0]
                if _db is not None:
                    additional_info = _db.child('users').child(_user['localId']).get().val()
                    if additional_info is None:
                        additional_info = {}
                else:
                    additional_info = {}
                return {**_user, **additional_info}
    except:
        pass
    return None


@app.route('/')
def index():
    _idToken = request.cookies.get('idToken')
    _refreshToken = request.cookies.get('refreshToken')

    _message = None
    _user = None
    _response = None

    if _idToken is not None:
        _user = get_user(_idToken)

    _response = make_response(render_template(
        'index.html',
        title='Home',
        user=_user,
        message=_message,
        year=datetime.now().year,
    ))

    if _user is None:
        if _idToken is not None:
            _response.set_cookie('idToken', '', expires=-1)
        if _refreshToken is not None:
            _response.set_cookie('refreshToken', '', expires=-1)

    return _response


@app.route('/login', methods=['GET', 'POST'])
def login():
    _idToken = request.cookies.get('idToken')
    _refreshToken = request.cookies.get('refreshToken')

    _message = None
    _user = None
    _response = None

    if _idToken is not None:
        _user = get_user(_idToken)

    if _user is not None:
        if _user['emailVerified']:
            _response = make_response(redirect('/dashboard'))
        else:
            _response = make_response(redirect('/verify'))
    else:
        if request.method == 'POST':
            email = None
            if 'email' in request.form:
                email = request.form['email']
            password = None
            if 'password' in request.form:
                password = request.form['password']
            try:
                if email is not None and password is not None:
                    _user = auth.sign_in_with_email_and_password(email, password)

                    _response = make_response(redirect('/dashboard'))
                    _response.set_cookie('idToken', _user['idToken'], eval(_user['expiresIn']))
                    _response.set_cookie('refreshToken', _user['refreshToken'], eval(_user['expiresIn']))
                else:
                    _message = 'All fields required.'
                    _response = render_template(
                        'login.html',
                        title='Login',
                        message=_message,
                        year=datetime.now().year,
                    )
            except:
                _message = 'Authentication failed.'
                _response = render_template(
                    'login.html',
                    title='Login',
                    message=_message,
                    year=datetime.now().year,
                )
                if _idToken is not None:
                    _response.set_cookie('idToken', '', expires=-1)
                if _refreshToken is not None:
                    _response.set_cookie('refreshToken', '', expires=-1)

        else:
            _response = render_template(
                'login.html',
                title='Login',
                message=_message,
                year=datetime.now().year,
            )
            if _idToken is not None:
                _response.set_cookie('idToken', '', expires=-1)
            if _refreshToken is not None:
                _response.set_cookie('refreshToken', '', expires=-1)

    return _response


@app.route('/logout')
def logout():
    _idToken = request.cookies.get('idToken')
    _refreshToken = request.cookies.get('refreshToken')
    _response = make_response(redirect('/login'))
    if _idToken is not None:
        _response.set_cookie('idToken', '', expires=-1)
    if _refreshToken is not None:
        _response.set_cookie('refreshToken', '', expires=-1)
    return _response


@app.route('/register', methods=['GET', 'POST'])
def register():
    _idToken = request.cookies.get('idToken')
    _refreshToken = request.cookies.get('refreshToken')

    _message = None
    _user = None
    _response = None

    if _idToken is not None:
        _user = get_user(_idToken)

    if _user is not None:
        _response = make_response(redirect('/dashboard'))
    else:
        if request.method == 'POST':
            email = None
            if 'email' in request.form:
                email = request.form['email'] if (request.form['email'] != '') else None

            password = None
            if 'password' in request.form:
                password = request.form['password'] if (request.form['password'] != '') else None

            confirm_password = None
            if 'confirmPassword' in request.form:
                confirm_password = request.form['confirmPassword'] if (request.form['confirmPassword'] != '') else None

            privacy_policy = False
            if 'privacyPolicy' in request.form and request.form['privacyPolicy'] == 'on':
                privacy_policy = True

            try:
                if email is not None and password is not None and confirm_password is not None:
                    if password is not None and password == confirm_password:
                        if privacy_policy:
                            _user = auth.create_user_with_email_and_password(email, password)
                            _response = make_response(redirect('/dashboard'))
                            _response.set_cookie('idToken', _user['idToken'], eval(_user['expiresIn']))
                            _response.set_cookie('refreshToken', _user['refreshToken'], eval(_user['expiresIn']))
                        else:
                            _message = 'Please accept privacy policy.'
                            _response = render_template(
                                'register.html',
                                title='Register',
                                message=_message,
                                year=datetime.now().year,
                            )
                    else:
                        _message = 'Confirm password didn\'t match.'
                        _response = render_template(
                            'register.html',
                            title='Register',
                            message=_message,
                            year=datetime.now().year,
                        )
                else:
                    _message = 'All fields required.'
                    _response = render_template(
                        'register.html',
                        title='Register',
                        message=_message,
                        year=datetime.now().year,
                    )
            except:
                _message = 'Registration failed'
                _response = render_template(
                    'register.html',
                    title='Register',
                    message=_message,
                    year=datetime.now().year,
                )
                if _idToken is not None:
                    _response.set_cookie('idToken', '', expires=-1)
                if _refreshToken is not None:
                    _response.set_cookie('refreshToken', '', expires=-1)

        else:
            _response = render_template(
                'register.html',
                title='Register',
                message=_message,
                year=datetime.now().year,
            )
            if _idToken is not None:
                _response.set_cookie('idToken', '', expires=-1)
            if _refreshToken is not None:
                _response.set_cookie('refreshToken', '', expires=-1)

    return _response


@app.route('/dashboard')
def dashboard():
    _idToken = request.cookies.get('idToken')
    _refreshToken = request.cookies.get('refreshToken')

    _message = None
    _user = None
    _response = None

    if _idToken is not None:
        _user = get_user(_idToken)

    if _user is not None:
        if _user['emailVerified']:
            _response = make_response(render_template(
                'dashboard.html',
                title='Dashboard',
                user=_user,
                year=datetime.now().year,
                message=_message
            ))
        else:
            _response = make_response(redirect('/verify'))
    else:
        _response = make_response(redirect('/login'))
        if _idToken is not None:
            _response.set_cookie('idToken', '', expires=-1)
        if _refreshToken is not None:
            _response.set_cookie('refreshToken', '', expires=-1)
    return _response


@app.route('/verify')
def verify():
    _idToken = request.cookies.get('idToken')
    _refreshToken = request.cookies.get('refreshToken')

    _message = None
    _user = None
    _response = None

    if _idToken is not None:
        _user = get_user(_idToken)

    if _user is not None:
        if _user['emailVerified']:
            _response = make_response(redirect('/dashboard'))
        else:
            try:
                auth.send_email_verification(_idToken)
                _message = 'A new verification mail sent on ' + _user['email']
            except:
                _message = 'A verification mail already sent on ' + _user['email']
            _response = make_response(render_template(
                'verify.html',
                title='Verify',
                user=_user,
                year=datetime.now().year,
                message=_message
            ))
    else:
        _response = make_response(redirect('/login'))
        if _idToken is not None:
            _response.set_cookie('idToken', '', expires=-1)
        if _refreshToken is not None:
            _response.set_cookie('refreshToken', '', expires=-1)
    return _response
