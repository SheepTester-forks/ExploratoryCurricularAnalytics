"""
Outputs a CSV file in Curricular Analytics' curriculum and degree plan formats
from the parsed academic plans and course prerequisites.

Exports:
    `output`, a generator function that takes a major code and optionally a
    college code and yields lines of the CSV file. You can use a for loop on the
    return value to print, write to a file, or store the lines in a string
    variable.
"""

from typing import Dict, Generator, Iterable, List, NamedTuple, Optional

from parse import (
    CourseCode as CourseCode,
    MajorPlans,
    PlannedCourse,
    major_plans,
    major_codes,
    prereqs,
)
from parse_course_name import parse_course_name

CourseId = str
Term = str


class CourseEntry(NamedTuple):
    code: CourseCode
    course: PlannedCourse
    id: str
    term: str

    def with_id(self, new_id: str) -> "CourseEntry":
        return CourseEntry(self.code, self.course, new_id, self.term)


INSTITUTION = "University of California, San Diego"
SYSTEM_TYPE = "Quarter"
HEADER = [
    "Course ID",
    "Course Name",
    "Prefix",
    "Number",
    "Prerequisites",
    "Corequisites",
    "Strict-Corequisites",
    "Credit Hours",
    "Institution",
    "Canonical Name",
    "Term",
]
CURRICULUM_COLS = 10
DEGREE_PLAN_COLS = 11


def output_header(
    curriculum: str = "",
    degree_plan: Optional[str] = None,
    institution: str = "",
    degree_type: str = "",
    system_type: str = "",
    cip: str = "",
) -> Generator[List[str], None, None]:
    """
    Outputs the header for the CSV file. See Curricular Analytics'
    documentation for the CSV header format:
    https://curricularanalytics.org/files.
    """
    yield ["Curriculum", curriculum]
    if degree_plan is not None:
        yield ["Degree Plan", degree_plan]
    yield ["Institution", institution]
    yield ["Degree Type", degree_type]
    yield ["System Type", system_type]
    yield ["CIP", cip]


college_names = {
    "RE": "Revelle",
    "MU": "Muir",
    "TH": "Marshall",
    "WA": "Warren",
    "FI": "ERC",
    "SI": "Sixth",
    "SN": "Seventh",
}


def output_plan(
    major: MajorPlans, college: Optional[str] = None
) -> Generator[List[str], None, None]:
    """
    Outputs a curriculum or degree plan in Curricular Analytics' format (CSV).

    To output a degree plan, specify the college that the degree plan is for. If
    the college isn't specified, then `output_plan` will output the major's
    curriculum instead.
    """
    major_info = major_codes[major.major_code]
    # NOTE: Currently just gets the last listed award type (bias towards BS over
    # BA). Will see how to deal with BA vs BS
    yield from output_header(
        curriculum=major_info.name,
        degree_plan=college and f"{major_info.name}/ {college_names[college]}",
        institution=INSTITUTION,
        degree_type=list(major_info.award_types)[-1],
        system_type=SYSTEM_TYPE,
        cip=major_info.cip_code,
    )

    course_ids: Dict[CourseCode, str] = {}
    main_courses: List[CourseEntry] = []
    additional_courses: List[CourseEntry] = []
    if college:
        for i, quarter in enumerate(major.plans[college].quarters):
            for course in quarter:
                code = parse_course_name(course.course_code)
                (
                    main_courses
                    if course.type == "DEPARTMENT" or course.overlaps_ge
                    else additional_courses
                ).append(CourseEntry(code, course, "", str(i + 1)))
        main_courses = [
            entry.with_id(str(i + 1)) for i, entry in enumerate(main_courses)
        ]
        additional_courses = [
            entry.with_id(str(len(main_courses) + i + 1))
            for i, entry in enumerate(additional_courses)
        ]
        for entry in main_courses:
            course_ids[entry.code] = entry.id
        for entry in additional_courses:
            course_ids[entry.code] = entry.id
    else:
        for i, course in enumerate(major.curriculum()):
            code = parse_course_name(course.course_code)
            course_ids[code] = str(i + 1)
            main_courses.append(CourseEntry(code, course, str(i + 1), ""))

    for courses in main_courses, additional_courses:
        if not college and courses is additional_courses:
            break
        yield ["Courses" if courses is main_courses else "Additional Courses"]
        yield HEADER
        for (prefix, number), course, course_id, term in courses:
            prereq_ids: List[str] = []
            coreq_ids: List[str] = []
            if (prefix, number) in prereqs:
                for alternatives in prereqs[prefix, number]:
                    for code, concurrent in alternatives:
                        if code in course_ids:
                            (coreq_ids if concurrent else prereq_ids).append(
                                course_ids[code]
                            )
            yield [
                course_id,
                course.course_code.strip("*"),  # Asterisks seem to break the site
                prefix,
                number,
                ";".join(prereq_ids),
                ";".join(coreq_ids),
                "",
                f"{course.units:g}",  # https://stackoverflow.com/a/2440708
                "",
                "",
                term,
            ]


def rows_to_csv(rows: Iterable[List[str]], columns: int) -> Generator[str, None, None]:
    """
    Converts a list of lists of fields into lines of CSV records. Yields a
    newline-terminated line.

    The return value from `output_plan` should be passed as the `rows` argument.

    `output_plan` always outputs a "Term" column because I'm lazy, so this
    function can cut off extra columns or adds empty fields as needed to meet
    the column count.
    """
    for row in rows:
        yield (
            ",".join(
                [
                    f'"{field}"' if any(c in field for c in ",\r\n") else field
                    for field in row
                ][:columns]
                + [""] * (columns - len(row))
            )
            + "\n"
        )


def output(major: str, college: Optional[str] = None) -> Generator[str, None, None]:
    return rows_to_csv(
        output_plan(major_plans[major], college),
        DEGREE_PLAN_COLS if college else CURRICULUM_COLS,
    )


def to_file(path: str, csv: Iterable[str]) -> None:
    """
    Writes the records of the given CSV file to a file at the given path.

    For example, the following saves the CS major curriculum to
    `files/Curriculum-CS26.csv` and the ERC degree plan for CS to `files/Degree
    Plan-ERC-CS26.csv`.

    ```py
    to_file("files/Curriculum-CS26.csv", output("CS26"))
    to_file("files/Degree Plan-ERC-CS26.csv", output("CS26", 'FI'))
    ```
    """
    with open(path, "w") as file:
        file.writelines(csv)


if __name__ == "__main__":
    to_file("files/CS26_Sixth.csv", output("CS26", "SI"))
    for line in output("CS26", "SI"):
        print(line, end="")
