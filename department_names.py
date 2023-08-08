"""
Compares the list of unique department codes of the degree plans available with the department codes from the ISIS major code spreadsheet. This is to figure out which department names I don't need to get the name for.

::ca::check

python3 department_names.py
"""

from parse import major_codes, major_plans


from_plans = sorted(set(major.department for major in major_plans(2021).values()))
from_codes = sorted(set(major.department for major in major_codes().values()))

print("PLANS CODES")
i = 0
j = 0
while i < len(from_plans) and j < len(from_codes):
    if from_plans[i] == from_codes[j]:
        department = from_plans[i] or "_"
        # https://stackoverflow.com/a/5676884
        print(f"{department: <5} {department: <5}")
        i += 1
        j += 1
    elif from_plans[i] < from_codes[j]:
        print(f"{from_plans[i] or '_': <5}      ")
        i += 1
    else:
        print(f"      {from_codes[j] or '_': <5}")
        j += 1
for dept in from_plans[i:]:
    print(f"{dept: <5}      ")
for dept in from_codes[j:]:
    print(f"      {dept: <5}")

# Seems that isis_major_code_list.xlsx has more departments than
# academic_plans.csv, which makes sense
print(from_plans)

codes = sorted(set(major.major_code[0:2] for major in major_plans(2021).values()))
print(codes)
