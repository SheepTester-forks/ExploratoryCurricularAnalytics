"""
Split course names from the academic plans into its subject and number to get
its prerequisites.
"""

from typing import Tuple


def parse_course_name(name: str) -> Tuple[str, str]:
    """
    Attempts to parse course name strings such as "MATH 10A/20A" into the course
    subject or department, which Curricular Analytics calls the prefix, and the
    course number.

    Returns a tuple of the prefix and number. If there isn't a prefix or number,
    use an empty string.

    This function is in its own file because parsing course names from academic
    plans might get quite complicated. For example, in the CS26 curriculum
    example file,

    - `CSE 197` has a prefix `CSE` and number `197/Elective`.
    - `Elective/Tech E1` has a prefix `CSE` with no number.
    - `SYSTEMS/NETW` has no prefix nor number.

    There are also numerous oddities in the academic plans CSV file's "Course"
    column (column D). Here's just a sampling.

    - BI30's ERC plan has `MATH 10A/20A` and `PHYS 1A&1AL`.
    - AN26's Muir plan has `MUIR UD Elective`.
    - AN26's Revelle plan has carets: `^^DEI` and `^LANGUAGE`.

    And so on. We'll probably list these oddities somewhere else, not here.

    Splitting course names is also necessary to get the prerequisites for the
    course.
    """
    # Temporary naïve approach
    if " " in name:
        subject, number = name.strip("*^").split(maxsplit=1)
        return subject, number if number[0].isnumeric() else ""
    else:
        return "", ""
