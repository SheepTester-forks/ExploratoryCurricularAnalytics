"""
Listed every unique course title (cleaned up a bit) with its parsed course code.
This was to test `parse_course_name` (which turns `BICD110` into `("BICD",
"110")` but not `IE1` into `("IE", "1")`) as well as `clean_course_title`.

::ca::check

python3 course_names.py > course_names.txt
"""

import re
from parse import major_plans
from university import clean_course_title, parse_course_name

course_names = {
    clean_course_title(course.course_title): f"{major_plan.major_code} {college}"
    for year in range(2015, 2023)
    for major_plan in major_plans(year).values()
    for college in major_plan.colleges
    for course in major_plan.plan(college)
}


for name in sorted(course_names):
    # Remove obvious course codes and non-course codes for brevity
    if re.search(r"\d", name) and not re.match(r"^[A-Z]{2,4} \d{1,3}[A-Z]?$", name):
        parsed = parse_course_name(name, 0)
        display = str(parsed[0][0]) if parsed[0][0] else ""
        print(f"[{course_names[name]}] {name}".ljust(80) + display)
