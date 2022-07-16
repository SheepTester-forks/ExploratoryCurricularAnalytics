from typing import Dict, Set
from parse import CourseCode, major_plans, prereqs
from parse_course_name import parse_course_name

flattened = {
    course_code: {
        course.course_code for alternatives in requirements for course in alternatives
    }
    for course_code, requirements in prereqs.items()
}


def get_nested_prereqs(code: CourseCode, cache: Set[CourseCode]) -> None:
    if code not in cache:
        if code in flattened:
            cache |= flattened[code]
            for prereq in flattened[code]:
                get_nested_prereqs(prereq, cache)


redundancies: Dict[CourseCode, Set[CourseCode]] = {}

for course_code, requisites in flattened.items():
    prereqs_of_prereqs: Set[CourseCode] = set()
    for prereq in requisites:
        get_nested_prereqs(prereq, prereqs_of_prereqs)
    redundant = {code for code in requisites if code in prereqs_of_prereqs}
    if redundant:
        redundancies[course_code] = redundant

print(redundancies)

for major_code, major in major_plans.items():
    need_prereq_removal: Set[CourseCode] = set()
    for course in major.curriculum():
        parsed = parse_course_name(course.course_title)
        if parsed is not None:
            subject, number, has_lab = parsed
            if (subject, number) in redundancies:
                need_prereq_removal.add((subject, number))
            if has_lab is not None and (subject, number + has_lab) in redundancies:
                need_prereq_removal.add((subject, number + has_lab))
    if need_prereq_removal:
        display = " | ".join(
            f"{subject} {number} <- {', '.join(map( ' '.join, redundancies[subject, number]))}"
            for subject, number in need_prereq_removal
        )
        print(f"[{major_code}] {display}")