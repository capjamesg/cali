from flask import Blueprint, request, jsonify, render_template, send_from_directory
from .config import API_KEY, DISCORD_POST_WEBHOOK
import requests

app = Blueprint("web_server", __name__, template_folder="templates")

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():
	# possible response values:
	# error = "error"
	# success = "message"

	if not request.headers.get("authorization") or request.headers.get("authorization").replace("Bearer", "").strip() != API_KEY:
		return jsonify({"error": "not_authorized"}), 403

	if not request.form.get("message"):
		return jsonify({"error": "invalid_request"}), 400

	data = {
		"username": "calibot",
		"content": request.form["message"]
	}

	requests.post(DISCORD_POST_WEBHOOK, data=data)

	return jsonify({"message": "message_sent"}), 200

# disabled as Cali is used as a Discord bot most of the time
# @app.route("/chat")
# def chat_interface():
# 	if not session.get("me"):
# 		return jsonify({"error": "not_authorized"}), 403

# 	return render_template("chat.html")

@app.errorhandler(404)
def page_not_found(e):
	return render_template("error.html", error_type="404", title="Page not found error"), 404

@app.errorhandler(500)
def server_error(e):
	return render_template("error.html", error_type="500", title="Server error"), 500

@app.route("/styles.css")
def css_styles():
    return send_from_directory(app.static_folder, "styles.css")

@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico")