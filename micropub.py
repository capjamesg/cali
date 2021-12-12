from config import MICROPUB_URL, ACCESS_TOKEN
import requests

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

def check_for_micropub_command(message):
    if message.startswith("post"):
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
    else:
        return None