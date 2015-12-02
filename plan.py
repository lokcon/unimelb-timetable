from pprint import pprint
from timetable import Timetable
from subject_codes import SEMESTERS


def stack_classes(classes):
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

    return classes


def flatten_classes(subject_timetables):
    all_classes = []
    for timetable in subject_timetables:
        (year, semester, subject_code), classes = timetable
        all_classes += classes

    return all_classes


def draw_timetable(subjects):
    # Fetch timetables
    t = Timetable()
    subject_timetables = []
    for year, semester, subject_code in subjects:
        subject_timetables.append(t.read_subject(year, semester, subject_code))

    print(subject_timetables)

    # Flatten clases from different subjects
    all_classes = flatten_classes(subject_timetables)

    # calculate stacking width of clashing classes
    all_classes = stack_classes(all_classes)

    # calculate start and finish of timetable
    earliest_start = min([class_["start"] for class_ in all_classes])
    lattest_finish = max([class_["finish"] for class_ in all_classes])

    # plot the timetable
    plot_matplot(all_classes, earliest_start, lattest_finish)


def time_to_float(time):
    (hour, minutes) = time
    return hour + minutes / 60


def get_color(subject, colors):
    COLORS = ["salmon", "wheat", "lightgreen", "pink", "lightblue"]
    if subject not in colors:
        colors[subject] = COLORS[len(colors)]

    return colors[subject]


def plot_matplot(classes, start, finish):
    import matplotlib.pyplot as plt

    TIME_MARGIN = 0.2
    ITEM_MARGIN = 0.02

    # Set axis
    fig = plt.figure(figsize = (13, 10))
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
        # x-coordinates
        day = class_["day"] + 1
        day_start = (day - 0.5) + class_["stacking"] / class_["total_stacking"]
        day_end = day_start + 1 / class_["total_stacking"]
        # y-coordinates
        start = time_to_float(class_["start"])
        finish = time_to_float(class_["finish"])

        # class information
        class_name = "%s/%s" % (class_["class"]["class_type"],
            class_["class"]["class_repeat"])
        too_narrow = class_["total_stacking"] >= 4

        # Draw the square
        plt.fill_between(
            [day_start, day_end - ITEM_MARGIN],
             start + ITEM_MARGIN,
             finish - ITEM_MARGIN,
            color = get_color(class_["class"]["subject"], colors),
            edgecolor = "k",
            linewidth = 0.5)

        if not too_narrow:
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
        if too_narrow:
            rotation = 270
        else:
            rotation = 0

        plt.text((day_start + day_end) / 2,
            (start + finish) / 2,
            class_name,
            fontsize = 10,
            ha = "center", va = "center",
            rotation = rotation)

    plt.show()



def main():
    subjects = [(2015, "SM1", "abpl10003")]
    draw_timetable(subjects)

if __name__ == "__main__":
    main()
