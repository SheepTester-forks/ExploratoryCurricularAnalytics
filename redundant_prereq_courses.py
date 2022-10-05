from typing import Dict, List, NamedTuple, Optional, Set, Tuple
from parse import CourseCode, prereqs
from util import add_entry, merge_partition, sorted_dict


# PHYS 1B requires [MATH 10B, MATH 20B], among others. PHYS 2B requires [MATH
# 20B, MATH 20C, MATH 31BH], among others. PHYS 1C requires [PHYS 1B, PHYS 2B]
# and [MATH 10B, MATH 20B]. Is this redundant? Taking PHYS 2B does not imply you
# have credit for MATH 20B. MATH 20C implies MATH 20B, but MATH 31BH implies
# MATH 31AH, which doesn't imply anything. You could have credit for MATH 31BH
# and not meet the requirements for PHYS 1C. Is that a good thing?

# I'll just assume that *every* alternative is taken.

course_prereqs = prereqs("FA22")
course_prereqs_flat = {
    course_code: [alt.course_code for req in prereqs for alt in req]
    for course_code, prereqs in course_prereqs.items()
}


# First course in list is the earliest prereq
PrereqChain = Tuple[CourseCode, ...]


class State(NamedTuple):
    taken: Dict[CourseCode, List[PrereqChain]]
    explored: Set[CourseCode]
    nonexistent: Dict[CourseCode, List[PrereqChain]]


def take_prereq(course_code: CourseCode, target: State, satisfies: PrereqChain) -> None:
    if course_code in target.explored:
        if course_code in satisfies[-1]:
            # Warning does not get emitted
            print(f"WARNING: circular reference? {' -> '.join(map(str, satisfies))}")
        return
    target.explored.add(course_code)
    for course in course_prereqs_flat[course_code]:
        add_entry(target.taken, course, satisfies)
        if course in course_prereqs_flat:
            take_prereq(course, target, (course, *satisfies))
        else:
            add_entry(target.nonexistent, course, satisfies)


def redundant_prereqs(
    course_code: CourseCode,
    nonexistent: Optional[Dict[CourseCode, List[PrereqChain]]] = None,
) -> Dict[CourseCode, List[PrereqChain]]:
    state = State({}, set(), {})
    prereqs = course_prereqs_flat[course_code]
    for course in prereqs:
        if course in course_prereqs_flat:
            take_prereq(course, state, (course, course_code))
        else:
            add_entry(state.nonexistent, course, (course_code,))
    if nonexistent is not None:
        merge_partition(nonexistent, state.nonexistent)
    return {course: state.taken[course] for course in prereqs if course in state.taken}


def main() -> None:
    nonexistent: Dict[CourseCode, List[PrereqChain]] = {}
    for course in sorted(course_prereqs_flat.keys()):
        redundant = redundant_prereqs(course, nonexistent)
        if not redundant:
            continue
        print(f"[{course}]")
        for course, chains in sorted_dict(redundant):
            display_chains = ", ".join(
                " → ".join(str(course) for course in chain) for chain in chains
            )
            print(
                f"Has redundant prereq {course}, which was already taken for {display_chains}"
            )
    print("[Nonexistent courses]")
    for course, chains in sorted_dict(nonexistent):
        display_chains = ", ".join(
            map(str, sorted({satisfies for satisfies, *_ in chains}))
        )
        print(f"Nonexistent {course} required by {display_chains}")
    print("[Nonexistent prereqs]")
    for course_code, reqs in sorted_dict(course_prereqs):
        for req in reqs:
            if len(req) == 1 and req[0].course_code not in course_prereqs:
                print(
                    f"{course_code} strictly requires nonexistent {req[0].course_code}"
                )


if __name__ == "__main__":
    main()