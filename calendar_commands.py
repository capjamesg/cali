import recurring_ical_events
import icalendar
import datetime
import requests

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)

def retrieve_calendar_information(url, header_message, file_to_open, cal_type, printer):
    today = datetime.datetime.today()

    r = requests.get(url)

    open(file_to_open, "wb").write(r.content)

    calendar = open(file_to_open, "rb")

    cal = icalendar.Calendar.from_ical(calendar.read())

    events = []

    start = today - datetime.timedelta(days=today.weekday())
    end = start + datetime.timedelta(days=6)

    this_week = daterange(start, end)

    this_week_list = [str(i) for i in this_week]

    # Use this to shw all recurring events
    recurring_events = recurring_ical_events.of(cal).between(start, end)

    for component in recurring_events:
        if component.name == "VEVENT":
            if cal_type == "Holidays" or cal_type == "Birthdays":
                if component.decoded("dtstart").strftime("%Y-%m-%d") in this_week_list:
                    events.append({
                        "summary": str(component.get("summary")),
                        "date_time": "{}".format(component.decoded("dtstart").strftime("%B %d, %Y"))
                    })
            else:
                if component.decoded("dtstart").strftime("%B %d, %Y") == today.strftime("%B %d, %Y"):
                    events.append({
                        "summary": str(component.get("summary")),
                        "date_time": "{}".format(component.decoded("dtstart").strftime("June 27, %Y (%H:%M %p)"))
                    })

    if len(events) > 0:
        # Reverse events so they appear in order from start of day / week to end of day / week
        events.reverse()
        
        return "\n".join(["{} - {}".format(e["summary"], e["date_time"]) for e in events])
    elif cal_type == "Events":
        return "You have no events today."
    elif cal_type == "Holidays":
        return "There are no holidays this week."
    elif cal_type == "Birthdays":
        return "There are no birthdays this week."

def holidays_this_week(printer):
    url = "https://calendar.google.com/calendar/ical/en.uk%23holiday%40group.v.calendar.google.com/public/basic.ics"

    retrieve_calendar_information(url, "Holidays this week", "holidays.ics", "Holidays", printer)

def birthdays(printer):
    url = "https://calendar.google.com/calendar/ical/"

    retrieve_calendar_information(url, "Birthdays this week", "birthdays.ics", "Birthdays", printer)

def mycal(printer):
    url = "https://calendar.google.com/calendar/ical/"

    retrieve_calendar_information(url, "Your schedule for the day", "mycalendar.ics", "Events", printer)