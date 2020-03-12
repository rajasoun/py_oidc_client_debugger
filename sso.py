import os
import flask
from flask import render_template, request
from requests_oauthlib import OAuth2Session

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
SCOPES = os.environ.get('SCOPES')

AUTHORIZATION_BASE_URL = os.environ.get("AUTHORIZATION_BASE_URL")
TOKEN_URL = os.environ.get("TOKEN_URL")
USERINFO_URL = os.environ.get('USERINFO_URL')
REDIRECT_URI = os.environ.get('REDIRECT_URI')

# This allows us to use a plain HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = flask.Flask(__name__)


###########
#  ERRORS #
###########

@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    print(e)
    return render_template('500.html'), 500
    
###########
#  ROUTES #
###########

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    simplelogin = OAuth2Session(
        CLIENT_ID, scope=SCOPES,redirect_uri=REDIRECT_URI
    )
    authorization_url, _ = simplelogin.authorization_url(AUTHORIZATION_BASE_URL)
    print("Redirect URL -------->" + authorization_url)
    return flask.redirect(authorization_url)


@app.route("/callback")
def callback():
    simplelogin = OAuth2Session(
        CLIENT_ID, redirect_uri=REDIRECT_URI
    )
    simplelogin.fetch_token(
        TOKEN_URL, 
        include_client_id=True,
        client_secret=CLIENT_SECRET, 
        authorization_response=flask.request.url
    )
    user_info = simplelogin.get(USERINFO_URL).json()
    return render_template('user_info.html',
                           email=user_info["email"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.secret_key = os.urandom(24)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(host='0.0.0.0', port=port, debug=True, ssl_context='adhoc') # For testing locally and SSL is needed
    app.run(host='0.0.0.0', port=port, debug=True)