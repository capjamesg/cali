from flask import Flask, render_template, session
from flask_session import Session
import os

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.urandom(32)

    app.config.from_object(__name__)

    sess = Session()
    sess.init_app(app)

    from .auth.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from .web_server import app as web_server_blueprint

    app.register_blueprint(web_server_blueprint)

    @app.errorhandler(400)
    def request_error(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="400", title="Bad request error", user=user, me=me), 400

    @app.errorhandler(405)
    def method_not_allowed(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="405", title="Method not allowed error", user=user, me=me), 405

    @app.errorhandler(404)
    def page_not_found(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="404", title="Page not found error", user=user, me=me), 404

    @app.errorhandler(500)
    def server_error(e):
        if session.get("access_token"):
            user = session["access_token"]
            me = session["me"]
        else:
            user = None
            me = None
        return render_template("error.html", error_type="500", title="Server error", user=user, me=me), 500

    return app

create_app()