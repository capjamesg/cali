from config import MICROPUB_URL, ACCESS_TOKEN, WIKI_API_KEY, MICROSUB_URL, MICROSUB_API_TOKEN
from bs4 import BeautifulSoup
import datetime
import requests
import random

def send_to_wiki(message):
	# send definition to wiki
	headers = {
		"Authorization": WIKI_API_KEY
	}

	data = {
		"description": message
	}

	requests.post("https://wiki.jamesg.blog/ping", headers=headers, data=data)

command_reference = """
Here are some of the main commands you can use:

ping - ping the bot
search - run a search on IndieWeb Search
what's X - find a a result from IndieWeb Search that answers your question (if available)
Wiki << https://jamesg.blog - adds the specified URL to the jamesg.blog "Wiki" wiki page
searchj - search jamesg.blog
coffee - receive a coffee response
X or Y - get a random response from the list of responses
tell me a joke - see an xkcd comic
flip a coin - heads or tails?
time - get the time
!christmas / !halloween - get days until christmas or halloween
post / like / bookmark / repost / poke / reply / react/ yo X - post something on jamesg.blog
X is Y - define X as Y on the jamesg.blog wiki
cali++ - add 1 karma to cali
cali-- - subtract 1 karma from cali
cali karma - see "cali" karma
how are you - find out how cali is doing
"""

def process_command(message, day_karma):
	# convert to lowercase so responses are parsed consistently
	original_message = message
	message = message.lower()

	if message.startswith("ping"):
		return "pong"
	elif (message.startswith("help") or message.startswith("man")) and len(message.split(" ")) < 2:
		return command_reference
	elif message.startswith("random"):
		first_number = int(message.split(" ")[1])
		second_number = int(message.split(" ")[2])

		if first_number.isnumeric() and second_number.isnumeric():
			return random.randint(first_number, second_number)
	elif message.endswith("karma"):
		target = message.split(" ")[0]

		karma = day_karma.get(target, 0)

		return "{} has {} karma".format(target, karma)
	elif "++" in message or "--" in message:
		get_plus_plus_target = message.split(" ")

		if "++" in message:
			target = [x for x in get_plus_plus_target if x.endswith("++")]
		else:
			target = [x for x in get_plus_plus_target if x.endswith("--")]

		original_target = target[0]

		if target[0]:
			target[0] = target[0].replace("++", "").replace("--", "").strip()
		else:
			return "please specify a target to ++ or --"

		todays_date = datetime.datetime.now().strftime("%Y-%m-%d")

		if target:
			if day_karma.get(target[0]):
				if "++" in original_target:
					day_karma[target[0]]["karma"] += 1
				else:
					day_karma[target[0]]["karma"] -= 1
			else:
				day_karma[target[0]] = {
					"date": todays_date,
					"karma": 1
				}

			return "{} has {} karma".format(target[0], day_karma[target[0]]["karma"])

	elif message.startswith("search "):
		return "https://indieweb-search.jamesg.blog/results?query=" + message.replace("search ", "").replace(" ", "%20")
	elif message.startswith("what's "):
		r = requests.get("https://indieweb-search.jamesg.blog/results?query={}&serp_as_json=direct".format(message.replace("what is ", "").replace(" ", "%20")))

		if r.status_code == 200:
			if r.json().get("message"):
				return r.json().get("message")
			else:
				search_result_description = BeautifulSoup(r.json()["text"], "lxml")
				# remove all headers and bold tags
				for header in search_result_description.find_all(["h1", "h2", "h3", "b"]):
					header.decompose()

				message = search_result_description.get_text() + " ({})".format(r.json()["featured_serp"]["breadcrumb"])
				return message
		else:
			return "error"
	elif "is" in message.split(" "):
		send_to_wiki(original_message)
	elif " << " in message:
		send_to_wiki(original_message)
	elif " < " in message:
		send_to_wiki(original_message)
	elif message.startswith("searchj"):
		r = requests.get('https://indieweb-search.jamesg.blog/results?query=site:"jamesg.blog"%20{}&serp_as_json=results_page'.format(message))

		if r.status_code == 200:
			if r.json()[0]:
				return r.json()[0]["title"] + " ({}) " + r.json()[0]["url"]
		else:
			return "error"
	elif message.startswith("boo"):
		return "eek :)"
	elif message == "coffee":
		random_chance = random.randint(1, 2)
		if random_chance == 1:
			return "coffee is tasty"
		else:
			return "coffee coffee coffee"
	elif message.startswith("tell me a joke"):
		return "my friend xkcd is going to take over on this one: https://c.xkcd.com/random/comic/"
	elif message.startswith("morning") or message.startswith("good morning") or message.startswith("hello") \
		 or message.startswith("hi") or message.startswith("what's up") or message.startswith("howdy") \
		 or message.startswith("hello") or message.startswith("sup") or message.startswith("yo"):
		return "morning!"
	elif message.startswith("cali"):
		return "yep! i'm here!"
	elif message.startswith("flip a coin"):
		result = random.randint(0, 1)

		if result == 0:
			return "heads"
		else:
			return "tails"
	elif message.startswith("make a sandwich"):
		return "nope"
	elif message.startswith("sudo make a sandwich"):
		return "here you go *hands over a sandwich*"
	elif " or " in message:
		choose = random.choice(message.split(" or "))
		preamble = ["definitely ", "for sure ", ""]
		return "{}{}".format(random.choice(preamble), choose)
	elif message.startswith("time"):
		return datetime.datetime.now().strftime("%I:%M %p")
	elif message.startswith("!christmas"):
		christmas_date = datetime.datetime(year=datetime.datetime.now().year, month=12, day=25)

		delta = christmas_date - datetime.datetime.now()

		return "christmas is in {} days".format(delta.days)
	elif message.startswith("!halloween"):
		halloween_date = datetime.datetime(year=datetime.datetime.now().year, month=10, day=31)

		delta = halloween_date - datetime.datetime.now()

		return "halloween is in {} days".format(delta.days)
	elif "make" and "coffee" in message:
		coffee_origins = ["ethiopia", "guatemala", "columbia", "kenya", "china"]
		brewing_devices = ["an aeropress", "the chemex", "an espresso machine", "a kalita wave", "a v60"]
		random_number = random.randint(0, 10)
		if random_number == 5:
			return "you have had too much coffee today!"
		elif random_number == 6:
			return "*hands over a cup of tea*"
		else:
			return "*brews a single origin coffee from {} using {}*".format(random.choice(coffee_origins), random.choice(brewing_devices))
	elif message.startswith("how are you"):
		responses = ["i'm good, thanks", "i'm doing well, thanks", "i'm doing great!", "i'm doing really well!"]
		weather = ["it's raining here in internet land", "it's sunny here in internet land"]

		# at random, send a weather message
		if random.randint(1, 10) == 1:
			return message + " " + random.choice(weather)

		return random.choice(responses)

	elif message.startswith("subscribe "):
		if len(message.replace("subscribe ", "").split(" ")) >= 2:
			channel = message.replace("subscribe ", "").split(" ")[0]
		else:
			channel = "indiewebnaw"

		url = message.split(" ")[-1]

		data = {
			"action": "follow",
			"channel": channel,
			"url": url
		}

		headers = {
			"Authorization": "Bearer {}".format(MICROSUB_API_TOKEN)
		}

		r = requests.post(MICROSUB_URL, data=data, headers=headers)

		if r.status_code == 200:
			return "subscribed to {}".format(url)
		else:
			return "there was an error subscribing to {}".format(url)

	elif message.startswith("post"):
		message_to_send_to_client = make_micropub_request("h-entry", message, "Note")
		return message_to_send_to_client
	elif message.startswith("like"):
		message_to_send_to_client = make_micropub_request("like-of", message, "Like")
		return message_to_send_to_client
	elif message.startswith("bookmark"):
		message_to_send_to_client = make_micropub_request("u-like-of", message, "Like")
		return message_to_send_to_client
	elif message.startswith("repost"):
		message_to_send_to_client = make_micropub_request("u-repost-of", message, "Repost")
		return message_to_send_to_client
	elif message.startswith("poke"):
		message_to_send_to_client = make_micropub_request("u-poke-of", message, "Poke")
		return message_to_send_to_client
	elif message.startswith("reply"):
		message_to_send_to_client = make_micropub_request("in-reply-to", message, "Reply")
		return message_to_send_to_client
	elif message.startswith("react"):
		message_to_send_to_client = make_micropub_request("in-reply-to", message, "Reply")
		return message_to_send_to_client
	elif message.startswith("yo"):
		message_to_send_to_client = make_micropub_request("note", message, "Note")
		return message_to_send_to_client
	elif message.startswith("yay") or message.startswith("amazing") or message.startswith("cool") or message.startswith("terrific"):
		return "yay!"
	else:
		return ""

def make_micropub_request(post_type, message, category):
	if post_type == "in-reply-to":
		# second space denotes end of reply
		if len(message.split(" ")) > 2:
			contents_of_post = " ".join(message.split(" ")[2:])
		else:
			return "please specify a url to reply to and something to include in your reply :)"
	else:
		contents_of_post = " ".join(message.split(" ")[1:])

	if message.startswith("yo "):
		contents_of_post = "<a class='u-yo-of yo-of' href='" + " ".join(message.split(" ")[2:]) + "'>" + "Yo!" + "</a>"

	headers = {
		"Authorization": ACCESS_TOKEN,
		"Content-Type": "application/json",
	}

	request_to_make = {
		"type": ["h-entry"],
	}

	if post_type == "note":
		request_to_make["properties"] = {
			"content": [contents_of_post],
			"category": ["Note"],
			"is_hidden": ["no"]
		}
	else:
		request_to_make[post_type] = message.split(" ")[1]
		request_to_make["properties"] = {
			"content": [contents_of_post],
			"category": [category],
			"is_hidden": ["no"]
		}

	r = requests.post(MICROPUB_URL, json=request_to_make, headers=headers)

	if r.status_code == 200 or r.status_code == 201 or r.status_code == 202:
		location = r.headers["Location"]
		return "your post was successfully sent to " + location
	else:
		return "there was an error sending your post"