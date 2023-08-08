"""
Runs [Arturo's course name cleanup
algorithm](https://www.overleaf.com/project/62e8265ff1395d787286ea5b) on every
unique course title, and lists all resulting unique cleaned course titles. The
goal with this is to reduce variability in course titles resulting from college
advisors phrasing things differently.

This supercedes the old aggressive course title cleanup algorithm that was
tested by course_names2.py.

::ca::check

python3 course_names3.py > course_names3.txt
"""

import itertools
import re
from typing import Dict
from parse import major_plans

# https://stackoverflow.com/a/93029
control_chars = re.escape(
    "".join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0))))
)

removals = {
    # 11.
    "(ANTH 1) SOCIAL SCIENCE GE": "SOCIAL SCIENCE GE",
    "(ANTH 2) SOCIAL SCIENCE GE": "SOCIAL SCIENCE GE",
    # 12.
    '"UD ELECTIVE': "UD ELECTIVE",
    # 13.
    "MATH 11 (MATH GE SEE NOTE) / PSYC 60": "MATH 11 / PSYC 60",
    # 14.
    "MATH 10A / 20A (MATH GE SEE NOTE) / MGT 3": "MATH 10A / 20A / MGT 3",
    # 15.
    "MATH 11 (MATH GE)": "MATH 11",
    # 16.
    "TECHNICAL ELECTIVE (TE)": "TECHNICAL ELECTIVE",
    # 17.
    "ELECTIVE (2 / 4 UNITS)": "ELECTIVE",
    "ELECTIVE (2, 3 / 4 UNITS)": "ELECTIVE",
    # 18.
    "BILD 1 (GENETICS PREREQ)": "BILD 1",
    # 19.
    "LD INTRO COURSE (EG GLBH 20)": "LD INTRO COURSE",
    "LD INTRO COURSE (EG SOCI 30)": "LD INTRO COURSE",
    # 20.
    "STATISTICS (QUANTITATIVE METHODS)": "STATISTICS",
    # 21.
    "BENG DE COURSE (ASSIGNED)": "BENG DE COURSE",
    # 22.
    "MAJOR CLASSES / ELECTIVES (VARIES)": "MAJOR CLASSES / ELECTIVES",
    "MAJOR CLASSES AND ELECTIVES (VARIES)": "MAJOR CLASSES AND ELECTIVES",
    # 23.
    "COGS 14B / PSYC 60 (STATS REQUIREMENT)": "COGS 14B / PSYC 60",
    # 26.
    "PHIL 10 (MATH GE)": "PHIL 10",
    # 27.
    "MATH 10A / 20A (NATURAL SCIENCE MAJOR)": "MATH 10A / 20A",
    "MATH 10B / 20B (NATURAL SCIENCE MAJOR)": "MATH 10B / 20B",
    # 28.
    "SOCIAL SCIENCE (REVELLE)": "SOCIAL SCIENCE",
    # 29.
    "CSE ELECTIVE (CSE 197)": "CSE ELECTIVE",
    # 30.
    "CENG 1 (OR CENG 4)": "CENG 1 / CENG 4",
    # 31.
    "ELECTIVE (UD)": "ELECTIVE UD",
    # 32.
    "ECE 111 (OR ECE 140B)": "ECE 111 / ECE 140B",
    # 33.
    "CSE 141 (OR CSE 142)": "CSE 141 / CSE 142",
    "CSE 141L (OR CSE 142L)": "CSE 141L / CSE 142L",
}


def clean_course_name(name: str) -> str:
    # 1. Strip *, ^, ~, #, +, non-ASCII, and <I> and </I> from the names
    name = re.sub(r"[*^~.#+=¹%s]+|<..?>" % control_chars, "", name)

    # 2. Strip trailing and leading spaces
    name = name.strip()

    # 3. Strip mentions of a writing requirement preceded by a "/"
    name = re.sub(r"\s*/\s*(AWPE?|A?ELWR|SDCC)", "", name)

    # 4. Turn everything uppercase
    name = name.upper()

    # 5. Turn ORs into / and standardize spacing around "/"
    name = re.sub(r"\s+OR\s+|\s*/\s*", " / ", name)

    # 6. Fix spacing on all "-"
    name = re.sub(r"-+", " - ", name)

    # 7. Standardize spacing
    name = re.sub(r" +", " ", name)

    # 8. Remove parenthesis containing GE SEE NOTE, NOTE, FOR, SEE, REQUIRES, or
    #    (ONLY) OFFERED
    name = re.sub(r" ?\( ?(GE SEE|NOTE|FOR|SEE|REQUIRES|ONLY|OFFERED)[^)]*\)", "", name)

    # 9. Remove unnecessary digits at the start of a course name
    name = re.sub(r"^\d+ ", "", name)

    # 10. Replace Elect and elec for Elective
    name = re.sub(r"ELECT?\b", "ELECTIVE", name)

    # Removals
    if name in removals:
        name = removals[name]

    # 24. Remove the (VIS) tag
    name = name.replace(" (VIS)", "")

    # 25. Remove the () around the numbered elective in NE ELECTIVE #
    if name.startswith("NE ELECTIVE "):
        name = re.sub(r"[()]", "", name)

    # 34. Complete incomplete words
    name = re.sub(r"TECH\b", "TECHNICAL", name)
    name = re.sub(r"REQUIRE\b", "REQUIREMENT", name)
    name = re.sub(r"BIO\b", "BIOLOGY", name)
    name = re.sub(r"BIOPHYS\b", "BIOPHYSICS", name)

    return name


mergers = [
    ["4th MATH", "4th MATH BS"],
    [
        "ADVANCED ART MAKING",
        "ADVANCED ART MAKING UD",
        # "ADVANCED ART MAKING  UD",
        "UD ADVANCED ART MAKING",
    ],
    [
        "ADVANCED ELECTIVE UD",
        "ADVANCED ELECTIVE",
        "UD ADVANCE ELECTIVE",
        # "UD ADVANCED ELECTIVE ",
        "UD ADVANCED ELECTIVE",
    ],
    [
        "ADVANCED INTERDISCIPLINARY",
        "ADVANCED INTERDISCIPLINARY UD",
        # "ADVANCED INTERDISCIPLINARY  UD",
        "ADVANCED LEVEL: INTERDISCIPLINARY",
        "UD AVANCED INTERDISCIPLINARY",
    ],
    ["ADVANCED LEVEL: ELECTIVE", "ADVANCED LEVEL: ELECTIVE ", "ADVANCED LEVEL: UD"],
    [
        "ADVANCED LEVEL: SEMINAR",
        "ADVANCED LEVEL: SEMINAR ",
        "ADVANCED LEVEL: SEMINAR UD",
        "UD ADVANCED SEMINAR",
        "ADVANCED SEMINAR",
        # "UD ADVANCED SEMINAR",
    ],
    [
        "ADVANCED LEVEL: THEORY",
        "ADVANCED LEVEL: THEORY ",
        "ADVANCED LEVEL: THEORY UD",
        "ADVANCED THEORY",
        "UD ADVANCED THEORY",
    ],
    ["AHI / SOCIAL SCIENCE GE", "AHI AND SOCIAL SCIENCE GE"],
    ["ANBI CONCENTRATION COURSE", "ANBI CONC ELECTIVE", "ANBI UPPER DIVISION COURSE"],
    ["ANSC 148", "ANSC 148 GLOBAL HEALTH & CULTURAL DIVERSITY"],
    ["ANTH 101", "ANTH 101: FOUNDATIONS OF SOCIAL COMPLEXITY"],
    [
        "ANTH 102",
        "ANTH 102: HUMAN ARE CULTURAL ANIMALS",
        "ANTH 102: HUMAN ARE CULTURED ANIMALS",
    ],
    ["ANTH 103", "ANTH 103: SOCIOCULTURAL ANTHRO"],
    [
        "ANTH 43 / 42, 5 / SOCI 70 / PSYC 1",
        "ANTH 5 / ANTH 42 / ANTH 43 / SOCI 70 / PSYC 1",
    ],
    ["ANSC CONC ELECTIVE", "ANTHROPOLOGY  ANSC CONCENTRATION COURSE"],
    [
        "ANTH UD ELECTIVE",
        "ANTHROPOLOGY UD ELECTIVE",
        "ANTHROPOLOGY UD ELECTIVE COURSE",
        "UD ANTH ELECTIVE COURSE",
    ],
    ["AWP / GE", "GE"],
    ["BENG DE", "BENG DE COURSE"],
    ["BIBC 100 / 102", "BIB 100 / BIBC 102"],
    ["BIBC 102 / CHEM 114B", "BIBC102 / CHEM114B"],
    ["BICD 110", "BICD110"],
    ["BILD 7 / 10", "BILD 10 / 7"],
    ["BIMM 100 / CHEM 114C", "BIMM100 / CHEM114C"],
    [
        "BIO UD ELECTIVE",
        "UD BIO ELECTIVE",
        # "BIO ELECTIVE",
        # "UD BIO ELECTIVE",
    ],
    ["BIOPHYS ELECTIVE", "BIOPHYSICS ELECTIVE"],
    ["BILD 3, 7 / 10", "BIOLOGY 3, 7, / 10"],
    [
        "CAT125 / PRACTICUM",
        "CAT 125 / PRACTICUM",
        "CAT 125 / SIXTH COLLEGE PRACTICUM",
        "PRAC / CAT 125",
        "PRACTICUM / CAT 125",
    ],
    ["CGS 2A (DEI)", "CGS 2A / DEI"],
    ["CGS UD COURSE", "CGS UD ELECTIVE"],
    ["CHEM 126 / 127", "CHEM 127 / 126"],
    ["CHEM 167 / 168", "CHEM 168 / 167"],
    ["CHEM 7L / CHEM 7LM", "CHEM 7LM / CHEM 7L"],
    ["CHEM6A", "CHEM 6A"],
    ["CHEM RE", "CHEM RESTRICTED ELECTIVE", "CHEMRES ELECTIVE"],
    ["CHEM GE", "CHEMISTRY GE"],
    [
        "COGS / PYSC UD ELECTIVE",
        "ADDITIONAL PSYCHOLOGY / COGNITIVE SCIENCE ELECTIVE",
        "ADDITIONAL UD COGS / PSYC ELECTIVE",
    ],
    [
        "COGS 101A / 101B / 101C",
        "COGS 101A / 101B / 1001C",
        "COGS (101A / 101B / 101C)",
    ],
    ["COGS 14B / PSYC 60 ", "COGS 14B / PYSC 60"],
    [
        "COGS CORE (BA) / COGS 100 (BS)",
        "COGS CORE / COGS 100 (BS)",
        "CORE / COGS 100 (BS)",
    ],
    [
        "COGS CORE (BA) / COGS 108 (BS)",
        "COGS CORE / COGS 108 (BS)",
        "CORE / COGS 108 (BS)",
    ],
    ["COGS 107A", "COGS CORE 107A"],
    ["COMM 10 (DEI APPROVED)", "COMM 10 (DEI)", "COMM 10 / DEI", "COMM 10"],
    ["COGS CORE", "CORE"],
    ["COMM INTERMEDIATE / ADVANCED ELECTIVE", "COMM INTERMEDIATE / ADV ELECTIVE"],
    ["CSE / ECE ELECTIVE", "CSE / ECE ELECTIVE (REPLACE ECE 108)"],
    ["CSE ELECTIVE", "CSE ELECTIVE (OR TECHNICAL ELECTIVE)"],
    ["CSE LD ELECTIVE", "CSE LOWER DIV ELECTIVE", "CSE LOWER DIVISION ELECTIVE"],
    ["DEI", "DEI / GE"],
    ["DEI / SOCIAL SCIENCE", "DEI / SOCIAL SCIENCE GE"],
    # Most of the DF section, but I'm not sure about that one
    ["DOC 1", "DOC 1 / DEI", "DOC1 / DEI"],
    ["EDS 139", "EDS 139 (DEI)"],
    ["EDS UD", "EDS UD ELECTIVE"],
    [
        "ELCETIVE",
        "ELECTIVE",
        # 'ELECTIVE (2 / 4 UNITS)',
        # 'ELECTIVE (BA)',
        # 'ELECTIVE / FRESHMAN SEMINAR',
        # 'ELECTIVE / QFS'
    ],
    # ELECTIVE 1, 2, 3, 4, 5 and ELECTIVE I, II, III, IV, V
    [
        "ELECTIVE 1",
        "ELECTIVE I",
        "ELECTIVE 2",
        "ELECTIVE II",
        "ELECTIVE 3",
        "ELECTIVE III",
        "ELECTIVE 4",
        "ELECTIVE IV",
        "ELECTIVE 5",
        "ELECTIVE V",
    ],
    ["ENG DESIGN", "ENGINEERING DESIGN"],
    [
        "ESYS ELECTIVE",
        "ESYS MAJOR ELECTIVE",
        # 'ESYS EBE LAB',
        # 'ESYS MAJOR LAB',
        # 'ESYS MAJOR LAB ELECTIVE',
        # 'ESYS MAJOR RESTRICTED ELECTIVE',
    ],
    ["ETHN 1", "ETHN 1 (DEI)", "ETHN 1 / DEI"],
    ["FINE ARTS", "FINE ARTS GE"],
    ["FOUNDATION LEVEL: ART MAKING ", "FOUNDATION LEVEL: ART MAKING"],
    [
        "FOUNDATION LEVEL: HISTORY",
        "FOUNDATION LEVEL: HISTORY ",
        "FOUNDATION LEVEL: HISTORY VIS 84",
    ],
    ["GE ALTERNATIVE", "ALTERNATIVE, GE ALTERNATIVE / DEI"],
    # GH ELECTIVE 1, 2, 3, 4, 5, 6, 7, 8 AND GLBH ELECTIVE 1, 2, 3, 4, 5, 6, 7, 8 AND GLBHELECTIVE 5
    [
        "GH ELECTIVE 1",
        "GLBH ELECTIVE 1",
        "GH ELECTIVE 2",
        "GLBH ELECTIVE 2",
        "GH ELECTIVE 3",
        "GLBH ELECTIVE 3",
        "GH ELECTIVE 4",
        "GLBH ELECTIVE 4",
        "GH ELECTIVE 5",
        "GLBH ELECTIVE 5",
        "GLBHELECTIVE 5",
        "GH ELECTIVE 6",
        "GLBH ELECTIVE 6",
        "GH ELECTIVE 7",
        "GLBH ELECTIVE 7",
        "GH ELECTIVE 8",
        "GLBH ELECTIVE 8",
    ],
    ["GLBH 150A", "GLBH 150A SENIOR CAPSTONE"],
    ["GLBH 150B", "GLBH 150B SENIOR CAPSTONE"],
    ["GLBH 181", "GLBH 181 ESSENTIALS OF GLOBAL HEALTH"],
    ["GROUP II", "GROUP II (A-F)"],
    ["HDP 194A", "HDP 194A / / ELECTIVE", "HDP 194A / ELECTIVE"],
    ["HDP 194B", "HDP 194B / / ELECTIVE", "HDP 194B / ELECTIVE"],
    ["HDP 194C", "HDP 194C / / ELECTIVE", "HDP 194C / ELECTIVE"],
    ["HDS DEVELOPMENTCOURSE", "HDS DEVELOPMENT COURSE"],
    # ["HDS AGING PRACTICUM", "HDS AGING SPECIALIZATION"],
    # ["HDS E&D PRACTICUM", "HDS E&D SPECIALIZATION"],
    ["HIGH-IMPACT", "HIGH IMPACT"],
    [
        "HISTORY AND THEORY",
        "HISTORY AND THEORY UD",
        "UD HISTORY & THEORY",
        "UD THEORY & HISTORY",
        "UD THEORY & HISTORY ELECTIVE",
    ],
    # ["HISTORY ELECTIVE", "HISTORY ELECTIVE UD"],
    ["HONORS METHOD / / ELECTIVE"],
    [
        "IE / RR - 1",
        "IE / RR1 - INTERDISCIPLINARY ELECTIVE / REGIONAL REQUIREMENT",
        "IE 1 - INTERDISC ELECTIVE",
        "IE1 - INTERDISC ELECTIVE (RR1)",
    ],
    [
        "INTERMEDIATE ART MAKING",
        # "INTERMEDIATE ART MAKING  UD",
        "INTERMEDIATE ART MAKING UD",
        "INTERMEDIATE LEVEL: ART MAKING",
        "UD INTERMEDIATE ART MAKING",
    ],
    [
        "INTERMEDIATE EMPHASIS",
        "INTERMEDIATE EMPHASIS UD",
        "INTERMEDIATE LEVEL: EMPHASIS",
    ],
    [
        "INTERMEDIATE GROUP A",
        "INTERMEDIATE GROUP A UD",
        "INTERMEDIATE: GROUP A",
        "UD INTERMEDIATE GROUP A",
    ],
    [
        "INTERMEDIATE GROUP B",
        "INTERMEDIATE GROUP B UD",
        "INTERMEDIATE: GROUP B",
        "UD INTERMEDIATE GROUP B",
    ],
    [
        "INTERMEDIATE INTERDISCIPLINARY",
        # "INTERMEDIATE INTERDISCIPLINARY  UD",
        "INTERMEDIATE INTERDISCIPLINARY UD",
        "INTERMEDIATE LEVEL: INTERDISCIPLINARY, INTERMEDIATE: INTERDISCIPLINARY",
        "UD INTERMEDIATE INTERDISCIPLINARY",
    ],
    ["LANGUAGE", "LANGUAGE COURSE"],
    ["LATI 10", "LATI 10 / DEI"],
    ["LATI CORE", "LATI CORE COURSE"],
    ["LATI METHOD", "LATI METHODS"],
    # [
    #     "LATI UD ELECTIVE",
    #     "LATI UG ELECTIVE",
    #     "LATI UG ELECTIVE (CON IN MEXICO)",
    #     "LATI UG ELECTIVE (CON IN MIG&BORDER)",
    # ],
    ["LD BIO SCI", "LD BIOLOGY"],
    ["LD CORE COURSE", "LD CORE COURSE / DEI"],
    ["LD LANG", "LD LANGUAGE", "LD LANUGAGE / LANGUAGE PROFICIENCY"],
    ["LD LIT", "LD LIT ELECTIVE"],
    # ["LD LTEN", "LD LTEN / GSS", "LD LTEN / TWS"],
    ["LD RESTRICTED ELECTIVE", "LD RESTRICTIVE ELECTIVE"],
    ["LD SOC COURSE", "LD SOC SCI"],
    ["LD SOCIAL & BEHAVIORAL SCI", "LD SOCIAL & BEHAVIORAL SCIENCE"],
    ["LEARNING / VISION / GRAPHICS", "LEARNING VISION GRAPHICS"],
    [
        "LIGN ELECTIVE",
        "LIGN ELECTIVE / OTHER",
        "LIGN ELECTIVE FROM LIST",
        "LING ELECTIVE",
    ],
    ["LTEN 27, 28, / 29", "LTEN 27, 28, / 29 (DEI)", "LTEN 27, 28, / 29 / DEI"],
    ["LTEN 29 / DEI / TWS 22", "LTEN 29 / TWS 22"],
    ["LTGM ELECTIVE", "LTGM UD ELECTIVE"],
    ["MAE 131 B / MAE 160", "MAE 160 / MAE 131B"],
    ["MAE170", "MAE 170"],
    ["MAJOR CLASSES / ELECTIVES", "MAJOR CLASSES AND ELECTIVES"],
    # MAJOR ELECTIVE 1,2,3,4,5 and MAJOR ELECTIVE I,II,III,IV,V and MAJOR UD ELECTIVE 1,2,3,4,5 and MAJOR ELECTIVE
    [
        "MAJOR ELECTIVE 1",
        "MAJOR ELECTIVE I",
        "MAJOR UD ELECTIVE 1",
        "MAJOR ELECTIVE 2",
        "MAJOR ELECTIVE II",
        "MAJOR UD ELECTIVE 2",
        "MAJOR ELECTIVE 3",
        "MAJOR ELECTIVE III",
        "MAJOR UD ELECTIVE 3",
        "MAJOR ELECTIVE 4",
        "MAJOR ELECTIVE IV",
        "MAJOR UD ELECTIVE 4",
        "MAJOR ELECTIVE 5",
        "MAJOR ELECTIVE V",
        "MAJOR UD ELECTIVE 5",
        "MAJOR ELECTIVE",
    ],
    ["MARINE BIOLOGY ELECTIVE", "MARINE BIO ELECTIVE"],
    [
        "MATH 10A (OR 20A)",
        "MATH 10A / 20A",
        "MATH 10A / MATH 20A",
        "MATH 20A (OR 10A)",
        "MATH 20A / 10A",
    ],
    [
        "MATH 10B (OR 20B)",
        "MATH 10B / 20A",
        "MATH 10B / 20B",
        "MATH 10B / MATH 20B",
        "MATH 20B (OR 10B)",
        "MATH 20B / 10B",
    ],
    [
        "MATH 10C / 20C",
        "MATH 10 / 20C",
        "MATH 10C IF CHOOSING MATH 10 SERIES",
        "MATH 10C IF CHOOSING THE 10 SERIES",
        "MATH 20C (OR 10C)",
        "MATH 20C / 10C",
        "IF MATH 10 SERIES THEN MATH 10C",
    ],
    # ["MATH 10C / 20C / 11", "MATH 10C / 20C / 11 (MATH GE)"],
    ["MATH 11 / PSYC 60", "MATH 11 FOR PSYC 60", "PSYC 60 / MATH 11"],
    ["MATH GE/ 10C", "MATH 10C / MATH GE"],
    [
        "MATH 18 (BS / BA - MATH 20 SERIES)",
        "MATH 18 (BS / BA MATH 20 SERIES)",
        "MATH 18 (BS)",
    ],
    ["MATH 189", "MATH 189 (IF NOT YET COMPLETED)"],
    ["MATH 109 / MATH 20D", "MATH 20D / MATH109"],
    # ["MCWP 40 / ELECTIVE", "MCWP 40 / GE"],
    # ["MCWP 50 / ELECTIVE", "MCWP 50 / GE"],
    ["MEDIA ADVANCED ELECTIVE", "MEDIA ADVANCED LEVEL"],
    [
        "MGT 173 PROJECT MANAGEMENT - HEALTH SERVICES",
        "MGT 173 PROJECT MANAGEMENT: HEALTH SERVICES",
    ],
    [
        "MGT 18",
        "MGT 18 (ALSO DEI)",
        "MGT 18 (DEI APPROVED)",
        "MGT 18 (DEI)",
        "MGT 18 / DEI",
    ],
    ["MMW 14", "MMW 14 / GE", "MMW14 / GE"],
    ["MMW12", "MMW 12"],
    ["MMW 13", "MMW13"],
    ["MMW 15", "MMW15"],
    [
        "MUIR UD ELECTIVE",
        "MUIR UD ELECTIVE / DEI",
        "MUIR UDE",
        "MUIR UPPER DIV ELECTIVE",
    ],
    [
        "MUS UD ELECTIVE ",
        "MUS UD ELECTIVE 107, 110, 116 / 150",
        "MUSIC UD ELECTIVE",
        "MUSIC UD ELECTIVE 107, 110, 116 / 150",
    ],
    [
        "MUS 101A, 101B, 101C, 120A, 120B, 120C, 170, 1A / 2A, 1B, 1B / 2B, 1C / 2C, 2A, 2AK, 2B, 2BK, 2C, 2CK, 4, 43, 6",
        "MUSIC 101A, 101B, 101C, 120A, 120B, 120C, 170, 1A / 2A, 1B, 1B / 2B, 1C / 2C, 2A, 2AK, 2B, 2BK, 2C, 2CK, 4, 43, 6",
    ],
    ["MUS UD EMPHASIS", "MUSIC EMPHASIS COURSE"],
    ["MMW 11", "MWW 11"],
    ["NATURAL SCIENCE", "NATURAL SCIENCE GE", "NATURAL SCIENCE GE - SEE NOTE BELOW"],
    ["NE ELECTIVE 1", "NANO ELECTIVE 1"],
    ["NE ELECTIVE 2", "NANO ELECTIVE 2"],
    [
        "NEW MAE MATERIALS LAB (PENDING)",
        "NEW MAE MATERIALS LAB COURSE (PENDING)",
        # "NEW MAE MATERIALS COURSE (PENDING)",
    ],
    [
        "PHI / POLI 27",
        "PHIL / POL 27",
        "PHIL / POLI 27",
        "PHIL 27 / POLI 27",
        "POLI / PHIL 27",
    ],
    ["PHIL / POL 28", "PHIL / POLI 28", "PHIL / POLI28", "PHIL 28 / POLI 28"],
    ["PHYS 1A / 1AL", "PHYS 1A / AL", "PHYS 1A&1AL", "PHYS 1A&AL"],
    ["PHYS 1B / 1BL", "PHYS 1B&1BL", "PHYS 1B&BL"],
    ["PHYS 1C / 1CL", "PHYS 1C / CL", "PHYS 1C&1CL", "PHYS 1C&CL"],
    ['PHYS 2BL / 2CL / 2DL", ""PHYS 2BL", "2CL", "/ 2DL'],
    ["PHYS RE", "PHYS UD RE"],
    ["PHYSICS GE", "PHYSIC GE", "PHYSICS SCIENCE GE"],
    [
        "POLI 30",
        "POLI 30(D)",
        "POLI 30D",
        # "POLI 30D (OR EQUIVALENT STATS)",
        # "POLI 30D / PSYC 60 / SOCI 60",
    ],
    ["POLI 5(D)", "POLI 5D"],
    ["POLICY ANALYSIS", "POLICY ANALYSIS ELECTIVE"],
    ["PROGRAMMING", "PROGRAMMING COURSE"],
    [
        "PSYC 60 (OR MATH 11 / 11L IN SPRING 2016)",
        "PSYC 60 (OR MATH 11 / 11L IN SPRING)",
    ],
    [
        "RED TECHNICAL ELECTIVE",
        "RED TECHNICAL ELECTIVE UD",
        "RED UPPER DIVISION ELECTIVE",
    ],
    ["RELI 101", "RELI 101 TOOLS & METHODS"],
    ["RELI 189", "RELI 189 SEMINAR IN RELIGION"],
    ["SE9", "SE 9"],
    ["SECURITY / CRYPTOGRAPHY", "SECURITY CRYPTOGRAPHY"],
    [
        "SOC - UD CONCENTRATION",
        "SOC UD CONCENTRATION",
        "SOCI - UD CONCENTRATION",
        "SOCI UD CONCENTRATION",
        "SOCI UD CONCENTRATION ELECTIVE",
    ],
    ["SOCI - METHOD", "SOCI - UD METHODOLOGY", "SOCI UD METHODOLOGY"],
    [
        "SOCI 10, 20, 30, 40, / 50",
        "SOCI 10, 20, 30, 40, /50 / ELECTIVE",
        "SOCI 10, 20, 30, 40,OR50",
        "SOCI10, 20, 30, 40,OR50",
    ],
    ["SOCI UD ELECTIVE", "SOC UD ELECTIVE"],
    [
        "SOCIAL SCIENCE",
        " SOCIAL SCIENCE / DEI",
        "SOCIAL SCIENCE GE",
        "SOCIAL SCIENCE GE / DEI",
        "SOCIAL SCIENCES",
        # "SOCIAL SCI ELECTIVE",
    ],
    ["STATISTICS", "STATISTICS COURSE"],
    ["STATISTICS COURSE (MATH 11 FOR GE)", "STATISTICS COURSE (MATH 11)"],
    # SUBJECT DOMAIN 1, 2, 3 and SUBJECT DOMAIN I, II, III
    [
        "SUBJECT DOMAIN 1",
        "SUBJECT DOMAIN I",
        "SUBJECT DOMAIN 2",
        "SUBJECT DOMAIN II",
        "SUBJECT DOMAIN 3",
        "SUBJECT DOMAIN III",
    ],
    ["SYN 1", "SYNTHESIS 1"],
    ["SYN 100", "SYNTHESIS 100"],
    ["SYN 2", "SYNTHESIS 2"],
    ["TDHT XXX", "TDHT XXX / DEI"],
    ["TE", "TECHNICAL ELECTIVE"],
    # ["UD / POLITICAL THEORY", "UD POLITICAL THEORY"], (duplicate)
    ["ADVANCED MEDIA PRACTICE", "UD ADVANCED MEDIA PRACTICE"],
    [
        "UD AREA STUDIES / UD LIGN ELECTIVE",
        "UD AREA STUDIES, UD LIT, / UD LIGN ELECTIVE",
    ],
    # ["UD BIEB CORE", "UD BIEB CORE LAB", "UD BIEB LAB"],
    ["UD COLLEGE ELECTIVE", "UD GE", "UD GE / DEI"],
    ["UD CONCENTRATION COURSE", "UD CONCENTRATION ELECTIVE", "CONCENTRATION UDE"],
    ["UD CORE COURSE", "CORE COURSE"],
    ["CORE MOVEMENT", "UD CORE MOVEMENT"],
    ["UD DEI / SOCIAL SCIENCE", "UD DEI / SOCIAL SCIENCE GE"],
    ["UD GH CORE COURSE", "UD GH CORE COURSE (EG GLBH 148)"],
    ["UD HISTORY", "UD HISTORY ELECTIVE"],
    # ["UD HB CORE", "UD HB CORE (DISEASE)", "UD HB CORE (PHYSIOLOGY)"],
    ["INTERMEDIATE COMPUTING", "UD INTERMEDIATE COMPUTING"],
    ["INTERMEDIATE LECTURE", "UD INTERMEDIATE LECTURE"],
    ["INTERMEDIATE MEDIA PRACTICE", "UD INTERMEDIATE MEDIA PRACTICE"],
    ["INTERMEDIATE MEDIA STUDIES", "UD INTERMEDIATE MEDIA STUDIES"],
    ["INTERMEDIATE STUDIO", "UD INTERMEDIATE STUDIO"],
    ["UD LIT ELECTIVE", "UD LITERATURE ELECTIVE"],
    ["UD LTCS (A, B, C / D)", "UD LTCS (A, B, C, / D)"],
    ["UD MAJOR - AFRICA TOPIC", "UD MAJOR - AFRICAN THEME"],
    ["UD MAJOR - ASIA TOPIC", "UD MAJOR - ASIAN THEME"],
    ["UD MAJOR - ELECTIVE", "UD MAJOR ELECTIVE"],
    ["UD MAJOR - LATIN AMERICA TOPIC", "UD MAJOR - LATINE AMERICAN THEME"],
    ["MUSIC EMPHASIS COURSE", "UD MUSIC EMPHASIS COURSE"],
    ["PHYS ELECTIVE", "UD PHYS ELECTIVE"],
    ["UD POLI - AMERICAN POLITICS", "UD POLI / AMERICAN POLITICS"],
    ["UD / POLITICAL THEORY", "UD POLITICAL THEORY"],
    ["UD PRE - 1900 LTSP", "UD LTSP - PRE - 1900"],
    ["UD PSYC ELECTIVE", "PSYC UD ELECTIVE"],
    ["UD PSYC RESEARCH LAB", "PSYC UD RESEARCH"],
    ["UD SENIOR INTERDISCIPLINARY", "SENIOR INTERDISCIPLINARY"],
    ["UD SENIOR MEDIA PRACTICE", "SENIOR MEDIA PRACTICE"],
    [
        "UD SOCIAL SCIENCE",
        "UD SOCIAL SCIENCE (MAJOR)",
        "UD SOCIAL SCIENCE / DEI",
        "UD SOCIAL SCIENCE / UD ELECTIVE",
        "UD SOCIAL SCIENCE / GE",
        "UD SOCIAL SCIENCES (MAJOR)",
    ],
    ["UDE", "UPPER DIV ELECTIVE", "UPPER DIVISION ELECTIVE", "UPPER DIVISIONELECTIVE"],
    ["USP 1 (DEI)", "USP 1", "USP 1 / DEI"],
    ["USP 3 (ALSO DEI)", "USP 3 (DEI)", "USP 3 / DEI", "USP 3"],
    ["USP 186 / PRACTICUM", "USP 186 / SIXTH PRACTICUM"],
    ["USP FD", "USP FOUNDATION", "USP FOUNDATION COURSE"],
    ["USP RESEARCH METHODS", "USP RESEARCH METHODS COURSE"],
    ["USP TECHNICAL ELECTIVE", "USP TECHNICAL ELECTIVE COURSE"],
    ["USP UD", "USP UPPER DIVISION ELECTIVE"],
    ["WCWP 10A", "WCWP10A"],
    ["WCWP 10B", "WCWP10B"],
]
merger_dict: Dict[str, str] = {}
for equivalents in mergers:
    equivalents = list(map(clean_course_name, equivalents))
    # Using first item in each list as canonical
    for equivalent in equivalents[1:]:
        if equivalent != equivalents[0]:
            if equivalent in merger_dict:
                raise Warning(
                    f"'{equivalent}' already has an equivalent '{merger_dict[equivalent]}'"
                )
            merger_dict[equivalent] = equivalents[0]

course_titles: Dict[str, int] = {}

for year in range(2015, 2023):
    for plans in major_plans(year).values():
        for college in plans.colleges:
            for course in plans.plan(college):
                title = clean_course_name(course.raw.course_title)
                if title in merger_dict:
                    title = merger_dict[title]
                if title not in course_titles:
                    course_titles[title] = 0
                course_titles[title] += 1

for title in sorted(course_titles.keys()):
    print(f"({course_titles[title]})".rjust(7) + " " + title)
print(f"{len(course_titles)} course names")
