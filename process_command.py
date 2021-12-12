from config import WIKI_API_KEY, MICROSUB_URL, MICROSUB_API_TOKEN, WEBMENTION_WEBHOOK_KEY, WOLFRAM_API_ID, GIPHY_API_KEY, DICTIONARY_API_KEY
from bs4 import BeautifulSoup
import command_references
import datetime
import micropub
import requests
import psutil
import random
import lists
import json
import csv

def send_to_wiki(message):
    # send definition to wiki
    headers = {
        "Authorization": WIKI_API_KEY
    }

    data = {
        "description": message
    }

    requests.post("https://wiki.jamesg.blog/ping", headers=headers, data=data)

def get_wolfram_response(message):
    cleaned_message = message.replace("!wolfram", "").strip()

    if cleaned_message == "":
        return "Please specify a query."

    request_url = "http://api.wolframalpha.com/v2/query?appid={}&input={}&output=json".format(WOLFRAM_API_ID, cleaned_message)

    r = requests.get(request_url)

    if r.status_code != 200:
        return "Something went wrong."

    response_data = r.json()

    if response_data["queryresult"]["success"] == "false":
        return "No results found."

    result = [pod for pod in response_data["queryresult"].get("pods", []) if pod.get("id") == "Result"]

    if len(result) == 0:
        return "No results found."

    final_result = result[0]["subpods"][0]["plaintext"]

    return final_result

def karma_operations(message, day_karma):
    if message.endswith("karma"):
        target = message.split(" ")[0]

        karma = day_karma.get(target, 0)

        return "{} has {} karma".format(target, karma.get("karma", 0))
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
        else:
            return None
    else:
        return None

def check_for_map_commands(message, shortcuts):
    if message.startswith("!map create"):
        shortcut_to_create = message.split("=")[0].replace("!map create ", "").strip()

        shortcuts[shortcut_to_create] = message.split("=")[1].strip()

        with open("shortcuts.json", "w") as f:
            json.dump(shortcuts, f)
        
        return "{} now maps to {}".format(shortcut_to_create, message.split("=")[1].strip())
    elif message.startswith("!map delete"):
        shortcut_to_delete = message.replace("!map delete ", "").split(" ")[1].strip()

        if shortcuts.get(shortcut_to_delete):
            del shortcuts[shortcut_to_delete]

            with open("shortcuts.json", "w") as f:
                json.dump(shortcuts, f)

            return "{} has been deleted".format(shortcut_to_delete)
        else:
            return "Shortcut {} not found".format(shortcut_to_delete)
    elif message.startswith("!map list"):
        shortcuts = ["{}: {}".format(key, value) for key, value in shortcuts.items()]

        return "Shortcuts: \n\n" + "\n".join(shortcuts)

    return None

def process_command(message, day_karma):
    # convert to lowercase so responses are parsed consistently
    original_message = message
    message = message.lower()

    # one word shortcuts are allowed
    # mapping happens before a command is evaluated

    with open("shortcuts.json", "r") as f:
        shortcuts = json.load(f)

    if shortcuts.get(message.split(" ")[0]):
        message = shortcuts[message.split(" ")[0]] + " ".join(message.split(" ")[1:]).strip()

    if message.startswith("ping"):
        return "pong"
    elif message.startswith("!post"):
        # make a post request
        request_info = message.replace("!post ", "").strip()

        if request_info == "":
            return "please specify a URL."

        url = request_info.split(" ")[0]

        if len(request_info.split(" ")) > 1:
            try:
                data = json.loads(" ".join(request_info.split(" ")[1:]))
            except:
                return "json data invalid"
        else:
            data = {}

        try:
            r = requests.post(url, json=data)
            return r.text
        except:
            return "something went wrong during the http request"
    elif message.startswith("!get"):
        # make a get request
        request_info = message.replace("!get ", "").strip()

        if request_info == "":
            return "please specify a URL."

        url = request_info.split(" ")[0]

        try:
            r = requests.get(url)
            return r.text
        except:
            return "something went wrong during the http request"
    elif message.startswith("!meme"):
        search_term = message.replace("!meme ", "").strip()

        if search_term != "":
            api_url = "https://api.giphy.com/v1/gifs/search?api_key={}&q={}&limit=1".format(GIPHY_API_KEY, search_term)
        else:
            api_url = "https://api.giphy.com/v1/gifs/random?api_key={}&limit=1".format(GIPHY_API_KEY)

        r = requests.get(api_url)

        if r.status_code == 200:
            data = r.json()

            if data["data"]:
                return data["data"][0]["embed_url"]
            else:
                return "no results found"

        return "there was an error getting a gif"
    elif message.startswith("!ping"):
        if len(message.split(" ")) < 1:
            return "please specify a url to ping."
        try:
            r = requests.get(message.split(" ")[-1], timeout=5)
        except:
            return "something went wrong during the http request"

        if r.status_code == 200:
            return "{} sent a {} status code".format(message.split(" ")[1], r.status_code)
    elif message.startswith("!define"):
        if len(message.split(" ")) < 1:
            return "please specify a word to define."
        
        word_to_define = message.replace("!define ", "").strip()

        dictionary_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}".format(word_to_define, DICTIONARY_API_KEY)

        r = requests.get(dictionary_url)

        if r.status_code == 200:
            data = r.json()

            for entry in data:
                return entry["shortdef"]

            return "no results found"

        return "there was an error getting the definition"
    elif message.startswith("man list"):
        return command_references.list_command_reference
    elif message.startswith("!qr"):
        return "https://chart.googleapis.com/chart?cht=qr&chs=512&&chl=" + message.replace("!qr", "").strip()
    elif message.startswith("!list create"):
        message = message.replace("!list create", "").strip()

        with open("lists.json", "r") as f:
            lists = json.load(f)

        lists[message] = []

        with open("lists.json", "w") as f:
            json.dump(lists, f)

        return "{} list has been created".format(message)
    elif message.startswith("!echo "):
        return message.replace("!echo ", "").strip()
    elif "haha" in message or "lol" in message or "rofl" in message or "hehe" in message:
        # 1 in 5 chance of sending a laughter response
        chance = random.randint(1, 5)

        if chance == 1:
            return "haha"
        else:
            return ""
    elif message.startswith("!stats"):
        sys_stats = """Cali system stats:

CPU usage: {}%
Memory usage: {}%
Disk usage: {}%
CPU count: {}
        """.format(
            psutil.cpu_percent(),
            psutil.virtual_memory().percent,
            psutil.disk_usage("/").percent,
            psutil.cpu_count()
        )

        return sys_stats
    elif (message.startswith("help") or message.startswith("man")) and len(message.split(" ")) < 2:
        return command_references.command_reference
    elif message.startswith("!wolfram"):
        response = get_wolfram_response(message)

        return response
    elif message.startswith("!status check"):
        with open("lists.json", "r") as f:
            lists = json.load(f)

        websites = lists.get("websites", [])

        messages = []

        for site in websites:
            site = site.strip()

            try:
                r = requests.get(site, timeout=5)
                message = "{} is {}".format(site, r.status_code)
                messages.append(message)
            except TimeoutError:
                message = "{} timed out".format(site)
                messages.append(message)
            except Exception as e:
                print(e)
                message = "{} is down (reason unknown)".format(site)
                messages.append(message)

        return "\n".join(messages)
    elif message.startswith("!status add"):
        with open("status.txt", "a") as status_file:
            status_file.write(message.split(" ")[2] + "\n")
        return "added {} to the status list".format(message.split(" ")[2])
    elif message.startswith("!status remove"):
        with open("status.txt", "r") as status_file:
            websites = status_file.readlines()

            for site in websites:
                site = site.strip().replace("\n", "")
                if site == message.split(" ")[2]:
                    websites.remove(site)

        with open("status.txt", "w") as status_file:
            for site in websites:
                status_file.write(site + "\n")

        return "removed {} from the status list".format(message.split(" ")[2])
    elif message.startswith("random"):
        first_number = int(message.split(" ")[1])
        second_number = int(message.split(" ")[2])

        if first_number.isnumeric() and second_number.isnumeric():
            return random.randint(first_number, second_number)

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
    elif message.startswith("!send"):
        r = requests.get("https://webmention.jamesg.blog/webhook?key={}&url={}".format(WEBMENTION_WEBHOOK_KEY, message.split(" ")[1]))

        return r.json()["message"]
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
    elif message.startswith("!remind all"):
        with open("reminders.csv", "r") as f:
            reader = csv.reader(f)
            reminders = list(reader)

        message = "reminders:\n" + "\n".join(reminders)

        return message
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

        # if friday, have a chance of sending a TGIF message
        if datetime.datetime.now().weekday() == 4 and random.randint(1, 2) == 1:
            return "tgif, am i right?"

        # at random, send a weather message
        if random.randint(1, 10) == 1:
            return message + " " + random.choice(weather)

        return random.choice(responses)

    elif message.startswith("!subscribe "):
        if len(message.replace("!subscribe ", "").split(" ")) >= 2:
            channel = message.replace("!subscribe ", "").split(" ")[0]
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
    elif message.startswith("!unsubscribe "):
        if len(message.replace("!subscribe ", "").split(" ")) >= 2:
            channel = message.replace("!subscribe ", "").split(" ")[0]
        else:
            channel = "indiewebnaw"

        url = message.split(" ")[-1]

        data = {
            "action": "unfollow",
            "channel": channel,
            "url": url
        }

        headers = {
            "Authorization": "Bearer {}".format(MICROSUB_API_TOKEN)
        }

        r = requests.post(MICROSUB_URL, data=data, headers=headers)

        if r.status_code == 200:
            return "unsubscribed from {}".format(url)
        else:
            return "there was an error unsubscribing from {}".format(url)
    elif message.startswith("yay") or message.startswith("amazing") or message.startswith("cool") or message.startswith("terrific"):
        return "yay!"

    response = None

    while response is None:
        response = check_for_map_commands(message, shortcuts)
        response = karma_operations(message, day_karma)
        response = lists.check_for_list_command(message)
        response = micropub.check_for_micropub_command(message)

        response = ""

    if message.startswith("!"):
        return "command not found"
    else:
        return ""