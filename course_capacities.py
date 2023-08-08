"""
Takes the number of incoming first years in each major-college and the number of
seats left in each course and outputs the number of seats needed for freshmen
and seats available for each course. Eighth first-years are ignored.

::seats::python

python3 course_capacities.py > files/course_capacities_output.csv
"""

import csv
from typing import Dict, List, NamedTuple, TextIO, Tuple
from parse import major_plans
from parse_defs import CourseCode

from university import university

YEAR_COUNT = 4


class StudentType(NamedTuple):
    year: int
    "Between 0 and 3 (0-indexed)."
    major: str
    college: str


StudentBody = Dict[StudentType, int]
ClassSizeOutput = Dict[CourseCode, List[int]]
CourseEnrollment = Dict[str, Tuple[int, int]]


def from_majors(students_by_major: Dict[str, int]) -> StudentBody:
    partitions = YEAR_COUNT * len(university.college_codes)
    students: StudentBody = {}
    for major, count in students_by_major.items():
        for year in range(YEAR_COUNT):
            for college in university.college_codes:
                students[StudentType(year, major, college)] = count // partitions
    return students


def from_first_years(file: TextIO) -> StudentBody:
    students: StudentBody = {}
    # It seems they alphabetized the colleges
    college_codes = dict(
        {name: code for code, name in university.college_names.items()},
        Eighth="EI",
        Roosevelt="FI",
    )
    reader = csv.reader(file)
    _, *college_names, _ = next(reader)  # Header
    for major_code, *by_college, _total in reader:
        if len(major_code) != 4:
            continue
        for i, count in enumerate(by_college):
            students[StudentType(0, major_code, college_codes[college_names[i]])] = int(
                count.replace(",", "") or "0"
            )
    return students


def class_sizes(students: StudentBody, year: int) -> ClassSizeOutput:
    """
    Iterates over each major plan and calculates the
    number of students that will take the course in each term.
    """
    courses: ClassSizeOutput = {}
    for major_code, plans in major_plans(year).items():
        for college in university.college_codes:
            if college not in plans.colleges:
                continue
            for course in plans.plan(college):
                if course.course_code:
                    year, term = university.get_term(course.term_index)
                    student_type = StudentType(year, major_code, college)
                    if student_type in students:
                        if course.course_code not in courses:
                            courses[course.course_code] = [0 for _ in university.terms]
                        courses[course.course_code][term] += students[
                            StudentType(year, major_code, college)
                        ]
    return courses


def output_class_sizes(sizes: ClassSizeOutput, file: TextIO) -> None:
    file.write("Course,")
    file.write(",".join(university.terms))
    file.write("\n")
    for course, size in sorted(sizes.items(), key=lambda item: item[0]):
        file.write(str(course))
        file.write(",")
        file.write(",".join(map(str, size)))
        file.write("\n")


def output_seats_left(
    sizes: ClassSizeOutput, term: int, enrollment: CourseEnrollment, file: TextIO
) -> None:
    file.write("Course,Students needing course,Capacity,Currently available\n")
    for course, size in sorted(sizes.items(), key=lambda item: item[0]):
        if size[term] == 0:
            continue
        enrolled, capacity = enrollment.get("".join(course), (0, 0))
        file.write(str(course))
        file.write(",")
        file.write(str(size[term]))
        file.write(",")
        file.write(str(capacity))
        file.write(",")
        file.write(str(capacity - enrolled))
        file.write("\n")


def main() -> None:
    import sys

    with open("files/ClassCapCalculatorNewStudents.csv", newline="") as file:
        student_body = from_first_years(file)

    courses: CourseEnrollment = {}
    with open("files/ClassCapCalculatorCourses.csv", newline="") as file:
        reader = csv.reader(file)
        next(reader)
        for course_code, _title, _type, capacity, enrolled in reader:
            capacity = int(capacity.replace(",", ""))
            enrolled = int(enrolled.replace(",", ""))
            if course_code in courses:
                # The spreadsheet they gave is a bit weird. It lists many
                # courses multiple times for each section type, but only one
                # section type is enrollable. This section type usually has
                # non-zero enrollment and has the smallest capacity. For
                # example, CSE 8A DI and LE have a capacity of 600 with 0
                # students enrolled, while LA has a capacity of 180 (which is
                # what's shown on WebReg) and 181 students enrolled. tbh, idk
                # why it's 181 enrolled, since there is much more than 1 student
                # on the waitlist. A section might be over-enrolled right now
                # for student priority reasons, maybe.
                # - CSE8A,Intro to Programming 1,DI,600,0
                # - CSE8A,Intro to Programming 1,LA,180,181
                # - CSE8A,Intro to Programming 1,LE,600,0
                other_enroll, other_cap = courses[course_code]
                if capacity < other_cap or enrolled > other_enroll:
                    # Overwrite the existing entry; this section is what we want
                    # (eg DI, LA)
                    pass
                else:
                    # Skip, it's not the section we want (eg LE)
                    continue
            courses[course_code] = enrolled, capacity
    output_seats_left(class_sizes(student_body, 2022), 0, courses, sys.stdout)


if __name__ == "__main__":
    main()
