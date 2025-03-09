> [!IMPORTANT]
> Because this fork has diverged significantly from the [original repo](https://github.com/ArturoAmaya/ExploratoryCurricularAnalytics), I've made a hard fork at
> [**SheepTester-forks/curricular-analytics-exploration**](https://github.com/SheepTester-forks/curricular-analytics-exploration).
> Development continues there.

# Curricular Analytics exploration

This is a long README for a large repo. Here's a list of quick links:

- [Setting up your environment](#setup)
- [Other related repos](#whats-in-other-repos)
- [Required data files](#required-files)
- [What to change for a new school year](#how-to-use-a-data-refresh)

## Setup

> [!NOTE]
> I recommend Windows users use WSL. While I am a Windows user myself, I haven't tested anything outside of WSL.

1. Make sure the following are installed:

   - `make`

     ```shell
     $ sudo apt install make
     ```

   - Python 3.12 or newer.

     I recommend setting up a virtual environment using VS Code. For some reason WSL comes with Python 3.12 preinstalled, but not `pip`. Using [VS Code's Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) to create a virtual environment from `/bin/python3.12` (ctrl+shift+P then "Python: Create Environment...") fixes this.

     Then, install the Python dependencies ([`curricularanalytics`](https://pypi.org/project/curricularanalytics/), [`python-dotenv`](https://pypi.org/project/python-dotenv/)):

     ```shell
     $ pip install -r requirements.txt
     ```

   - Node 22 or newer.

     I recommend using [nvm](https://github.com/nvm-sh/nvm) to install Node.

     Then install the Node dependencies.

     ```shell
     $ npm install
     ```

2. Download the required CSV files to files/. The links are probably private, so you will have to request access or ask for updated data. Their format is [detailed below](#required-files).

   - **`academic_plans_thruFA24.csv`** and **`prereqs_thruFA25.csv`** from the [Archive of Data Dumps](https://ucsdcloud.sharepoint.com/:f:/r/sites/EI/Shared%20Documents/Projects/Curricular%20Analytics/Archive%20of%20Data%20Dumps)
   - [**`isis_major_code_list.csv`**](https://blink.ucsd.edu/_files/instructors-tab/major-codes/isis_major_code_list.xlsx)
     - Export the Major Codes sheet ("isis_major_code_list") as a CSV.

3. Run `make`.

   ```shell
   $ make
   ```

   If you're working with [protected data](#protected-data) (for the [plan graph](https://github.com/SheepTester-forks/curricular-analytics-graph)), you also need to `make protected`.

   ```shell
   $ make protected
   ```

   You can remove all generated files by running

   ```shell
   $ make clean
   ```

4. Enjoy the output. `Makefile` has the files that are produced listed under `# Reports`.

5. Every year, once a data dump of the new year's plans and prereqs is available, you'll need to update all the reports. See [§ How to use a data refresh](#how-to-use-a-data-refresh) for instructions on how to do this.

### What's in other repos

- [CurricularAnalytics.py](https://github.com/SheepTester-forks/CurricularAnalytics.py): This is a rewrite of CurricularAnalytics.jl (hence the unused Julia files in this repo). Julia takes such a long time to start up (due to JIT compilation) that it overshadows any resulting performance gains, so these scripts end up running faster in Python.

- [curricular-analytics-graph](https://github.com/SheepTester-forks/curricular-analytics-graph): This produces `plan-graph.html`. I recommend cloning that repo in the same parent folder as this repo (i.e. the repos should be siblings) because the graph repo depends on files in this repo.

- [ucsd-plan-editor](https://github.com/SheepTester-forks/ucsd-plan-editor): This produces [`plan-editor.html`](https://educationalinnovation.ucsd.edu/_files/plan-editor.html).

- [ucsd-degree-plans](https://github.com/SheepTester-forks/ucsd-degree-plans): This contains the output of dump_graphs.py and is referenced by [`plan-graph-index.html`](https://educationalinnovation.ucsd.edu/_files/plan-graph-index.html).

  ```shell
  $ rm -rf plan_csvs/ # Ensure empty
  $ git clone https://github.com/SheepTester-forks/ucsd-degree-plans.git plan_csvs
  $ rm -r plan_csvs/* plan_csvs/metadata.json # Ensure old files get removed
  $ make
  $ cd plan_csvs/
  $ git add .
  $ git commit -m "..."
  $ git push
  ```

### Required files

[`parse.py`](parse.py) expects certain files in the `files/` directory. Download them from our shared Google Drive folder.

- [**`academic_plans.csv`**](https://ucsdcloud.sharepoint.com/:f:/r/sites/EI/Shared%20Documents/Projects/Curricular%20Analytics/Archive%20of%20Data%20Dumps),
  containing degree plans for every year, major, and college combination since
  fall 2012 created by college advisors painstakingly cross-referencing major
  and college requirements to manually design plans for every major, so there
  are some human errors. These plans are publicly available at
  [plans.ucsd.edu](https://plans.ucsd.edu/).

  We use this to create degree plans and curriculum for every major to upload to
  [Curricular Analytics](https://curricularanalytics.org/). It is retrieved using this SQL query:

  ```sql
  -- Hops (Provost DB) - Academic Plans query
  SELECT
  p.department AS "Department",
  p.major_code AS "Major",
  p.college  AS "College",
  c.course_name AS "Course",
  c.units  AS "Units",
  c.course_type  AS "Course Type",
  CASE c.ge_major_overlap WHEN 1 THEN 'Y' ELSE 'N' END AS "GE/Major Overlap",
  p.start_year AS "Start Year",
  c.year_taken AS "Year Taken",
  c.quarter_taken AS "Quarter Taken",
  CASE
  WHEN c.quarter_taken=1 THEN CONCAT('FA',SUBSTRING(p.start_year+c.year_taken-1,3,2) )
  WHEN c.quarter_taken=2 THEN CONCAT('WI',SUBSTRING(p.start_year+c.year_taken,3,2) )
  WHEN c.quarter_taken=3 THEN CONCAT('SP',SUBSTRING(p.start_year+c.year_taken,3,2) )
  WHEN c.quarter_taken=4 THEN CONCAT('SU',SUBSTRING(p.start_year+c.year_taken,3,2) )
  ELSE 'ERROR' END AS "Term Taken"
  FROM college_four_year_plans.college_plans p
  JOIN college_four_year_plans.college_plan_courses c
   ON (c.plan_id =p.plan_id )
   WHERE p.plan_length =4 AND p.start_year >=2012 AND p.college <>'XX'
   ORDER BY p.start_year ,p.major_code ,p.college,c.year_taken ,c.quarter_taken ,c.display_order
  ```

  If others want to adapt our code for their university, here is sampling of rows to show what we were dealing with.

  | Department | Major | College | Course  | Units | Course Type | GE/Major Overlap | Start Year | Year Taken | Quarter Taken | Term Taken |
  | ---------- | ----- | ------- | ------- | ----- | ----------- | ---------------- | ---------- | ---------- | ------------- | ---------- |
  | ANTHROPOLO | AN27  | SI      | ANTH 1  | 4.0   | DEPARTMENT  | N                | 2012       | 1          | 1             | FA12       |
  | ANTHROPOLO | AN27  | SI      | CAT 1   | 4.0   | COLLEGE     | N                | 2012       | 1          | 1             | FA12       |
  | BENG       | BE25  | FI      | CHEM 6A | 4.0   | DEPARTMENT  | N                | 2012       | 1          | 1             | FA12       |
  | BENG       | BE25  | MU      | CHEM 6A | 4.0   | DEPARTMENT  | N                | 2012       | 1          | 1             | FA12       |

  - `Major` is an [ISIS major
    code](https://blink.ucsd.edu/instructors/academic-info/majors/major-codes.html).

  - `College` is a two-letter code for a UCSD college.

    | Code | Name                                               |
    | ---- | -------------------------------------------------- |
    | RE   | Revelle                                            |
    | MU   | Muir                                               |
    | TH   | Marshall (formerly Third)                          |
    | WA   | Warren                                             |
    | FI   | ERC (formerly Fifth)                               |
    | SI   | Sixth                                              |
    | SN   | Seventh                                            |
    | DP   | Appears in the file, but we're not sure what it is |

    Generally speaking, every major has a plan for every college. However, there
    are exceptions, usually for weird majors that aren't actually 4-year plans
    (e.g. only Revelle has plans for undeclared "majors").

    For universities without a college system, this column can be set to a single value or be used for plans with different general education requirements (e.g. an honors college). The Python programs do not expect a specific format for college codes.

  - `Course` is a **manually-written** description of a course. It's usually the
    course subject and number, but it can also be a phrase like "CSE Elective"
    or list alternatives like "MATH 10A/20A." Human error makes parsing this
    difficult; see [`parse_course_name`](./parse_course_name.py) for an attempt.

    Course codes from other colleges will likely require modifying the implementation of [`parse_course_name`](./parse_course_name.py).

  - `Course Type` is either `DEPARTMENT` (major requirement) or `COLLEGE` (GE requirement). When `GE/Major Overlap`
    is `Y` (a course satisfies both major and college requirements), it doesn't matter what `Course Type` is.

    To get a curriculum (the major requirements) from a plan, we only keep
    courses with a `Course Type` of `DEPARTMENT` _or_ a `GE/Major Overlap` of
    `Y`.

    We were not provided a plan with only major requirements. According to #14 it seems
    removing college-specific courses from Marshall (TH)'s degree plan tends to
    produce the most compatible results for other colleges, so we base curricula
    off of Marshall.

    Currently, many parts of the code only handle UCSD's seven colleges. Some modification would be required to use other college codes.

  - `Start Year` indicates the year that the plan is for. For example, a student
    who enrolls at UCSD in fall 2019 should follow the plan with a `Start Year`
    of 2019.

  - `Year Taken` and `Quarter Taken` define the *n*th school year and *n*th quarter.

    Our Python programs expect four quarters per year (this includes a summer quarter at the end of each year, even though plans should not require summer sessions), but not all quarters need to be used. For universities on the semester system, the first two quarters could be used to represent the two semesters.

    Many parts of the code currently expect four years, each with three quarters. Summer quarters (the fourth quarter of each year) are merged with the prior spring quarter.

  - `Term Taken` is not used. Its contents can be derived from the other columns.

- [**`prereqs.csv`**](https://ucsdcloud.sharepoint.com/:f:/r/sites/EI/Shared%20Documents/Projects/Curricular%20Analytics/Archive%20of%20Data%20Dumps),
  containing every course and their prerequisites for every quarter since fall 2012.

  We use this to add prerequisite and corequisite relationships between courses
  in the degree plans for [Curricular
  Analytics](https://curricularanalytics.org/). It was retrieved using this SQL query:

  ```sql
  SELECT
      sc.TRM_TERM_CODE AS "Term Code",
      sc.TRM_TERM_ID AS "Term ID",
          sc.CRS_COURSE_ID AS "Course ID",
          sc.SUB_SUBJECT_CODE AS "Course Subject Code",
          sc.CRS_COURSE_CODE AS "Course Number",
          p.PREREQ_SEQ_ID AS  "Prereq Sequence ID",
          p.PREREQ_COURSE_ID AS "Prereq Course ID",
          p.PREREQ_SUBJECT_CODE AS "Prereq Subject Code",
          p.PREREQ_COURSE_CODE AS "Prereq Course Number",
          p.PREREQ_MIN_GRADE_PRIORITY AS "Prereq Minimum Grade Priority",
          g.GRADE_CODE  AS "Prereq Minimum Grade",
          p.PREREQ_CNCRNT_REG_PERMITTED AS "Allow concurrent registration"
          FROM STUDENT_DB.S_COURSE sc
          LEFT JOIN STUDENT_DB.S_COURSE_PREREQ p
          ON (p.CRS_COURSE_ID=sc.CRS_COURSE_ID AND p.TRM_TERM_CODE=sc.TRM_TERM_CODE AND p.CRS_START_TERM =sc.CRS_START_TERM_CODE AND p.CRS_END_TERM=sc.CRS_END_TERM_CODE)
          LEFT JOIN  STUDENT_DB.S_STU_LEVEL_GRADE g
          ON (g.ACADEMIC_LEVEL ='UN' AND g.END_TERM_CODE ='' AND g.GRADE_PRIORITY=p.PREREQ_MIN_GRADE_PRIORITY )
          WHERE sc.TRM_TERM_ID  >= 4550 AND sc.CRS_ACADEMIC_LEVEL IN ('UD','LD')
          ORDER BY sc.TRM_TERM_ID ASC,sc.CRS_COURSE_ID ASC, p.PREREQ_SEQ_ID, p.PREREQ_COURSE_ID ;
  ```

  Here are some sample rows from the CSV file.

  | Term Code | Term ID | Course ID | Course Subject Code | Course Number | Prereq Sequence ID | Prereq Course ID | Prereq Subject Code | Prereq Course Number | Prereq Minimum Grade Priority | Prereq Minimum Grade | Allow concurrent registration |
  | --------- | ------- | --------- | ------------------- | ------------- | ------------------ | ---------------- | ------------------- | -------------------- | ----------------------------- | -------------------- | ----------------------------- |
  | FA22      | 5250    | CHEM43AM  | CHEM                | 43AM          | 001                | CHEM7L           | CHEM                | 7L                   | 600                           | P                    | N                             |
  | FA22      | 5250    | CHEM43AM  | CHEM                | 43AM          | 001                | CHEM7LM          | CHEM                | 7LM                  | 600                           | P                    | N                             |
  | FA22      | 5250    | CHEM43AM  | CHEM                | 43AM          | 002                | CHEM40A          | CHEM                | 40A                  | 600                           | P                    | N                             |
  | FA22      | 5250    | CHEM43AM  | CHEM                | 43AM          | 002                | CHEM40AH         | CHEM                | 40AH                 | 600                           | P                    | N                             |
  | FA22      | 5250    | CHEM43AM  | CHEM                | 43AM          | 002                | CHEM41A          | CHEM                | 41A                  | 600                           | P                    | N                             |
  | FA22      | 5250    | CHEM6A    | CHEM                | 6A            |                    |                  |                     |                      |                               |                      |
  | FA22      | 5250    | CHEM6AH   | CHEM                | 6AH           |                    |                  |                     |                      |                               |                      |

  Some courses do not have prerequisites, so they will have a single row with
  empty fields after `Course Number`.

  For courses with prerequisites, they will have a row for every prerequisite
  course. `Prereq Sequence ID` is a natural number, and of the prerequisites
  with the same `Prereq Sequence ID`, only one course is needed to satisfy the
  requirement. One course from each `Prereq Sequence ID` is required to satisfy
  the prerequisites for the course.

  In the case of UCSD, `Allow concurrent registration` represents how WebReg enforces corequisites, which can differ from the course catalog. For example, while CSE 12 and CSE 15L are said to be corequisites in the course catalog, there is no such relationship in WebReg. Generally speaking, this flag is almost always `N`. The Python program creates a non-strict corequisite relationship between two courses when this flag is set to `Y`.

  `Term ID`, `Course ID`, `Prereq Course ID`, `Prereq Minimum Grade Priority`,
  and `Prereq Minimum Grade` aren't used.

  `Term Code` is respected in case prerequisites change midway through the plan. They currently are expected to be in UCSD's term code format: `<quarter><year>`, such as `FA22` for Fall 2022.

- [**`isis_major_code_list.csv`**](https://blink.ucsd.edu/_files/instructors-tab/major-codes/isis_major_code_list.xlsx)

  The spreadsheet is a modified version of the publicly available [list of ISIS
  major
  codes](https://blink.ucsd.edu/_files/instructors-tab/major-codes/isis_major_code_list.xlsx).

  We use this to add the major name and CIP major code to the uploaded
  curriculum on the [Curricular Analytics
  website](https://curricularanalytics.org/).

  | Previous Local Code | UCOP Major Code (CSS) | ISIS Major Code | Major Abbreviation | Major Description              | Diploma Title                             | Start Term | End Term | Student Level | Department | Award Type | Program Length (in years) | College              | CIP Code | CIP Description                | STEM | Self Supporting | Discontinued or Phasing Out | Notes                                                                   |
  | ------------------- | --------------------- | --------------- | ------------------ | ------------------------------ | ----------------------------------------- | ---------- | -------- | ------------- | ---------- | ---------- | ------------------------- | -------------------- | -------- | ------------------------------ | ---- | --------------- | --------------------------- | ----------------------------------------------------------------------- |
  |                     | 0HK                   | AA25            | BlkDspAfAm         | Black Diaspora &African AmrcSt | Black Diaspora & African American Studies | S122       |          | UN            | AAS        | BA         | 4.00                      | RE MU TH WA FI SI SN | 050201   | AFRICAN-AMERICAN/BLACK STUDIES |      |                 |                             | Administrative start in S1 to accommodate new students attending Summer |

  Only the following fields are used:

  - `ISIS Major Code` is the major code used by UCSD and the Python programs as an ID for each major. At UCSD, they are of the format `<subject><number>`, such as `CG25` for Cognitive Science. The Python programs do not expect a specific format for these major codes.

  - `Diploma Title` is used as a human-readable display name for the major.

  - `Department` is a department code used to group majors by departments and schools. The Python programs don't expect a specific format for department codes, but the way majors are grouped for Tableau views is defined in [`departments.py`](./departments.py).

  - `Award Type` (BS vs BA) and `CIP Code` (national major codes) are used to populate data fields for Curricular Analytics. That's it.

#### Protected data

- [**`21-22 Enrollment_DFW CJ.xlsx.csv`**](https://docs.google.com/spreadsheets/d/1Lq1-35oZra3pOS94VdrWOPD3gQZgmfCb/): Export as CSV.

- [**`Waitlist by Course for CJ.xlsx.csv`**](https://docs.google.com/spreadsheets/d/1EC9QdtP9vy2nX46XOQyXWiMO7gnYWc6-/): Export as CSV.

- [**`CA_MetricsforMap_FINAL(Metrics).csv`**](https://ucsdcloud-my.sharepoint.com/:x:/r/personal/eespaldon_ucsd_edu/_layouts/15/Doc.aspx?sourcedoc=%7BD138C288-C477-4FC1-8F27-A275EAD0DCFD%7D&file=CA_MetricsforMap_FINAL.xlsx): Export as CSV.

### Uploading

To automatically upload CSV files to Curricular Analytics using [`upload.py`](upload.py), you need to create a copy of [`.env.example`](.env.example) and name it `.env`, then fill in `AUTHENTICITY_TOKEN` and `CA_SESSION`.

- To get `CA_SESSION`, open inspect element and head to Application > Cookies > https://curricularanalytics.org. Copy the cookie value for `_curricularanalytics_session`.

  ![`_curricularanalytics_session` cookie](./docs/ca_session.png)

## Development (plan diff, prereq tree, and plan editor)

Watch for changes. Open the template file in the browser:

- http://localhost:8000/reports/plan-diffs/template.html
- http://localhost:8000/reports/prereq-tree/template.html
- http://localhost:8000/reports/plan-editor/template.html

```sh
$ npm run watch plan-diffs
$ npm run watch prereq-tree
$ npm run watch plan-editor
```

Build a single file. Upload the output file to the CMS.

- reports/output/academic-plan-diffs.html
- reports/output/prereq-tree.html
- reports/output/plan-editor.html

```
$ make
```

# Projects

There are a lot of scripts in the top-level directory of this repo, and it's not clear how they're related to each other because file tree viewers tend to alphabetize these file names. `redundant_prereq_check.py` and `redundant_prereq_courses.py` are right next to each other; are they related?

Many files are one-time scripts just to answer a question that someone or I had. How many majors depend on math 18? Which major changed the most over the past few years? Also, for technical reasons ([I don't understand Python modules](https://stackoverflow.com/a/4383597)), I put all the Python files in the root directory so they can import each other.

Below, the files are listed in somewhat chronological order, at least within each list. I think this organization better shows the relationship between the files so that when I clean things up for others to use, it's easier to tell which ones I can toss out.

## Uploading to Curricular Analytics

_2022 June 8 to July 7 (2021 plans), August 2 to 11 (2015–2022 plans). Python._

Task: Upload every major's curriculum and each of its college degree plans to Curricular Analytics.

We approached this using automation rather than manually entering in the plans as other universities did. This involved parsing the given CSVs of all degree plans and majors, then outputting CSVs in the format of Curricular Analytics. A lot of cleanup was necessary to fix prerequisites, clean up messy course names, and correct the number of units for courses. Finally, to expediate uploading all of the plans, I reverse engineered Curricular Analytics' internal API to automate uploading the generated CSVs to the website.

[ca-julia]: https://github.com/CurricularAnalytics/CurricularAnalytics.jl/

I also rewrote some Python scripts in Julia so the degree plans could be used with the [Curricular Analytics Julia package][ca-julia].
We were later given academic plans from 2012 to 2022; we previously only had plans from 2021. I only uploaded the plans from 2015 on (older plans were deemed too low quality). The Curricular Analytics website wasn't great for navigating this many curricula, so I made a [Tableau view that just had links][curr-idx] to the curriculum for every major and year.
In a later refactor, I tried to pull out all UCSD-specific code into its own file, university.py, so other universities don't have to scour through the code to figure out how to adapt it.

Arturo noticed a discrepancy between the complexity scores shown on Curricular Analytics (calculated by the website on curricula generated by Python) and Tableau (calculated by the Julia package from curriculum objects created by Julia). I suspected that the two implementations of degree plan parsing differed, and looked into finding differences between them. Ultimately, I think I will discard the Julia implementation when we finish [translating CurricularAnalytics.jl to Python](#rewriting-curricularanalyticsjl-in-python).

Files:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
**parse.py** | parses the input CSV files as Python objects.
**output.py** | takes the Python objects and outputs them as CSV or JSON files to upload to Curricular Analytics.
**api.py** | defines helper methods that interface directly with Curricular Analytics' internal API. Think of it like discord.js but for Curricular Analytics. <br> [Documentation for Curricular Analytics' internal API](./docs/ca-api.md)
**Parse.jl** | is the Julia equivalent of parse.py.
**Output.jl** | creates `Curriculum` and `DegreePlan` objects for a given year and major.
<!-- prettier-ignore-end -->

Data files:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
**output_json.py** | defines Python `TypedDict` objects to define the JSON structure for output.py.
**departments.py** | parses a JSON file containing a list of departments. The department name is included in the curriculum name on Curricular Analytics.
university.py | defines UCSD-specific constants, such as the number of colleges and the university name.
parse_defs.py | defines Python objects representing data regarding plans, such as `CourseCode`s and `TermCode`s.
<!-- prettier-ignore-end -->

This involved additional scripts for error checking:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
compare-curricula.py | (output: comparisons.txt) compared, for each major, every college's degree plan (major courses only) against each other, and listed the differences in courses in comparisons.txt. I found that Marshall had the least deviations overall, so Marshall's degree plans are used to create curricula.
marshall-viability-analysis.py | (output: marshall.txt) was a follow-up script that checked that Marshall was the least deviant of all the colleges. It compared Marshall with the degree plans of all the other colleges and printed when it disagreed with every college. It only disagreed with the others twice, which is pretty good.
course_names.py | (output: course_names.txt) listed every unique course title (cleaned up a bit) with its parsed course code. This was to test `parse_course_name` (which turns `BICD110` into `("BICD", "110")` but not `IE1` into `("IE", "1")`) as well as `clean_course_title`.
department_names.py | (output: departments.txt) checks if there were department codes in the degree plan CSV that weren't included in the major code CSV. <br> This was originally called departments.py, but I renamed it in a merge conflict because there was already another departments.py. This is why the output isn't called department_names.txt.
course_names2.py | (output: course_names2.txt) attempted to clean up course titles more aggressively, mostly to match the example CSV files we were given. <br> However, by removing `GE`, `AWP`, and `DEI`, this ended up removing useful context from the plans. For example, some plans had something like two instances of "MCWP 40/GE," but on Curricular Analytics, this appeared as two MCWP 40 courses, which looks like an error. The rewrite of parse.py does not do this anymore I believe.
common_prereqs.py | (output: common_prereqs.txt) identified common prereqs across all courses in a subject. This was to figure out if there were any exceptions other than the provided `SOCI- UD METHODOLOGY` and `TDHD XXX`. <br> We started with example manually created curricula that defined prerequisites for these course categories, and to make our script match the examples, we just added special cases for those two courses.
unit_check.py | listed degree plans with fewer than 180 units.
course_names3.py | (output: course_names3.txt) runs [Arturo's course name cleanup algorithm](https://www.overleaf.com/project/62e8265ff1395d787286ea5b) on every unique course title, and lists all resulting unique cleaned course titles. The goal with this is to reduce variability in course titles resulting from college advisors phrasing things differently. <br> This supercedes the old aggressive course title cleanup algorithm that was tested by course_names2.py.
DebugOutput.jl | output a JSON representation of the degree plan objects produced by Julia. This was intended to be compared with equivalent output from Python.
<!-- prettier-ignore-end -->

Scripts for uploading:

<!-- prettier-ignore-start -->

| File | Description |
| ---- | ----------- |
**upload.py** | (output: files/uploaded\*.yml) is a CLI tool that uploads the specified major to Curricular Analytics.
**update.py** | overwrote an already-uploaded curriculum. I ran this if I fixed something in output.py. It uses Curricular Analytics' internal API for editing curricula/degree plans using their visual editor by sending them a JSON file (rather than CSV) of the result. <br> This script isn't very good because Curricular Analytics is kind of buggy. Course IDs are tied between curriculum and degree plans or something because in updated plans, prerequisites specific to a course in one degree plan would bleed into another. Uploading or editing by JSON is also much slower than using a CSV file. <br> Editing is occasionally necessary because you can only delete curricula you created, and we were asked to overwrite the curricula already uploaded by someone else with ones generated by our scripts. Also, if we wanted to fix something now, we probably wouldn't want to break URLs by deleting existing curricula and uploading new ones.
files/fix.sh | was used to update already-uploaded plans for several majors without me having to sit around the terminal waiting for it to load.
check_uploaded.py | checked every major uploaded onto Curricular Analytics. For some reason, if curricula are uploaded too quickly to Curricular Analytics, they end up with blank degree plans. This happened for curricula uploaded earlier before I realized I set the delay time too short.
rename_all.py | renamed every uploaded 2021 curriculum on Curricular Analytics to the new curriculum name format. This was because we were uploading plans for other years now, so the existing curriculum names had to include their year.
files/upload.sh | was used to mass-upload plans for other (non-2021) years.
<!-- prettier-ignore-end -->

## Tableau of metrics

_2022 July 7 to August 2. Python, Julia, Tableau. [Views 1 and 2][views], [reports 1–4][reports], [curriculum index][curr-idx]._

Task: Create dashboards on Tableau displaying data about courses and majors:

1. View \#1: majors going down, colleges going right. Given a year, select a metric to show in each degree plan's cell, or flag plans that meet specific conditions.
2. View #2: majors going down. Given a college and year, select a metric to show in each row along with its value (e.g. the name of the course with highest complexity).
3. Reports:
   1. Number of plans any course appears in by year.
   2. Complexity for any course by plan and year.
   3. Centrality for any course by plan and year.
   4. Course overlap between majors.

In order to get metrics such as complexity and centrality, I had to use Curricular Analytics' [Julia package][ca-julia]. I had to load the plans from Python into Julia. I first created a CSV file for every degree plan, but I decided to rewrite the plan parsing script in Julia. The Julia scripts output CSV files that I imported into Tableau. Tableau is quite powerful but also somewhat annoying to fight when I want a visualization (viz) to look a certain way.

<!-- We were supposed to receive Tableau training, but scheduling was a pain. We had to take a privacy workshop first (where they asked us to move our views from Tableau Public to UCSD's Tableau instance), but by then, we had already figured out Tableau ourselves. -->

Arturo took over handling the Tableau views, adding additional views (including views for quality control) and blank, data-less templates for other universities to use. We plan on sharing views so that some views were public while others remained private to administrators only once we get sharing permissions.

<!-- It has been over a year, and we still haven't resolved this issue. -->

Someone wanted to filter the course centrality/complexity view by year taken in plan, so I added a new column to the CSV file. It took a bit to figure out how to update a CSV data source on a view already uploaded to Tableau; I think I ended up just adding a new data source and swapping out references from the old to new version, resulting in two versions of a CSV file both in use in the same Tableau file.

[Old Tableau view][metrics-old]:

<!-- _Carlos mentioned in a meeting that he wanted a certain Tableau view, so I went ahead and [made it][metrics-old]. This was before he gave more specific details above._ -->

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
output_all.py | (output: files/output/\*\*/\*.csv) wrote a CSV for every curriculum and degree plan (2021 only).
metrics.jl | (output: files/metrics.csv, files/courses.csv) read these CSVs then created a CSV of each degree plan's metrics.
<!-- prettier-ignore-end -->

New Tableau views:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
Metrics.jl | (output: files/metrics_fa12.csv) uses these objects to output a CSV of all the metrics needed for the [Tableau views (#1 and #2)][views] for every year-major-college combination. <br> Not to be confused with lowercase metrics.jl. I don't know why I named it this way, but I guess it was because this supercedes the old metrics.jl. Julia module names are conventionally uppercase, which I learned after writing metrics.jl.
**Utils.jl** | helped to reduce code repetition between Metrics.jl and CourseMetrics.jl for common functions like writing a CSV row.
CourseMetrics.jl | (output: files/courses_fa12.csv) outputs a CSV of every course in every year-major and lists its metrics in the curriculum (based on Marshall's degree plan). This is for [reports #1, #2, and #3][reports].
CourseOverlap.jl | (output: files/course_overlap.csv) lists the percent overlap of courses for every ordered major pair and year, for [report #4][reports]. It's an ordered pair because the way I calculated percent overlap wasn't commutative; it used the first major's number of courses in the denominator of the percentage.
curricula_index.py | (output: files/curricula_index.csv) created a CSV file with the URL of every year-major pair, including the department and school of the major. This was for the [list of uploaded Curricular Analytics curriculum links][curr-idx]. <br> I'm listing this here because it's kind of a cross between the plan uploading and Tableau view project (we consider it a Tableau viz).
<!-- prettier-ignore-end -->

Unrelated:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
majors_per_course.py | (output: files/majors_per_course.csv) lists the number of majors a course shows up in per major. Apparently this has nothing to do with the Tableau views; the math department just wanted to know how many majors depend on math 18.
redundant_prereq_check.py | attempted to identify redundant prereqs. I think this might be to remove unnecessary prereq lines in the degree plans on Curricular Analytics (e.g. an arrow from MATH 20A and MATH 20B to some other course, even though only the arrow from MATH 20B is necessary).
<!-- prettier-ignore-end -->

[metrics-old]: https://public.tableau.com/app/profile/sean.yen/viz/metrics_16619827387790/
[views]: https://public.tableau.com/app/profile/sean.yen/viz/metrics_fa12/
[reports]: https://public.tableau.com/app/profile/sean.yen/viz/reports_16591343716100/
[curr-idx]: https://public.tableau.com/app/profile/sean.yen/viz/curriculum_index/

## Systematically flagging issues

_2022 August 18–23. Python. [Document](https://docs.google.com/document/d/1fa70-d-hs-eTqiSTg7h5M69SWHUgpRjxH6z_3ymu9vc/)._

Task: Systematically flag common issues in UCSD's degree plans (because they are manually created by advisors, so they're bound to contain mistakes).

At first, these issues were supposed to be unfiltered so the colleges could identify false positives, but after some colleges fixed the issues, the issues were expected to be cleaned up. I am currently waiting on a data update to remove issues that have been fixed.

<!-- They're rather pissed that the document is still listing issues they've fixed, but we haven't gotten a data update since last year. -->

The report used to be in plain text, but I moved it to a Google Doc so it's web accessible for the advisors.

Files:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
flag_issues.py | (output: files/flagged_issues.html) outputs an HTML file that can be copy-pasted into a Google Doc for the advisors.
units_per_course.py | (output: units_per_course.txt, units_per_course.json) identifies the likely correct number of units for a course. This is used as the correct number of units until I get a dataset of units per course (which I have not yet received). <br> However, this isn't very accurate because units of courses can change over time. LTSP 2A seemingly used to be 4 units and now is 5, and all but one college updated their plans to reflect this, but they're all marked wrong because most of the older plans have 4 units.
<!-- prettier-ignore-end -->

## Web apps

> [!WARNING]
> These were originally written with [Deno](https://deno.com/) and [Preact](https://preactjs.com/) (very similar to React). However, because [`deno bundle` was deprecated](https://github.com/denoland/deno/issues/11073) then removed in Deno 2, and to lower the barrier to entry of others maintaining this project, I've since switched to [React](https://react.dev/), which more people are familiar with, and [esbuild](https://esbuild.github.io/) for bundling. Some old files may still contain references to Deno and Preact.

The following projects involved interactive web pages written in [TypeScript](https://www.typescriptlang.org/) using [React](http://react.dev/) bundled by [esbuild](https://esbuild.github.io/) that used the existing data sources we had (prerequisites and academic plans) to deliver new insights about UCSD's courses and majors. These web reports and apps were uploaded to the [UCSD Educational Innovation website](https://educationalinnovation.ucsd.edu/ca-views/).

For all web reports:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
Makefile | is shared by all web reports and contains the commands to build all web reports just by running `make`.
cms-replace-file.js | is a browser script (copypaste and run in console) that adds a file input to every entry on UCSD's CMS that allows me to upload a large HTML file to overwrite an existing file. <br> UCSD's CMS ([Cascade](https://www.hannonhill.com/products/cascade-cms/index.html)) shows a code editor for HTML files, which hangs the page when trying to load the large HTML files that these projects produce, so I can't upload a new version of an HTML file normally.
reports/util/Prereqs.ts | defines types for `CourseCode` and `Prereqs` that are used across the web apps.
reports/util/Vector2.ts | exports a two-component vector class.
reports/util/csv.ts | exports a helper function for outputting a CSV.
reports/util/download.ts | exports a function for downloading a file.
<!-- prettier-ignore-end -->

### Changes to degree plans over time (plan diff)

_2022 August 26–31. Python, Deno/TypeScript/Preact. [Details](https://educationalinnovation.ucsd.edu/ca-views/plan-changes.html), [report](https://educationalinnovation.ucsd.edu/_files/academic-plan-diffs.html)._

I was shown a graph showing how chaotically units and complexity were changing differently in each college even for the same major, and I wanted to see what specific changes were occurring to these plans, so I went ahead and made a diffing program. With feedback, I made what originally was a fancy CLI tool into a web app. Since I had done the [CMS training](https://blink.ucsd.edu/technology/websites/training/start/access/index.html), I got access to [educationalinnovation.ucsd.edu](https://educationalinnovation.ucsd.edu/) and was told to upload the web page on there.

Files: (output: reports/output/academic-plan-diffs.html)

- diff_plan.py (output: reports/output/academic-plan-diffs.json) pretty-prints the changes made to the given major-college degree plan over the years. To make it more presentable for the advisors, this also outputs a JSON file of diffs for every major-college combo for the web app that I made.
  - It uses files/metrics_fa12.csv (rather than from PlanChanges.jl) to include complexity score changes.
- reports/plan-diffs-template.html - A template HTML file. The Makefile replaces the last few lines with inline script tags containing the JSON of all the plan changes and the bundled code.
- reports/plan-diffs.tsx - The entry point of the Preact app. It's written in TypeScript for Deno and uses Preact, and it's bundled using `deno bundle`, which later got deprecated for some reason.
- reports/plan-diffs/components/App.tsx: top-level component.
  - reports/plan-diffs/components/Table.tsx: renders the table of majors and colleges on the left half of the screen.
  - reports/plan-diffs/components/Diff.tsx: renders the right half of the screen with the diffs for the selected major-college.
    - reports/plan-diffs/components/YearDiff.tsx: the changes made in a year for a major.
      - reports/plan-diffs/components/ChangeItem.tsx: a change made to a course in a plan.
        - reports/plan-diffs/components/Change.tsx: displays an old and new value in a change, such as a name change or a change in units for a course.
- reports/plan-diffs/types.ts: defines how the plan changes are represented in the JSON produced by diff_plan.py.

Unused:

- PlanChanges.jl (output: files/changes.csv, which I imported into a [Google Sheet](https://docs.google.com/spreadsheets/d/1CIz7pCOAduXC-58jixgXlHwYGKCx4k9MX7z51uq0wtQ/)) calculates the amount of change per major-college. I wanted to see which degree plans would have interesting diffs. This is not used anywhere else since diff_plan.py uses Metrics.jl's complexity scores.

### Changes to prerequisites over time (prereq diff)

_2022 September 9–28. Python. [Details](https://educationalinnovation.ucsd.edu/ca-views/prereq-changes.html), [report (by course)](https://educationalinnovation.ucsd.edu/_files/prereq-diffs.html), [report (by term)](https://educationalinnovation.ucsd.edu/_files/prereq-timeline.html)._

Task: list changes to prerequisites and specify which term they were added or removed.

I added an additional report to focus on changes one year at a time. This way, you can see when prerequisites are changed in the middle of a year.

Files: (output: reports/output/prereq-diffs.html, reports/output/prereq-timeline.html)

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
diff_prereqs.py | (reports/output/prereq-diffs-fragment.html, reports/output/prereq-timeline-fragment.html) generates an HTML fragment for the report.
reports/prereq-diffs-template.html, reports/prereq-timeline-template.html | Contains the CSS for the web page. The Makefile removes the last few lines to insert the HTML fragments generated by `diff_prereqs.py`.
<!-- prettier-ignore-end -->

### Additional GE units by college

_2022 October 14–18. Python, JavaScript. [Details](https://educationalinnovation.ucsd.edu/ca-views/college-ge-units.html), [report](https://educationalinnovation.ucsd.edu/_files/college-ge-units.html)._

Task: compare how plans vary between colleges.

Files: (output: reports/output/college-ge-units.html)

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
college_ges.py | (output: college_ges.csv, reports/output/college-ge-units-fragment.html) outputs a CSV or HTML table of every major and the number of non-elective GE units per college's degree plan.
reports/college-ge-template.html | has the CSS and some JavaScript functionality for table sorting by column.
<!-- prettier-ignore-end -->

### Tree of blocked courses (prereq tree)

_2022 November 3 to December 15 (blocked courses), 2023 January 19–24 (prerequisites). Deno/TypeScript/Preact. [Details](https://educationalinnovation.ucsd.edu/ca-views/prereq-tree.html), [app](https://educationalinnovation.ucsd.edu/_files/prereq-tree.html)._

Task: display a tree (like a [network graph](https://neo4j.com/developer-blog/hands-on-graph-data-visualization/) or a [top-down graph](https://www.researchgate.net/figure/Real-time-visualization-of-the-graph-of-curriculum-links-a-Management-view-b-Term_fig11_319277572)) showing prerequisite relationships to count how many courses depend on a given course.

My approach to this was to let the user enter in the classes they've taken, and every iteration, all courses with prerequisites[^1] that get unlocked by already-taken classes gets added to the list of classes taken, until no more courses are unlocked. I intended this to be used by students to see what classes they can take next, so after some feedback, I changed the wording to be about blocked courses, since that was what administrators were concerned about.

<!-- The tree ended up becoming a hit among administrators, apparently. -->

I later added a reverse option to show the prerequisite ancestors of a course as a tree.
I looked into another graphical representation of the tree since the current network diagram, albeit nice, was too messy.

<!-- I didn't finish as I moved on to rewriting [Curricular Analytics' Julia package][ca-julia] in Python. -->

[^1]: i.e. courses without prerequisites, such as CSE 11, would not be shown ever in the tree because it cannot be unlocked by a course: it's already unlocked. The exception to this is if the user entered CSE 11 in as a course to start with.

- dump_prereqs.py (output: reports/output/prereqs.json, files/blocked.csv) creates a JSON file containing all of the prereqs from the prereqs CSV file. It also can output a separate CSV file that runs the dependent course simulation on every course to calculate the number of courses blocked by each course; I uploaded this onto Google Sheets and embedded the result on the Educational Innovation website.
- reports/prereq-tree-template.html has the CSS for the web app.
- reports/prereq-tree.tsx is the entry point for the Preact app.
- reports/prereq-tree/components/App.tsx: the top-level component of the app.
  - reports/prereq-tree/components/CourseAdder.tsx: the search bar that lets you add and remove courses.
  - reports/prereq-tree/components/Options.tsx: a small menu on the top right corner that lets you switch between showing blocked courses (forward) and prerequisites (reverse).
  - reports/prereq-tree/components/Tree.tsx: a wrapper around a d3.js-controlled SVG for drawing the network graph.
  <!-- - reports/prereq-tree/d3-hack.ts: a hack to make d3.js work in TypeScript. -->
- reports/prereq-tree/graphs/ForceDirectedGraph.ts: renders a force-directed graph (network) using d3.js.
- reports/prereq-tree/graphs/TidyTree.ts: renders a more linear, level-by-level tree also using d3.js.
- reports/prereq-tree/graphs/GraphCommon.ts: contains code common between the force-directed graph and tidy tree.

### Academic plan creator (plan editor)

_2023 January 26 to April 6. [App](https://educationalinnovation.ucsd.edu/_files/plan-editor.html)._

Task: create a GUI for entering in plans, with the same format as [plans.ucsd.edu](https://plans.ucsd.edu/), that has autocompletion for course codes, a sidebar listing the prereqs for each course, and the ability to export the plan for Curricular Analytics.

UCSD already has [degree-planner.ucsd.edu](https://academicaffairs.ucsd.edu/sso/degree-planner/), but there are some nicer features in this one, like prereq checking.

<!-- Since we were waiting on fixing Tableau permissions and 2-year transfer plans, I didn't have much else to work on, so I spent perhaps a quarter on this. -->

Unfinished.

Files:

- reports/plan-editor-template.html: CSS.
- reports/plan-editor.tsx: entry point.
- reports/plan-editor/components/App.tsx: the top-level component of the web app.
  - reports/plan-editor/components/Metadata.tsx: metadata (e.g. the major code) for a plan, shown above the schedule.
    - reports/plan-editor/components/MetadataField.tsx: an input field in the metadata section.
  - reports/plan-editor/components/Editor.tsx: the schedule, taking up most of the screen next to the sidebar.
    - reports/plan-editor/components/Year.tsx: a year in the schedule.
      - reports/plan-editor/components/Term.tsx: a quarter in a year.
        - reports/plan-editor/components/PlanCourse.tsx: a course in the plan.
          - reports/plan-editor/components/CourseOptions.tsx: a dialog for editing course details, such as whether it satisfies a GE or major requirements, and listing warnings and errors about the course.
  - reports/plan-editor/components/PrereqSidebar.tsx: the sidebar.
    - reports/plan-editor/components/PrereqCheck.tsx: in the sidebar, lists the prerequisites for a course and alerts whether any are missing.
    - reports/plan-editor/components/CustomCourse.tsx: a custom course entry in the sidebar.
  - reports/plan-editor/components/RemoveZone.tsx: a visual red zone that appears while dragging a course to let you delete a course.
- reports/plan-editor/drag-drop.ts: defines types relating to dragging courses.
- reports/plan-editor/export-plan.ts: defines functions that export plans to various formats.
- reports/plan-editor/types.ts: defines how a plan is represented as a JavaScript object.
- reports/plan-editor/components/Toggle.tsx: unused toggle switch from the prereq tree.
- reports/plan-editor/save-to-url.ts: handled saving and loading a plan and options from the URL.
- reports/util/local-storage.ts: a getter for the `localStorage` object, since accessing it directly could throw errors in incognito mode in some browsers.
- reports/plan-editor/README.md: details the component hierarchy listed above.

Plan index:

- dump_plans.py (output: reports/output/plan-editor-index.html, reports/output/plans.json) outputs all academic plans to a file. This was to allow using an existing plan as a template to edit it.

## Redundant prerequisites by course

_2022 September 29 to October 11. Python. [Document](https://docs.google.com/document/d/1sxWBVhSMkQWPXLNyZXA4acDasFBuiv66rg6PFEJeEd8/)._

Task: identify redundant prerequisites for courses (rather than curricula with redundant prerequisites).

The Curricular Analytics Julia package can only identify redundant prerequisites in a curriculum or degree plan. Identifying redundancy in prerequisites without a degree plan is a bit harder because prerequisites aren't a graph—they encode OR relationships like "MATH 10B or 20A"—so typical graph algorithms won't work on it.

Files:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
redundant_prereq_courses.py | (output: files/redundant_prereq_courses.txt, redundant_prereq_courses.csv) outputs a report (human-readable plain text or CSV) of courses with redundant prerequisites. CSV support is to permit easier filtering. There are three categories of prerequisite issues that I ended up flagging: <ol><li>Courses that require nonexistent courses.</li> <li>Redundant prerequisites, which assumes every alternative prerequisite is taken.</li> <li>Courses with nonexistent courses as an alternative prerequisite</li></ol>
util.py | was created to house list partitioning helper functions. It's now used by other scripts too, like output.py after the rewrite.
<!-- prettier-ignore-end -->

## Rewriting CurricularAnalytics.jl in Python

_2023 April 13 to May 9. Python. [GitHub repo](https://github.com/SheepTester-forks/CurricularAnalytics.py)._

Task: port Curricular Analytics to Python.

Arturo had made a what-if tool in Julia using the [Curricular Analytics Julia package][ca-julia] and wanted to make it available for advisors to use. However, since the beginning of 2023 we've been trying to no avail to try to set up a server to run the Julia program as a backend; there were concerns about whether it would handle increased load during weeks 9 through finals, for example. IT was being very slow. So, one idea was to rewrite the package in Python—most people use Python, anyways, so it would be useful for more than just this one tool. This would also obviate having to maintain two versions of our plan parser.

Translating all the files was mostly tedious but simple work. Some issues I ran into were fussing over Python typings with third party libraries like pandas, and figuring out how to set up a Python package of my own. Translated Python files were placed adjacent to the original Julia files in a [fork](https://github.com/SheepTester-forks/CurricularAnalytics.py) of the original package. Even though Curricular Analytics had a REST API (documented in docs/ca-api-notes.md), having a Python version might still be useful in other cases.

<!-- Good progress was made until the U of A trip, when I changed focus to the seats calculator (below). The Curricular Analytics team didn't think a Python port was necessary because they had a (WIP) API (documented in docs/ca-api-notes.md), but Carlos believed the Python version would still be useful in cases when the API wouldn't suffice. -->

## Seats needed per course (class capacity calculator)

_2023 May 23 to June 2 (web app), July 24–31 (Python script)._

Task: calculate how many seats are needed per course based on the number of students in each major.

The number of students in each major wasn't enough: because of GEs and slightly different course placements in each college's degree plan, I'd also need to know the college distribution for each major. I'd also need the distribution of students in each year for maximum accuracy. Since we wouldn't be given the data until _after_ finishing the program, I decided to approach this by making another web app that would take a CSV file and ask whether it included college and year data, and make assumptions if not. This way, advisors could upload their own data without having to go through me.

However, because the results were a bit urgent, I ended up narrowing the scope by simply assuming each major is split evenly across 7 colleges and 4 years. We were then given a file of first year majors and colleges across 8 colleges. We don't have academic plans for 2023 yet, so Eighth students were omitted from our results. However, the academic plans aren't strictly followed anyways, so it doesn't really make our estimates significantly more inaccurate, I think.

Web app (no longer used):

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
courses_req_by_majors.py | (output: courses_req_by_majors.json) tried to output the degree plans that required each course.
reports/seats-template.html | CSS.
reports/seats.tsx | entry point.
reports/seats/components/App.tsx | top-level component.
reports/seats/components/SeatsNeeded.tsx | displays the seats needed per course.
reports/seats/courses-by-major.ts | defines types for the data structure of courses_req_by_majors.json.
reports/seats/students-by-group.ts | defines an intermediate format that the uploaded CSV file would be converted into. For example, if the given input doesn't account for years, then each major-college would be partitioned evenly into four years, and each demographic would look up the course it would take in the quarter.
<!-- prettier-ignore-end -->

Narrowed Python version:

<!-- prettier-ignore-start -->
| File | Description |
| ---- | ----------- |
course_capacities.py | (inputs: files/ClassCapCalculatorNewStudents.csv, files/ClassCapCalculatorCourses.csv; output: files/course_capacities_output.csv) takes the number of incoming first years in each major-college and the number of seats left in each course and outputs the number of seats needed for freshmen and seats available for each course. Eighth first-years are ignored. <br> The sample input: course_capacities_input.csv and output: course_capacities_output.csv were for an earlier version that assumed every major was evenly divided across the 7 colleges and 4 years.
<!-- prettier-ignore-end -->

## How to use a data refresh

1.  `Makefile`: Update these variables:

    - `year` - the final year available.
    - `prereq-term` - the term from which prereqs will be used for the prereq tree.
    - `prereqs`, `plans`, `majors` - if the paths to the new files changed.

1.  `university.py`: Update these variables:

    - `prereqs_file`, `plans_file`, `majors_file` - if the paths to the new files changed.
    - `curriculum_priority`, `college_codes`, `college_names` - if there's a new college. It doesn't particularly matter where the college goes in `curriculum_priority`.

1.  You may need to get a new version of `isis_major_code_list.csv` for any new majors.

1.  Run `make`. This will update the web report files in `reports/output/` as well as CSV files used in the Tableau views.

1.  Update [ucsd-degree-plans](https://github.com/SheepTester-forks/ucsd-degree-plans) using the commands in [§ What's in other repos](#whats-in-other-repos).

1.  Clone [curricular-analytics-graph](https://github.com/SheepTester-forks/curricular-analytics-graph) and build it.
    <!-- See [curricular-analytics-graph § Getting protected data (UCSD only)](https://github.com/SheepTester-forks/curricular-analytics-graph?tab=readme-ov-file#getting-protected-data-ucsd-only). -->

1.  **Web reports**: Update the views on the [EI website](https://educationalinnovation.ucsd.edu/ca-views/).

    1.  Navigate to the [`/_files/` folder for the Educational-Innovation site on Cascade CMS](https://cms.ucsd.edu/entity/open.act?id=bbd5a01eac1a010c51a0f38fa018ce21&type=folder).

    1.  Copy and paste the contents of [cms-replace-file.js](./cms-replace-file.js) into the DevTools console; this adds a file upload button to each file.

        cms-replace-file.js exists because Cascade CMS only lets you use their HTML text editor to edit the file, and it can get laggy with large HTML files.

    1.  Then replace the individual HTML files as needed from [reports/output/](./reports/output/) (their file names are the same).

    1.  Replace plan-graph.html and plan-graph-\*\*\*\*\*\*.html with curricular-analytics-graph/dist/plan-graph.html.

    1.  Edit the "Last updated" dates on all the pages under [/curricular-analytics/views/](https://educationalinnovation.ucsd.edu/curricular-analytics/views/).

<!-- 1.  ~~**Uploading to Curricular Analytics**: Run `python3 parse.py <year>` to get a list of major codes to upload. Paste them into `files/upload.sh` and run `bash files/upload.sh`.~~ We no longer upload to Curricular Analytics because we have our own [graph renderer now](https://github.com/SheepTester-forks/curricular-analytics-graph), which was handled in the previous step. -->

1.  **Tableau**: I don't really remember how to update the views on Tableau anymore (I think Arturo handles that), but I just remember it's quite a pain.

1.  **Systematically flagged issues**: To share automatically flagged issues in the degree plans, open [files/flagged_issues.html](./files/flagged_issues.html) in the browser, then copy and paste it into a Google Doc. Remove false positives as needed.
