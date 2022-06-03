from typing import Set
import parse


def dei_issue(list1: Set[parse.PlannedCourse], list2: Set[parse.PlannedCourse]) -> bool:
    its_a_dei_thing = False
    if (len(list1) - len(list2) == 1):
        for course in list1:
            if course.course_code == "GE/DEI" or course.course_code == "DEI/GE":
                list1.remove(course)
                break
        its_a_dei_thing = set_cmp(list1, list2)
    elif (len(list1)-len(list2) == -1):
        for course in list2:
            if course.course_code == "GE/DEI" or course.course_code == "DEI/GE":
                list2.remove(course)
                break
        its_a_dei_thing = set_cmp(list1, list2)
    return its_a_dei_thing


def course_cmp(course1: parse.PlannedCourse, course2: parse.PlannedCourse) -> bool:
    return (course1.course_code == course2.course_code) and (course1.units == course2.units) and (course1.type == course2.type)


def set_cmp(list1: Set[parse.PlannedCourse], list2: Set[parse.PlannedCourse]) -> bool:
    check = True
    m_match = False
    for m in list1:
        m_match = False
        for n in list2:
            if (course_cmp(m, n)):
                m_match = True
                break
        check = check and m_match
    return check


for major in parse.major_plans.values():

    print(f'Testing {major.major_code}')
    if (major.major_code == "PS33"):
        print("PS33 is weird, leave it alone")
        continue
    if(major.major_code == "UN27" or major.major_code == "UNHA" or major.major_code == "UNPS" or major.major_code == "UNSS"):
        print("Undeclared is weird, leave it alone")
        continue

    temp_curr_RE = major.curriculum("RE")
    temp_curr_MU = major.curriculum("MU")
    temp_curr_FI = major.curriculum("FI")
    temp_curr_SI = major.curriculum("SI")
    temp_curr_SN = major.curriculum("SN")
    temp_curr_TH = major.curriculum("TH")
    temp_curr_WA = major.curriculum("WA")

    RE_repr = repr(temp_curr_RE)
    MU_repr = repr(temp_curr_MU)
    FI_repr = repr(temp_curr_FI)
    SI_repr = repr(temp_curr_SI)
    SN_repr = repr(temp_curr_SN)
    TH_repr = repr(temp_curr_TH)
    WA_repr = repr(temp_curr_WA)

    degree_plans = [temp_curr_RE, temp_curr_MU, temp_curr_FI,
                    temp_curr_SI, temp_curr_SN, temp_curr_TH, temp_curr_WA]
    reprs = [RE_repr, MU_repr, FI_repr, SI_repr, SN_repr, TH_repr, WA_repr]
    colleges = ["RE", "MU", "FI", "SI", "SN", "TH", "WA"]

    for x in range(7):
        for y in range(x+1, 7):
            # print(f'Testing colleges {colleges[x]}, vs {colleges[y]}')
            eq = reprs[x] == reprs[y]
            if(not eq):
                # print(f'Colleges {colleges[x]} and {colleges[y]} don\'t match')
                quarter_eq = str(degree_plans[x]) == str(
                    degree_plans[y])
                if (not quarter_eq):
                    # Check the quarter sizes are the same
                    if (len(degree_plans[x]) != len(degree_plans[y])):
                        dei = False
                        dei = dei_issue(
                            degree_plans[x], degree_plans[y])
                        if (not dei):
                            print(
                                f'Colleges {colleges[x]} and {colleges[y]} don\'t match. They\'re different length')
                            print(
                                f'College {colleges[x]}: {degree_plans[x]}')
                            print(
                                f'College {colleges[y]}: {degree_plans[y]}')
                    else:
                        list1 = degree_plans[x]
                        list2 = degree_plans[y]
                        if ((not set_cmp(list1, list2)) and (not set_cmp(list2, list1))):
                            dei = False
                            dei = dei_issue(
                                degree_plans[x], degree_plans[y])
                            if (not dei):
                                print(
                                    f'Colleges {colleges[x]} and {colleges[y]} don\'t match.')
                                print(
                                    f'College {colleges[x]}: {degree_plans[x]}')
                                print(
                                    f'College {colleges[y]}: {degree_plans[y]}')
