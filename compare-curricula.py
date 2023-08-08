"""
Compares, for each major, every college's degree plan (major courses only)
against each other, and listed the differences in courses in comparisons.txt. I
found that Marshall had the least deviations overall, so Marshall's degree plans
are used to create curricula.

::ca::check

python3 compare-curricula.py
"""

import itertools
import re
from typing import List, Tuple
from parse import major_plans

colleges = ["RE", "MU", "TH", "WA", "FI", "SI", "SN"]
ignored = ["GE/DEI", "DEI/GE", "DEI"]


def difference(a: List[str], b: List[str]) -> Tuple[List[str], List[str]]:
    """
    Takes two sorted lists, which may have duplicate items, and returns tuple of
    a list of items only in `a` and items only in `b`.
    """
    a_exclusive: List[str] = []
    b_exclusive: List[str] = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
        elif a[i] < b[j]:
            a_exclusive.append(a[i])
            i += 1
        else:
            b_exclusive.append(b[j])
            j += 1
    a_exclusive += a[i:]
    b_exclusive += b[j:]
    return a_exclusive, b_exclusive


def display_set(ls: List[str]) -> str:
    """
    Represent a list like a set so the Git diff for comparisons.txt isn't all
    just changing curly braces to square brackets.
    """
    return f"{{{repr(ls)[1:-1]}}}" if ls else "set()"


oddity_scores = {college: 0 for college in colleges}
deviation_scores = {college: 0 for college in colleges}
for major_plan in major_plans(2021).values():
    try:
        curricula = {
            college: sorted(
                re.sub(
                    r"( ?/ ?(awp|dei|sixth practicum)| \(dei approved\)|\*\* ?/elective)$",
                    "",
                    course.course_title.strip(" *^").lower(),
                )
                for course in major_plan.curriculum(college)
                if course.course_title not in ignored
            )
            for college in colleges
        }
    except KeyError as e:
        print(f"= <!> Error for {major_plan.major_code} =")
        print(f"Missing academic plan for {e.args[0]} (and possibly others too)")
        print()
        continue

    local_scores = {college: 0 for college in colleges}
    header_printed = False
    for (clg1, curr1), (clg2, curr2) in itertools.combinations(curricula.items(), 2):
        if curr1 != curr2:
            if not header_printed:
                print(f"= Discrepancies for {major_plan.major_code} =")
                header_printed = True
            print(f"== {clg1} vs {clg2} ==")
            only1, only2 = difference(curr1, curr2)
            print(f"[{clg1}] {display_set(only1)}")
            print(f"[{clg2}] {display_set(only2)}")
            local_scores[clg1] += 1
            local_scores[clg2] += 1
            oddity_scores[clg1] += 1
            oddity_scores[clg2] += 1
    if header_printed:
        unique = [
            college
            for college, score in local_scores.items()
            if score == len(colleges) - 1
        ]
        if len(unique) > 0:
            print(f"Deviations: {unique}")
            for college in unique:
                deviation_scores[college] += 1
        print()

print(f"College oddity scores: {oddity_scores}")
print(f"College deviation scores: {deviation_scores}")
