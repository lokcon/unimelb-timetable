from pprint import pprint
from timetable import Timetable
from subject_codes import STUDY_PERIODS

def choose_study_period(subject_code, subject_classes):
    """Prompt the user to choose a study period of a subject
    Return the classes in that study period
    """

    # Prompt the user
    print("%s has the following study periods:" % subject_code.upper())

    options_dict = {}
    for count, study_period in enumerate(sorted(subject_classes.keys()), 1):
        print("\t%d: %s (%s)"
            % (count, STUDY_PERIODS[study_period], study_period))

        options_dict[count] = study_period

    # Construct a string of options e.g. "[1,2,3,4]"
    options = range(1, len(subject_classes) + 1)
    options_str = ""
    for i in options:
        options_str += "%s," % i
    options_str = options_str[:-1]

    # Ask the user
    import sys
    sys.stdout.write("Chose a study period [%s]: " % options_str)
    try:
        choosen_num = int(input())
    except ValueError:
        choosen_num = 1
    else:
        if choosen_num not in options:
            print("Invalid option, defaults to option 1")
            choosen_num = 1

    return subject_classes[options_dict[choosen_num]]


def fetch_timetables(year, subjects, debug = False, dump = False):
    if debug:
        import json
        with open("test.json") as f:
            return json.loads(f.read())

    t = Timetable()
    timetables = [t.read_subject(year, subject) for subject in subjects]

    if dump:
        import json
        with open("test.json", 'w') as f:
            f.write(json.dumps(timetables))

    return timetables


def draw_timetable(subject_codes, year = None):
    if not year:
        from datetime import date
        year = date.today().year

    # Fetch timetables
    subject_timetables = fetch_timetables(year, subject_codes, debug = True)

    # Flatten clases from different subjects
    classes = []
    for subject_timetable in subject_timetables:
        subject_code, subject_classes = subject_timetable
        if len(subject_classes) > 1:
            classes += choose_study_period(subject_code, subject_classes)
        else:
            [(study_period, subject_classes)] = subject_classes.items()
            classes += subject_classes

    # Sort by day, start, then finish of a class
    classes = sorted(classes,
        key = lambda x:(x["day"], x["start"], x["finish"]))

    for class_ in classes:
        class_info = class_["class"]
        print("%s, %s, %s"
            % (class_info["subject"], class_info["class_type"],
            class_info["class_repeat"]))
    start = min([class_["start"] for class_ in classes])
    finish = max([class_["finish"] for class_ in classes])

    plot(classes, start, finish)

def time_to_float(time):
    (hour, minutes) = time
    return hour + minutes / 60


def plot(classes, start, finish):
    import matplotlib.pyplot as plt

    TIME_MARGIN = 0.2
    ITEM_MARGIN = 0.02

    # Set axis
    fig = plt.figure(figsize = (10, 10))
    subplot = fig.add_subplot(1,1,1)
    subplot.yaxis.grid()
    subplot.set_xlim(0.5, 5 + 0.5)
    subplot.set_ylim(time_to_float(finish) + TIME_MARGIN,
        time_to_float(start) - TIME_MARGIN)
    subplot.set_xticks(range(1,5+1))
    subplot.set_xticklabels(["Monday","Tuesday","Wednesday","Thursday", "Friday"])
    subplot.set_ylabel('Time')

    for class_ in classes:
        pprint(class_)
        day = class_["day"] + 1
        (day_start, day_end) = (day - 0.5, day + 0.5)
        start = time_to_float(class_["start"])
        finish = time_to_float(class_["finish"])

        # Draw the square
        plt.fill_between(
            [day_start + ITEM_MARGIN, day_end - ITEM_MARGIN],
             start + ITEM_MARGIN,
             finish - ITEM_MARGIN,
            color = "lightblue",
            edgecolor = "k",
            linewidth = 0.5)
        # Draw starting time
        plt.text(day_start + ITEM_MARGIN * 2,
            start + ITEM_MARGIN * 5,
            "%d:%02d" % tuple(class_["start"]),
            fontsize = 8, va = "top")
        # Draw class name
        plt.text(day,
            (start + finish) / 2,
            "%s/%s" % (class_["class"]["class_type"],
                class_["class"]["class_repeat"]),
            fontsize = 10,
            ha = "center", va = "center")

    plt.show()



def main():
    subject_codes = ["comp20003"] #, "swen20003", "info20003", "mast20026"]
    draw_timetable(subject_codes)

if __name__ == "__main__":
    main()
