"""
Identifies common prereqs across all courses in a subject. This was to figure
out if there were any exceptions other than the provided `SOCI- UD METHODOLOGY`
and `TDHD XXX`.

::ca::check

python3 common_prereqs.py
"""

from typing import Dict, Tuple
from parse import prereqs
from parse_defs import CourseCode

THRESHOLD = 0.5


def parse_int(string: str) -> Tuple[int, str]:
    """
    Like JavaScript `parseInt`, where non-digits after the integer are ignored.
    """
    for i, char in enumerate(string):
        if not char.isdigit():
            index = i
            break
    else:
        index = len(string)
    # Return 1000 so WARR CULTD gets put after all numbers
    return int(string[0:index]) if index > 0 else 1000, string[index:]


def main() -> None:
    course_codes = set(prereqs("FA21").keys()) | {
        prerequisite.course_code
        for requirements in prereqs("FA21").values()
        for alternatives in requirements
        for prerequisite in alternatives
    }
    subjects = sorted({subject for subject, _ in course_codes})

    for subject in subjects:
        numbers = [number for subj, number in course_codes if subj == subject]
        upper_division = [
            number for number in numbers if parse_int(number)[0] // 100 == 1
        ]

        for name, numbers in (subject, numbers), (f"{subject} UD", upper_division):
            if len(numbers) <= 1:
                continue
            prereq_freq: Dict[CourseCode, int] = {}
            for number in numbers:
                code = subject, number
                if code in prereqs("FA21"):
                    for alternatives in prereqs("FA21")[code]:
                        for prereq_code, _ in alternatives:
                            if prereq_code not in prereq_freq:
                                prereq_freq[prereq_code] = 0
                            prereq_freq[prereq_code] += 1
            results = [
                f"{subject} {number} {count}x"
                for (subject, number), count in sorted(
                    prereq_freq.items(), key=lambda entry: entry[1], reverse=True
                )
                if count / len(numbers) > THRESHOLD
            ]
            print(f"[{name}] {len(numbers)}. {', '.join(results)}")


if __name__ == "__main__":
    main()
