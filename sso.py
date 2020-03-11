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
#FUNCTIONS#
###########

def get_user_info(user_info):
    return f"""
    User information: <br>
    Name: {user_info["name"]} <br>
    Email: {user_info["email"]} <br>    
    Avatar <img src="{user_info.get('avatar_url')}"> <br>
    <a href="/">Home</a>
    """

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
    #  return """
    #  <a href="/login">Login</a>
    #  """
    return render_template('index.html')

@app.route("/login")
def login():
    simplelogin = OAuth2Session(
        CLIENT_ID, scope=SCOPES,redirect_uri=REDIRECT_URI
    )
    authorization_url, _ = simplelogin.authorization_url(AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/callback")
def callback():
    print("--------------------------------------" + str(request))
    simplelogin = OAuth2Session(client_id=CLIENT_ID)
    print("-----" + str(simplelogin))
    simplelogin.fetch_token(
        TOKEN_URL, 
        include_client_id=True,
        client_secret=CLIENT_SECRET, 
        authorization_response=flask.request.url
    )
    print("-----" + str(simplelogin))
    user_info = simplelogin.get(USERINFO_URL).json()
    print("-----" + str(user_info))
    return get_user_info(user_info)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.secret_key = os.urandom(24)
    # app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(host='0.0.0.0', port=port, debug=True, ssl_context='adhoc') # For testing locally and SSL is needed
    app.run(host='0.0.0.0', port=port, debug=True)