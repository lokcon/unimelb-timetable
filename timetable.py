"""
The scraper for the Uniemlb timetable
"""

CLASS_ROW_HEADERS = ["class", "description", "day", "start", "finish",
    "duration", "weeks", "location", "date", "start_date"]
CLASS_CODES = ["subject", "campus", "num", "semester", "class_type",
    "class_repeat"]
TIMETALBE_LINK = ("https://sws.unimelb.edu.au/%(year)s/Reports/List.aspx"
    "?objects=%(subject)s&weeks=1-52&days=1-7&periods=1-56"
    "&template=module_by_group_list"
    )

class Timetable:
    """A scraper for the timetable of a subject"""

    @staticmethod
    def __timetable_link(year, subject):
        return TIMETALBE_LINK % {"year": year, "subject": subject}


    @staticmethod
    def __read_subject(year, semester, subject):
        import requests
        from bs4 import BeautifulSoup

        url = Timetable.__timetable_link(year, subject)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        classes = []
        for table in soup.find_all("table", class_ = "cyon_table"):
            for row in table.find("tbody").find_all("tr"):
                cells = row.find_all("td")

                # Assemble the cells in the row
                this_row = [cell.string for cell in cells]
                class_ = dict(zip(CLASS_ROW_HEADERS, this_row))

                # process the cells
                class_["day"] = Weekday.from_string(class_["day"]).to_num()
                class_["start"] = Time.from_string(class_["start"]).to_tuple()
                class_["finish"] = Time.from_string(class_["finish"]).to_tuple()
                class_["class"] = dict(zip(CLASS_CODES,
                    class_["class"].split("/")))

                # filter classes by semester
                if semester.upper() == class_["class"]["semester"].upper():
                    classes.append(class_)

        return ((year, semester.upper(), subject.upper()), classes)


    @staticmethod
    def get(year, semester, subject):
        return Timetable.__read_subject(year, semester, subject)


class Time:
    """Illustrate a time in a day, in the format HH:MM"""

    def __init__(self, hour, minutes):
        if hour not in range(24) or minutes not in range(60):
            raise Exception("Invalid hour/minutes supplied")

        self.hour = hour
        self.minutes = minutes

    @staticmethod
    def from_string(time_string):
        try:
            hour, minutes = map(int, time_string.split(":"))
        except Exception:
            raise Exception("Error while parsing time from string \"%s\""
                % time_string)

        return Time(hour, minutes)


    def to_tuple(self):
        return (self.hour, self.minutes)


class Weekday:
    WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday",
        "saturday", "sunday"]


    def __init__(self, day_num):
        if day_num not in range(7):
            raise Exception("Invalid day number supplied")

        self.day_num = day_num


    @staticmethod
    def from_string(day_string):
        if day_string.lower() not in Weekday.WEEKDAYS:
            raise Exception("Error while parsing weekday from string \"%s\""
                % day_string)

        return Weekday(Weekday.WEEKDAYS.index(day_string.lower()))


    def to_num(self):
        return self.day_num
