import datetime
import csv

import requests
from config import API_KEY

with open("reminders.csv", "r") as f:
    reader = csv.reader(f)
    reminders = list(reader)

current_minute = str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute).zfill(2)

for reminder in reminders:
    message = reminder[2]

    print(reminder[0])

    print(reminder[1])

    if reminder[0] == current_minute and reminder[1] == datetime.datetime.now().strftime("%d/%m/%Y"):
        headers = {
            "Authorization": "Bearer {}".format(API_KEY)
        }

        r = requests.post("https://cali.jamesg.blog/webhook", data={"message": "{}".format(message)}, headers=headers)

        print(r.status_code)