"""
Lists what majors require each course. I might've done this already, I forgot.

::seats::web

python3 courses_req_by_majors.py
python3 courses_req_by_majors.py json > courses_req_by_majors.json
"""

import json
from sys import stdout
from typing import NamedTuple
from parse import major_plans
from parse_defs import CourseCode
from university import university
from util import partition, sorted_dict


class CourseTaker(NamedTuple):
    year: int
    quarter: int
    major_code: str
    college_code: str
    for_major: bool


MOST = 0.5
'Minimum percentage considered to be "most" colleges/majors (to allow for errors)'


def print_json() -> None:
    # TODO: partition by term
    majors = major_plans(2022)
    courses = partition(
        (
            course.course_code,
            CourseTaker(
                course.term_index // 3,
                course.term_index % 3,
                major_code,
                college,
                course.for_major,
            ),
        )
        for major_code, plans in majors.items()
        # Exclude undeclared majors
        if len(plans.colleges) >= len(university.college_codes) * MOST
        for college in university.college_codes
        if college in plans.colleges
        for course in plans.plan(college)
        if course.course_code
    )
    json.dump(
        {
            "colleges": list(university.college_names.items()),
            "quarterNames": university.terms,
            "courses": [
                {
                    "courseCode": str(course_code),
                    "takers": takers,
                }
                for course_code, takers in sorted_dict(courses, key=CourseCode.parts)
            ],
        },
        stdout,
    )


def print_readable() -> None:
    courses = partition(
        (course.course_code, major_code)
        for major_code, plans in major_plans(2022).items()
        for college in plans.colleges
        for course in plans.plan(college)
        if course.for_major and course.course_code
    )
    for course_code, major_codes in sorted_dict(courses, key=CourseCode.parts):
        majors = ", ".join(sorted(set(major_codes)))
        print(f"[{course_code}] {majors}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "json":
        print_json()
    else:
        print_readable()
