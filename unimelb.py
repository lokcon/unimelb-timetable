from pprint import pprint

'A scraper for the timetable of a subject'''
class Timetable:
    TIMETALBE_LINK = ("https://sws.unimelb.edu.au/%(year)s/Reports/List.aspx"
        "?objects=%(subject)s&weeks=1-52&days=1-7&periods=1-56"
        "&template=module_by_group_list"
        )
    CLASS_ROW_HEADERS = ["class", "description", "day", "start", "finish",
        "duration", "weeks", "location", "date", "start_date"]


    def __timetable_link(self, year, subject):
        return self.TIMETALBE_LINK % {"year": year, "subject": subject}


    def read_subject(self, year, subject):
        import requests
        from bs4 import BeautifulSoup

        url = self.__timetable_link(year, subject)
        page = requests.get(url)
        soup = BeautifulSoup(page.content)

        classes = {}
        for table in soup.find_all("table", class_ = "cyon_table"):
            for row in table.find("tbody").find_all("tr"):
                cells = row.find_all("td")

                # Assemble the cells in the row
                this_row = [cell.string for cell in cells]
                class_ = dict(zip(self.CLASS_ROW_HEADERS, this_row))

                # process the cells
                class_["day"] = Weekday.from_string(class_["day"])
                class_["start"] = Time.from_string(class_["start"])
                class_["finish"] = Time.from_string(class_["finish"])

                # group classes by study period
                (subject, campus, num, semester, class_name, class_repeat) = \
                    class_["class"].split("/")
                    
                if semester not in classes:
                    classes[semester] = [class_]
                else:
                    classes[semester].append(class_)

        return classes


"""Illustrate a time in a day, in the format HH:MM"""
class Time:
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


def main():
    timetable = Timetable()
    pprint(timetable.read_subject(2016, "comp10001"))


if __name__ == "__main__":
    main()
