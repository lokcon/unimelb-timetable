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
        choosen_num = int(raw_input())
    except ValueError:
        choosen_num = 1
    else:
        if choosen_num not in options:
            print("Invalid option, defaults to option 1")
            choosen_num = 1

    return subject_classes[options_dict[choosen_num]]


def fetch_timetables(subjects, debug = False):
    if debug:
        import json
        with open("test.json") as f:
            return json.loads(f.read())

    t = Timetable()
    return [t.read_subject(year, subject) for subject in subjects]


def draw_timetable(subject_codes, year = None):
    if not year:
        from datetime import date
        year = date.today().year

    # Fetch timetables
    subject_timetables = fetch_timetables(subject_codes, debug = True)

    classes = []
    for subject_timetable in subject_timetables:
        subject_code, subject_classes = subject_timetable
        if len(subject_classes) > 1:
            classes += choose_study_period(subject_code, subject_classes)
        else:
            [(study_period, subject_classes)] = subject_classes.items()
            classes += subject_classes


def main():
    subject_codes = ["comp20003", "swen20003", "info20003", "mast20026"]
    draw_timetable(subject_codes)

if __name__ == "__main__":
    main()
