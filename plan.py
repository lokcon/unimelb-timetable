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


def fetch_timetables(year, subjects, debug = False):
    if debug:
        import test_data
        return test_data.timetables

    t = Timetable()
    timetables = [t.read_subject(year, subject) for subject in subjects]

    print(timetables)

    return timetables


def draw_timetable(subject_codes, year = None):
    if not year:
        from datetime import date
        year = date.today().year

    # Fetch timetables
    subject_timetables = fetch_timetables(year, subject_codes, debug = False)

    # Flatten clases from different subjects
    classes = []
    for subject_timetable in subject_timetables:
        subject_code, subject_classes = subject_timetable
        if len(subject_classes) > 1:
            classes += choose_study_period(subject_code, subject_classes)
        else:
            [(study_period, subject_classes)] = subject_classes.items()
            classes += subject_classes


    # Calculate stacking of classes
    classes_by_day = {} # group classes by day
    for class_ in classes:
        classes_by_day.setdefault(class_["day"], []).append(class_)

    for day, classes_that_day in classes_by_day.items(): # process each weekday
        # construct intervals
        intervals = []
        for class_ in classes_that_day:
            intervals.append(class_["start"])
            intervals.append(class_["finish"])
        intervals.sort()
        intervals_count = [0] * len(intervals) # parallel counter list

        # stack classes on intervals
        for class_ in classes_that_day:
            start_index = intervals.index(class_["start"])
            finish_index = intervals.index(class_["finish"])
            peak_level = max(intervals_count[start_index: finish_index])

            class_["stacking"] = peak_level

            # increment stakcing level on the peark
            for index in range(start_index, finish_index):
                intervals_count[index] = peak_level + 1

        # retreive max stacking for each class
        for class_ in classes_that_day:
            start_index = intervals.index(class_["start"])
            finish_index = intervals.index(class_["finish"])
            class_["total_stacking"] = \
                max(intervals_count[start_index: finish_index])


    start = min([class_["start"] for class_ in classes])
    finish = max([class_["finish"] for class_ in classes])
    plot(classes, start, finish)

def time_to_float(time):
    (hour, minutes) = time
    return hour + minutes / 60

def get_color(subject, colors):
    COLORS = ["salmon", "wheat", "lightgreen", "pink", "lightblue"]
    if subject not in colors:
        colors[subject] = COLORS[len(colors)]

    return colors[subject]


def plot(classes, start, finish):
    import matplotlib.pyplot as plt

    TIME_MARGIN = 0.2
    ITEM_MARGIN = 0.02

    # Set axis
    fig = plt.figure(figsize = (10, 10))
    subplot = fig.add_subplot(1,1,1)
    subplot.yaxis.grid(which = "both")
    subplot.set_xlim(0.5, 5 + 0.5)
    subplot.set_ylim(time_to_float(finish) + TIME_MARGIN,
        time_to_float(start) - TIME_MARGIN)
    subplot.set_xticks(range(1,5+1))
    subplot.set_xticklabels(["Monday","Tuesday","Wednesday","Thursday", "Friday"])
    subplot.set_ylabel('Time')

    colors = {}
    for class_ in classes:
        day = class_["day"] + 1
        day_start = (day - 0.5) + class_["stacking"] / class_["total_stacking"]
        day_end = day_start + 1 / class_["total_stacking"]
        start = time_to_float(class_["start"])
        finish = time_to_float(class_["finish"])

        # Draw the square
        plt.fill_between(
            [day_start, day_end - ITEM_MARGIN],
             start + ITEM_MARGIN,
             finish - ITEM_MARGIN,
            color = get_color(class_["class"]["subject"], colors),
            edgecolor = "k",
            linewidth = 0.5)
        # Draw starting time
        plt.text(day_start + ITEM_MARGIN * 2,
            start + ITEM_MARGIN * 5,
            "%d:%02d" % class_["start"],
            fontsize = 8, va = "top")
        # Draw finishing time
        plt.text(day_start + ITEM_MARGIN * 2,
            finish - ITEM_MARGIN * 5,
            "%d:%02d" % class_["finish"],
            fontsize = 8, va = "bottom")
        # Draw class name
        plt.text((day_start + day_end) / 2,
            (start + finish) / 2,
            "%s/%s" % (class_["class"]["class_type"],
                class_["class"]["class_repeat"]),
            fontsize = 10,
            ha = "center", va = "center")

    plt.show()



def main():
    subject_codes = ["abpl10003"]
    draw_timetable(subject_codes)

if __name__ == "__main__":
    main()
