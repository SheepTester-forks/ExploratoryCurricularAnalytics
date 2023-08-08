"""
Checks every major uploaded onto Curricular Analytics. For some reason, if
curricula are uploaded too quickly to Curricular Analytics, they end up with
blank degree plans. This happened for curricula uploaded earlier before I
realized I set the delay time too short.

::ca::upload

python3 check_uploaded.py
"""

import os

from dotenv import load_dotenv  # type: ignore
from api import Session
from upload import track_uploaded_curricula

load_dotenv()
ca_session = os.getenv("CA_SESSION")
if ca_session is None:
    raise EnvironmentError("No CA_SESSION environment variable")
session = Session(ca_session)
with track_uploaded_curricula(2021) as curricula:
    for major_code in (
        "BI34",
        "CR25",
        "CH25",
        "CH34",
        "CH36",
        "CH38",
        "CG25",
        "CG33",
        "CG34",
        "CG35",
        "CS25",
        "AN26",
        "MC25",
    ):
        curriculum_id = curricula[major_code]
        curriculum = session.get_curriculum(curriculum_id)
        if not curriculum["courses"]:
            print(f"{major_code} empty")
        else:
            print(f"{major_code}\r", end="")
        for name, plan_id in session.get_degree_plans(curriculum_id).items():
            degree_plan = session.get_degree_plan(plan_id)
            if len(degree_plan["terms"]) != 12:
                print(f'{major_code} {name} has {len(degree_plan["terms"])} quarters')
