from flask import request, redirect, session, Blueprint, flash, render_template
from config import ME, CALLBACK_URL, CLIENT_ID
import indieauth_helpers
import random
import string
import hashlib
import base64

auth = Blueprint('auth', __name__)

@auth.route("/callback")
def indieauth_callback_handler():
    code = request.args.get("code")
    state = request.args.get("state")

    # these are the scopes necessary for the application to run
    required_scopes = []

    message, response = indieauth_helpers.indieauth_callback(
        code,
        state,
        session.get("token_endpoint"),
        session["code_verifier"],
        session.get("state"),
        ME,
        CALLBACK_URL,
        CLIENT_ID,
        required_scopes
    )

    if message != None:
        flash(message)
        return redirect("/login")

    session.pop("code_verifier")

    session["me"] = response.get("me")
    session["access_token"] = response.get("access_token")
    session["scope"] = response.get("scope")

    return redirect("/")

@auth.route("/logout")
def logout():
    session.pop("me")
    session.pop("access_token")

    return redirect("/login")

@auth.route("/login", methods=["GET"])
def login():
    return render_template("auth.html", title="Cali Login")

@auth.route("/discover", methods=["POST"])
def discover_auth_endpoint():
    domain = request.form.get("me")

    headers_to_find = [
        "authorization_endpoint",
        "token_endpoint",
        "micropub",
        "microsub"
    ]

    headers = indieauth_helpers.discover_endpoints(domain, headers_to_find)

    if not headers.get("authorization_endpoint"):
        flash("A valid IndieAuth authorization endpoint could not be found on your website.")
        return redirect("/login")
    
    if not headers.get("token_endpoint"):
        flash("A valid IndieAuth token endpoint could not be found on your website.")
        return redirect("/login")

    authorization_endpoint = headers.get("authorization_endpoint")
    token_endpoint = headers.get("token_endpoint")

    session["micropub_url"] = headers.get("micropub")
    session["server_url"] = headers.get("microsub")

    random_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

    session["code_verifier"] = random_code
    session["authorization_endpoint"] = authorization_endpoint
    session["token_endpoint"] = token_endpoint

    sha256_code = hashlib.sha256(random_code.encode('utf-8')).hexdigest()

    code_challenge = base64.b64encode(sha256_code.encode('utf-8')).decode('utf-8')

    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    session["state"] = state

    return redirect(
        authorization_endpoint + "?client_id=" +
        CLIENT_ID + "&redirect_uri=" +
        CALLBACK_URL + "&scope=create profile&response_type=code&code_challenge=" +
        code_challenge + "&code_challenge_method=S256&state=" + state
    )