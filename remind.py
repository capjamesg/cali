import datetime
import csv
import re

def process_reminder(message):
    reminder_time = re.search(r"\d{1,2}:\d{2}", message)
    reminder_date = re.search(r"\d{1,2}/\d{1,2}/\d{4}", message)

    if not reminder_time:
        if message.split(" ")[-1] == "tomorrow":
            reminder_time = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            reminder_time = datetime.datetime.now()

    if not reminder_date:
        reminder_date = datetime.datetime.now().strftime("%d/%m/%Y")
    else:
        reminder_date = reminder_date.group()

    # get content after "to"

    message = "".join(message.split("to")[1:])

    message = "".join(message.split("at")[:-1]).strip()

    full_reminder = [reminder_time.group(), reminder_date, message]

    with open("reminders.csv", "a+") as f:
        writer = csv.writer(f)
        writer.writerow(full_reminder)

    reminder_message = "Your reminder '{}' at {} on {} has been set".format(message, reminder_time.group(), reminder_date)

    return reminder_message

process_reminder("remind me to buy milk at 12:00 tomorrow")