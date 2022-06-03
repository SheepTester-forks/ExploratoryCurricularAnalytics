"""
Parses the prerequisite and academic plan CSV files into objects for easier
manipulation.

Exports:
    `prereqs`, a dictionary mapping from a subject code-number tuple to a list
    of prerequisites, which are each lists of possible course codes to satisfy
    the requirement.

    `major_plans`, a dictionary mapping from ISIS major codes to `MajorPlans`
    objects, which contains a dictionary mapping college codes to `Plan`s, which
    have a list of list of `PlannedCourse`s for each quarter.

    `major_codes`, a dictionary mapping from ISIS major codes to `MajorInfo`
    objects, which contains data from the ISIS major codes spreadsheet.
"""

from typing import Dict, List, Literal, NamedTuple, Optional, Set, Tuple

CourseCode = Tuple[str, str]


class Prerequisite(NamedTuple):
    course_code: CourseCode
    allow_concurrent: bool


def read_csv_from(
    path: str, not_found_msg: Optional[str] = None, strip: bool = False
) -> List[List[str]]:
    """
    Reads and parses the file at the given path as a CSV file.

    The CSV parser doesn't validate the CSV, so it's kind of dumb, but I don't
    think much cleverness is needed for parsing these fairly tame CSV files.
    There is support for quoted fields and rudimentary support for backslashes
    (they won't break, but they're currently not interpreted, so `\\"` remains
    in the field value).

    This function returns a list of records (rows), each containing the fields
    of the record. Quoted fields have their double quotes removed.

    Since I gitignored the CSV files, I'm using `not_found_msg` to give more
    helpful error messages in case someone running this code hasn't put the
    necessary CSV files in files/ folder.

    Set `strip` to true to remove whitespace padding from record fields.
    """
    rows: List[List[str]] = []

    def parse_field(field: str) -> str:
        """
        Helper function to process a raw field from the CSV file. Removes quotes
        from quoted fields and strips whitespace if desired.
        """
        if len(field) > 0 and field[0] == '"':
            # NOTE: Currently doesn't deal with backslashes
            field = field[1:-1]
        return field.strip() if strip else field

    try:
        with open(path, "r") as file:
            row_overflow: Optional[Tuple[List[str], str]] = None
            for line in file.read().splitlines():
                row: List[str]
                in_quotes: bool
                if row_overflow:
                    row = row_overflow[0]
                    in_quotes = True
                else:
                    row = []
                    rows.append(row)
                    in_quotes = False
                last_index: int = 0
                ignore_next: bool = False  # For backslashes in quotes
                for i, char in enumerate(line + ","):
                    if in_quotes:
                        if ignore_next:
                            ignore_next = False
                        elif char == '"':
                            in_quotes = False
                        elif char == "\\":
                            ignore_next = True
                    else:
                        if char == '"':
                            in_quotes = True
                        elif char == ",":
                            prefix: str = row_overflow[1] if row_overflow else ""
                            row_overflow = None
                            row.append(parse_field(prefix + line[last_index:i]))
                            last_index = i + 1
                if in_quotes:
                    prefix: str = row_overflow[1] if row_overflow else ""
                    row_overflow = row, prefix + line[last_index:] + "\n"
    except FileNotFoundError as e:
        raise e if not_found_msg is None else FileNotFoundError(not_found_msg)
    return rows


def prereq_rows_to_dict(
    rows: List[List[str]],
) -> Dict[CourseCode, List[List[Prerequisite]]]:
    """
    Converts prerequisite rows from a CSV to a dictionary mapping between
    courses and the prerequisites.

    The dictionary values are lists of lists. The outer list is a list of
    requirements, like an AND, while each inner list is a list of possible
    courses to satisfy the requirement, like an OR.
    """
    prereqs: Dict[CourseCode, List[List[Prerequisite]]] = {}
    for subject, number, prereq_id, pre_sub, pre_num, allow_concurrent in rows:
        course: CourseCode = subject, number
        prereq = Prerequisite((pre_sub, pre_num), allow_concurrent == "Y")
        if course not in prereqs:
            prereqs[course] = []
        index = int(prereq_id) - 1
        while len(prereqs[course]) <= index:
            prereqs[course].append([])
        # Could probably include the allow concurrent registration info here
        prereqs[course][index].append(prereq)
    return prereqs


class PlannedCourse:
    """
    Represents a course in an academic plan.
    """

    course_code: str
    units: float
    type: Literal["COLLEGE", "DEPARTMENT"]
    overlaps_ge: bool

    def __init__(
        self,
        course: str,
        units: float,
        type: Literal["COLLEGE", "DEPARTMENT"],
        overlaps_ge: bool,
    ) -> None:
        self.course_code = course
        self.units = units
        self.type = type
        self.overlaps_ge = overlaps_ge

    def __repr__(self) -> str:
        return f"PlannedCourse(course_code={repr(self.course_code)}, units={repr(self.units)}, type={repr(self.type)}, overlaps_ge={repr(self.overlaps_ge)})"


class Plan:
    """
    Represents a college-specific academic plan. Can be used to create degree
    plans for Curricular Analytics.
    """

    quarters: List[Set[PlannedCourse]]

    def __init__(self, quarters: Optional[List[Set[PlannedCourse]]] = None) -> None:
        # https://stackoverflow.com/a/33990699
        self.quarters = [set() for _ in range(12)] if quarters is None else quarters

    def __repr__(self) -> str:
        return f"Plan(quarters={repr(self.quarters)})"


class MajorPlans:
    """
    Represents a major's set of academic plans. Contains plans for each college.

    To get the plan for a specific college, use the two-letter college code. For
    example, `plans["FI"]` contains the academic plan for ERC (Fifth College).
    """

    department: str
    major_code: str
    plans: Dict[str, Plan]

    def __init__(
        self, department: str, major_code: str, plans: Optional[Dict[str, Plan]] = None
    ) -> None:
        self.department = department
        self.major_code = major_code
        self.plans = {} if plans is None else plans

    def curriculum(self, college: str = "RE") -> Set[PlannedCourse]:
        """
        Creates an academic plan with college-specific courses removed. Can be
        used to create a curriculum for Curricular Analytics.

        The `overlaps_ge` attribute for these courses should be ignored (because
        there is no college whose GEs the course overlaps with).

        Assumes that the department plans are the same for all colleges. It
        might be worth checking if that's actually the case. By default, it
        arbitrarily uses Revelle's college plan, but you can specify a college
        code in `college` to base the degree plan off a different college.
        """
        return set(
            course
            for quarter in self.plans[college].quarters
            for course in quarter
            if course.type == "DEPARTMENT" or course.overlaps_ge
        )

    def __repr__(self) -> str:
        return f"Major(department={repr(self.department)}, major_code={repr(self.major_code)}, plans={repr(self.plans)})"


def plan_rows_to_dict(rows: List[List[str]]) -> Dict[str, MajorPlans]:
    """
    Converts the academic plans CSV rows into a dictionary of major codes to
    `Major` objects.
    """
    majors: Dict[str, MajorPlans] = {}
    for (
        department,  # Department
        major_code,  # Major
        college_code,  # College
        course_code,  # Course
        units,  # Units
        course_title,  # Course Type
        overlap,  # GE/Major Overlap
        _,  # Start Year
        year,  # Year Taken
        quarter,  # Quarter Taken
        _,  # Term Taken
    ) in rows:
        if major_code not in majors:
            majors[major_code] = MajorPlans(department, major_code)
        if college_code not in majors[major_code].plans:
            majors[major_code].plans[college_code] = Plan()
        quarter = (int(year) - 1) * 3 + int(quarter) - 1
        if course_title != "COLLEGE" and course_title != "DEPARTMENT":
            raise TypeError('Course type is neither "COLLEGE" nor "DEPARTMENT"')
        majors[major_code].plans[college_code].quarters[quarter].add(
            PlannedCourse(course_code, float(units), course_title, overlap == "Y")
        )
    return majors


class MajorInfo:
    """
    Represents information about a major from the ISIS major code list.

    You can find the major code list by Googling "isis major codes," but it's
    not going to be in the format that this program expects:
    https://blink.ucsd.edu/_files/instructors-tab/major-codes/isis_major_code_list.xlsx
    """

    isis_code: str
    name: str
    department: str
    cip_code: str
    award_types: Set[str]

    def __init__(
        self,
        isis: str,
        description: str,
        department: str,
        cip: str,
        award_types: Set[str],
    ) -> None:
        self.isis_code = isis
        self.name = description
        self.department = department
        self.cip_code = cip
        self.award_types = award_types

    def __repr__(self) -> str:
        return f"MajorInfo(isis_code={repr(self.isis_code)}, name={repr(self.name)}, department={repr(self.department)}, cip_code={repr(self.cip_code)}, award_types={repr(self.award_types)})"


def major_rows_to_dict(rows: List[List[str]]) -> Dict[str, MajorInfo]:
    majors: Dict[str, MajorInfo] = {}
    for (
        _,  # Previous Local Code
        _,  # UCOP Major Code (CSS)
        isis_code,  # ISIS Major Code
        _,  # Major Abbreviation
        description,  # Major Description
        _,  # Diploma Title
        _,  # Start Term
        _,  # End Term
        _,  # Student Level
        department,  # Department
        award_types,  # Award Type
        _,  # Program Length (in years)
        _,  # College
        cip_code,  # CIP Code
        _,  # CIP Description
        _,  # STEM
        _,  # Self Supporting
        _,  # Discontinued or Phasing Out
        _,  # Notes
    ) in rows:
        majors[isis_code] = MajorInfo(
            isis_code,
            description,
            department,
            cip_code,
            set(award_types.split(" ")) if award_types else set(),
        )
    return majors


prereqs = prereq_rows_to_dict(
    read_csv_from(
        "./files/prereqs.csv",
        "There is no `prereqs.csv` file in the files/ folder. See the README for where to download it from.",
        strip=True,
    )[1:]
)

major_plans = plan_rows_to_dict(
    read_csv_from(
        "./files/academic_plans.csv",
        "There is no `academic_plans.csv` file in the files/ folder. See the README for where to download it from.",
        strip=True,
    )[1:]
)

major_codes = major_rows_to_dict(
    read_csv_from(
        "./files/isis_major_code_list.xlsx - Major Codes.csv",
        "There is no `isis_major_code_list.xlsx - Major Codes.csv` file in the files/ folder. See the README for where to download it from.",
        strip=True,
    )[1:]
)

if __name__ == "__main__":
    #print(prereqs["CAT", "1"])
    #print(next(major for major in majors if major.major == "CS26").curriculum())
    #print(prereqs["MATH", "109"])
    #print(prereqs["MATH", "109"][0][0])
    # print(majors[0].major)
    print(majors[0].curriculum("MU").quarters[11][0])
    #print(repr(majors[0].curriculum("RE")) == repr(majors[0].curriculum("MU")))
    # print(majors[0].curriculum("RE").quarters[0] ==
    # majors[0].curriculum("MU").quarters[0])
