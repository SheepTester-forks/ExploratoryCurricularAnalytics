from typing import List
import parse


def course_cmp(course1: parse.PlannedCourse, course2: parse.PlannedCourse) -> bool:
    return (course1.course == course2.course) and (course1.units == course2.units) and (course1.type == course2.type)


def set_cmp(list1: List[parse.PlannedCourse], list2: List[parse.PlannedCourse]) -> bool:
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


for major in parse.majors:

    print(f'Testing {major.major}')
    if (major.major == "PS33"):
        print("PS33 is weird, leave it alone")
        continue
    if(major.major == "UN27" or major.major == "UNHA" or major.major == "UNPS" or major.major == "UNSS"):
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
            #print(f'Testing colleges {colleges[x]}, vs {colleges[y]}')
            eq = reprs[x] == reprs[y]
            if(not eq):
                #print(f'Colleges {colleges[x]} and {colleges[y]} don\'t match')
                for z in range(12):
                    quarter_eq = str(degree_plans[x].quarters[z]) == str(
                        degree_plans[y].quarters[z])
                    if (not quarter_eq):
                        # Check the quarter sizes are the same
                        if (len(degree_plans[x].quarters[z]) != len(degree_plans[y].quarters[z])):
                            print(
                                f'Colleges {colleges[x]} and {colleges[y]} don\'t match in quarter {z+1}. They\'re different length')
                            print(
                                f'College {colleges[x]}: {degree_plans[x].quarters[z]}')
                            print(
                                f'College {colleges[y]}: {degree_plans[y].quarters[z]}')
                        else:
                            list1 = degree_plans[x].quarters[z]
                            list2 = degree_plans[y].quarters[z]
                            if ((not set_cmp(list1, list2)) and (not set_cmp(list2, list1))):

                                print(
                                    f'Colleges {colleges[x]} and {colleges[y]} don\'t match in quarter {z+1}.')
                                print(
                                    f'College {colleges[x]}: {degree_plans[x].quarters[z]}')
                                print(
                                    f'College {colleges[y]}: {degree_plans[y].quarters[z]}')
