from flask import Flask, request, jsonify, render_template, send_from_directory
from config import API_KEY, DISCORD_POST_WEBHOOK
import requests

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():
	# possible response values:
	# error = "error"
	# success = "message"

	if not request.headers.get("authentication") or request.headers.get("authentication").replace("Bearer: ", "") != API_KEY:
		return jsonify({"error": "not_authorized"}), 403

	data = request.get_json()

	if not data.get("message"):
		return jsonify({"error": "invalid_request"}), 400

	data = {
		"username": "calibot",
		"content": data["message"]
	}

	requests.post(DISCORD_POST_WEBHOOK, data=data)

	return jsonify({"message": "message_sent"}), 200

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

if __name__ == "__main__":
	app.run()