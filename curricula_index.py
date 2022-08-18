from departments import departments, dept_schools
from parse import major_codes
from upload import track_uploaded_curricula

print("School,Department,Major,Year,URL")

for year in range(2015, 2023):
    with track_uploaded_curricula(year) as curricula:
        for major_code, curriculum_id in curricula.items():
            department = major_codes()[major_code].department
            department_name = departments.get(department) or "UNKNOWN"
            print(
                ",".join(
                    [
                        f'"{dept_schools.get(department) or department_name}"',
                        f'"{department_name}"',
                        major_code,
                        str(year),
                        f"https://curricularanalytics.org/curriculums/{curriculum_id}",
                    ]
                )
            )