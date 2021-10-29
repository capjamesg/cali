from flask import Flask, request, jsonify, render_template
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

if __name__ == "__main__":
	app.run()