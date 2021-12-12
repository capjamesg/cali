import json

def check_for_list_command(message):
    if message.startswith("!list delete"):
        message = message.replace("!list delete", "").strip()

        with open("lists.json", "r") as lists_file:
            lists = json.load(lists_file)

        if lists.get(message.split(" ")[2]):
            del lists[message.split(" ")[2]]

        with open("lists.json", "w") as lists_file:
            json.dump(lists, lists_file)

        return "{} list has been deleted".format(message)
    elif message.startswith("!list pop"):
        message = message.replace("!list pop", "").strip()
        list_name = message.split(" ")[0]
        item_to_remove = " ".join(message.split(" ")[1:])

        with open("lists.json", "r") as lists_file:
            lists = json.load(lists_file)

        if lists.get(list_name):
            if len(lists[list_name]) > 0:
                with open("lists.json", "w") as lists_file:
                    lists[list_name].remove(item_to_remove)
                    json.dump(lists, lists_file)

                return "Removed {} from {} list".format(" ".join(item_to_remove), list_name)
            else:
                return "No items in {} list".format(list_name)
        else:
            return "{} does not exist".format(list_name)
    elif message.startswith("!list add"):
        list_name = message.split(" ")[2]
        item = " ".join(message.split(" ")[3:])

        all_items = item.split(",")

        with open("lists.json", "r") as lists_file:
            lists = json.load(lists_file)

        for i in all_items:
            if lists.get(list_name):
                lists[list_name].append(item)
            else:
                lists[list_name] = [item]

            with open("lists.json", "w") as lists_file:
                json.dump(lists, lists_file)
            
        return "{} has been added to {}".format(item, list_name)
    elif message.startswith("!list see"):
        list_name = message.split(" ")[2]

        with open("lists.json", "r") as lists_file:
            lists = json.load(lists_file)

        if lists.get(list_name):
            return "\n".join(lists[list_name])
        else:
            return "No list found by the name {}".format(list_name)
    elif message.startswith("!list random"):
        list_name = message.split(" ")[2]

        with open("lists.json", "r") as lists_file:
            lists = json.load(lists_file)

        random_item = random.choice(lists[list_name])

        return random_item
    elif message.startswith("!list all"):
        with open("lists.json", "r") as f:
            lists = json.load(f)

        list_names = ", ".join(lists.keys()).strip(", ")

        return "Lists: \n\n" + list_names
    else:
        return None