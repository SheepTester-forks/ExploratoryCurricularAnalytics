"""
Loads department codes and names from a JSON file saved from plans.ucsd.edu:
https://plans.ucsd.edu/controller.php?action=LoadSearchControls

departments.txt was created by department_names.py, not departments.py.

Exports:
    `departments`, a dictionary mapping from department codes to their names.

    `dept_schools`, a dictionary mapping from department codes to the name of
    the school they're part of.

::ca::data

python3 departments.py
"""

import json
from typing import Dict, List

__all__ = ["departments", "dept_schools"]


departments: Dict[str, str] = {}
with open("./files/LoadSearchControls.json") as controls:
    for department in json.load(controls)["departments"]:
        departments[department["code"]] = department["name"]
# Add old department names
# https://registrar.ucsd.edu/catalog/15-16/curric/JUDA-ug.html
departments["JUDA"] = "Jewish Studies Program"
# https://registrar.ucsd.edu/catalog/15-16/curric/TWS.html
departments["TWS"] = "Third World Studies Program"
# https://registrar.ucsd.edu/catalog/15-16/curric/FPM-ug.html
departments["FPMU"] = "Undergraduate Program in Public Health"
# https://registrar.ucsd.edu/catalog/15-16/curric/HDP.html
departments["HDP"] = "Human Development Program"

# List of school names: https://evc.ucsd.edu/about/Divisions%20and%20Schools.html
_schools: Dict[str, List[str]] = {
    # https://artsandhumanities.ucsd.edu/academics/departments-programs.html
    "School of Arts & Humanities": [
        "HIST",
        "LIT",
        "MUS",
        "PHIL",
        "THEA",
        "VIS",
        "AAS",
        "CHIN",
        "CLAS",
        "GMST",
        "GSS",
        "ITAL",
        "JAPN",
        "JWSP",
        "RUSS",
        # https://religion.ucsd.edu/undergraduate/index.html
        # Study of Religion seems to be led by professors of the Department of
        # Literature, but its membership of the School or Department aren't
        # stated explicitly
        "RELI",
        # Judaic Studies, now Jewish Studies (JWSP) http://judaicstudies.ucsd.edu/
        "JUDA",
        # Third World Studies, now Global South Studies (GSS)
        "TWS",
    ],
    # https://biology.ucsd.edu/education/undergrad/maj-min/majors/fall20-later/index.html
    "School of Biological Sciences": ["BIOL"],
    # https://isp.ucsd.edu/programs/bachelor-arts/index.html ?
    "School of Global Policy & Strategy": ["INTL"],
    # https://jacobsschool.ucsd.edu/ navbar
    # https://jacobsschool.ucsd.edu/prospective-students/undergraduate-majors
    "Jacobs School of Engineering": ["BENG", "CSE", "ECE", "MAE", "NENG", "CENG", "SE"],
    # https://physicalsciences.ucsd.edu/academics/index.html
    "School of Physical Sciences": ["CHEM", "MATH", "PHYS"],
    # https://rady.ucsd.edu/programs/undergraduate/index.html ?
    "Rady School of Management": [],
    # https://socialsciences.ucsd.edu/programs/index.html
    "School of Social Sciences": [
        "ANTH",
        "COGS",
        "COMM",
        "CGS",
        "ECON",
        "EDS",
        "ETHN",
        "GLBH",
        "HDS",
        "LATI",
        "LING",
        "POLI",
        "PSYC",
        "SOC",
        "USP",
    ],
    # https://datascience.ucsd.edu/academics/undergraduate/
    "Halıcıoğlu Data Science Institute": ["DSC"],
    # Not listed as a school
    # https://scripps.ucsd.edu/esys
    "Scripps Institution of Oceanography": ["SIO", "ESYS"],
}
dept_schools: Dict[str, str] = {}
for school, depts in _schools.items():
    for department in depts:
        dept_schools[department] = school

if __name__ == "__main__":
    for code, name in departments.items():
        if code not in dept_schools:
            print(f"{code}: {name}")
    # print(" ".join(departments.keys()))
