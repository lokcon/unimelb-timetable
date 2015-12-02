DEFAULT_OUTPUT_FORMAT = "svg"
SUPPORTED_OUTPUT_FORMATS = ["svg", "png"]

def _stack_classes(classes):
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

            max_level = max(intervals_count[index] for index in range(start_index, finish_index))

            class_["stacking"] = max_level

            # add one more level
            for index in range(start_index, finish_index):
                intervals_count[index] = max_level + 1


        # retreive max stacking for each class
        for class_ in classes_that_day:
            start_index = intervals.index(class_["start"])
            finish_index = intervals.index(class_["finish"])
            class_["total_stacking"] = \
                max(intervals_count[index] for index in range(start_index, finish_index))

    return classes


def _flatten_classes(subject_timetables):
    all_classes = []
    for timetable in subject_timetables:
        (year, semester, subject_code), classes = timetable
        all_classes += classes

    return all_classes


def _plot_matplot(classes, start, finish, format = DEFAULT_OUTPUT_FORMAT, show = False):
    import matplotlib.pyplot as plt

    TIME_MARGIN = 0.3
    X_MARGIN = 0.015
    Y_MARGIN = 0.025

    # Set axis
    fig = plt.figure(figsize = (13, 10), facecolor = "white")
    subplot = fig.add_subplot(1,1,1)

    # Set grids
    subplot.xaxis.grid(which = "major", alpha = 0)
    subplot.xaxis.grid(which = "minor", alpha = 0.85)
    subplot.yaxis.grid(which = "major", alpha = 0.85)
    subplot.yaxis.grid(which = "minor", alpha = 0.3)

    # Set limits of axes
    subplot.set_xlim(0.5, 5 + 0.5)
    subplot.set_ylim(_time_to_float(finish) + TIME_MARGIN,
        _time_to_float(start) - TIME_MARGIN)

    # Set labels of axes
    subplot.set_xlabel("Day")
    subplot.set_xticklabels(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    subplot.set_ylabel('Time')
    subplot.set_yticklabels(
        ["%d:00" % i for i in
            range(_time_to_int(start), _time_to_int(finish) + 1)])

    # Set x ticks
    subplot.set_xticks(range(1, 5 + 1))
    subplot.set_xticks([i + 0.5 for i in range(1, 5 + 1)], minor = True)

    # Set y ticks
    subplot.set_yticks(range(_time_to_int(start), _time_to_int(finish) + 1))
    subplot.set_yticks(
        [i / 4 for i in
            range(_time_to_int(start) * 4, (_time_to_int(finish) + 1) * 4)],
        minor = True)

    colors = {}
    for class_ in classes:
        # x-coordinates
        day = class_["day"] + 1
        day_start = (day - 0.5) + class_["stacking"] / class_["total_stacking"]
        day_end = day_start + 1 / class_["total_stacking"]
        # y-coordinates
        start = _time_to_float(class_["start"])
        finish = _time_to_float(class_["finish"])

        # class information
        class_name = "%s/%s" % (class_["class"]["class_type"],
            class_["class"]["class_repeat"])
        too_narrow = len(class_name) * class_["total_stacking"] >= 19
            # 19 is the tested magic number

        # Draw the square
        plt.fill_between(
            [day_start + X_MARGIN, day_end - X_MARGIN],
             start + Y_MARGIN,
             finish - Y_MARGIN,
            color = _get_color(class_["class"]["subject"], colors))

        if not too_narrow:
            # Draw starting time
            plt.text(day_start + X_MARGIN * 2,
                start + Y_MARGIN * 4,
                "%d:%02d" % class_["start"],
                fontsize = 8, va = "top")
            # Draw finishing time
            plt.text(day_start + X_MARGIN * 2,
                finish - Y_MARGIN * 4,
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

    if show:
        plt.show()

    # determine format
    if format not in SUPPORTED_OUTPUT_FORMATS:
        format = DEFAULT_OUTPUT_FORMAT # fallback to defaults

    # Get the bytes of the png
    import io
    image = io.BytesIO()
    fig.savefig(image, format = format)
    image.seek(0)

    return image.read()


def _time_to_float(time):
    (hour, minutes) = time
    return hour + minutes / 60

def _time_to_int(time):
    return int(_time_to_float(time))


def _get_color(subject, colors):
    COLORS = ["salmon", "wheat", "lightgreen", "pink", "lightblue"]
    if subject not in colors:
        colors[subject] = COLORS[len(colors)]

    return colors[subject]


def fetch_timetables(subjects):
    from timetable import Timetable
    subject_timetables = []
    for year, semester, subject_code in subjects:
        subject_timetables.append(
            Timetable.read_subject(year, semester, subject_code))

    return subject_timetables


def draw_timetable(subject_timetables, format = DEFAULT_OUTPUT_FORMAT):
    # Flatten clases from different subjects
    all_classes = _flatten_classes(subject_timetables)

    # calculate stacking width of clashing classes
    all_classes = _stack_classes(all_classes)

    # calculate start and finish of timetable
    earliest_start = min([class_["start"] for class_ in all_classes])
    lattest_finish = max([class_["finish"] for class_ in all_classes])

    # plot the timetable
    return _plot_matplot(all_classes, earliest_start, lattest_finish, format)


def fetch_and_draw_timetable(subjects, format = DEFAULT_OUTPUT_FORMAT):
    return draw_timetable(fetch_timetables(subjects), format)
