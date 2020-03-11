import os
from pprint import pformat
from time import time

from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import requests
from requests_oauthlib import OAuth2Session

import logging
import sys

log = logging.getLogger('sso')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get('REDIRECT_URI')

# OAuth endpoints 
authorization_base_url = os.environ.get("AUTHORIZATION_BASE_URL")
token_url = os.environ.get("TOKEN_URL")
user_info_url= os.environ.get("USERINFO_URL")
refresh_url = os.environ.get("TOKEN_URL") # True for Google but not all providers.
scope = os.environ.get('SCOPES')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/login")
def login():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (IDP)
    using an URL with a few key OAuth parameters.
    """
    sso_login = OAuth2Session(client_id,scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = sso_login.authorization_url(authorization_base_url,
        # offline for refresh token
        # force to always make user click authorize
        access_type="offline")

    # State is used to prevent CSRF, keep this for later.
    session["oauth_state"] = state
    return redirect(authorization_url)

# Step 2: User authorization, this happens on the provider 
# Browser gets redirected to redirect_url on successfull authorization

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    sso_login = OAuth2Session(client_id, redirect_uri=redirect_uri,
                           state=session["oauth_state"])
    token = sso_login.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # We use the session as a simple DB for this example.
    session["oauth_token"] = token

    return redirect(url_for('.menu'))


@app.route("/menu", methods=["GET"])
def menu():
    """"""
    return """
    <h1>Congratulations, you have obtained an OAuth 2 token!</h1>
    <h2>What would you like to do next?</h2>
    <ul>
        <li><a href="/profile"> Get account profile</a></li>
        <li><a href="/automatic_refresh"> Implicitly refresh the token</a></li>
        <li><a href="/manual_refresh"> Explicitly refresh the token</a></li>
        <li><a href="/validate"> Validate the token</a></li>
    </ul>

    <pre>
    %s
    </pre>
    """ % pformat(session['oauth_token'], indent=4)


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    sso_login = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(sso_login.get(user_info_url).json())


@app.route("/automatic_refresh", methods=["GET"])
def automatic_refresh():
    """Refreshing an OAuth 2 token using a refresh token.
    """
    token = session['oauth_token']

    # We force an expiration by setting expired at in the past.
    # This will trigger an automatic refresh next time we interact with IDP
    token['expires_at'] = time() - 10

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    def token_updater(token):
        session['oauth_token'] = token

    sso_login = OAuth2Session(client_id,
                           token=token,
                           auto_refresh_kwargs=extra,
                           auto_refresh_url=refresh_url,
                           token_updater=token_updater)

    # Trigger the automatic refresh
    jsonify(sso_login.get(user_info_url).json())
    return jsonify(session['oauth_token'])


@app.route("/manual_refresh", methods=["GET"])
def manual_refresh():
    """Refreshing an OAuth 2 token using a refresh token.
    """
    token = session['oauth_token']

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    sso_login = OAuth2Session(client_id, token=token)
    session['oauth_token'] = sso_login.refresh_token(refresh_url, **extra)
    return jsonify(session['oauth_token'])

@app.route("/validate", methods=["GET"])
def validate():
    """Validate a token with the OAuth provider.
    """
    token = session['oauth_token']
    validate_url = (user_info_url+'?access_token=%s' % token['access_token'])

    # No OAuth2Session is needed, just a plain GET request
    return jsonify(requests.get(validate_url).json())

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    port = int(os.environ.get("PORT", 3000))
    app.secret_key = os.urandom(24)
    # app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(host='0.0.0.0', port=port, debug=True, ssl_context='adhoc') # For testing locally and SSL is needed
    app.run(host='0.0.0.0', port=port, debug=True)