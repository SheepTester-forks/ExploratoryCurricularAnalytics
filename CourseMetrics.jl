# Outputs a CSV of every course in every year-major and lists its metrics in the
# curriculum (based on Marshall's degree plan). This is for reports #1, #2, and
# #3.
#
# ::tableau::new
#
# julia CourseMetrics.jl

module CourseMetrics

include("Output.jl")
include("Utils.jl")

import CurricularAnalytics: blocking_factor, centrality, complexity, Curriculum, delay_factor
import .Output: output, plans, termname
import .Utils: convert, writerow

open("./files/courses_fa12.csv", "w") do file
  writerow(file, [
    "Year",
    "Major",
    "Course",
    "Complexity",
    "Centrality",
    "Year taken in plan",
    "Blocking factor",
    "Delay factor",
  ])

  for year in 2015:2050
    if year ∉ keys(plans)
      break
    end
    for major in sort(collect(keys(plans[year])))
      degree_plans = output(year, major)
      curriculum_college = first(
        college
        for college in ["TH", "WA", "SN", "MU", "FI", "RE", "SI"]
        if college ∈ keys(degree_plans) && !(college == "SN" && year < 2020)
      )
      curriculum = convert(Curriculum, degree_plans[curriculum_college])
      for (i, course) in enumerate(curriculum.courses)
        if course.prefix == "" || course.institution != "DEPARTMENT"
          continue
        end

        writerow(file, [
          string(year), # Year
          major, # Major
          "$(course.prefix) $(course.num)", # Course
          string(complexity(curriculum, i)), # Complexity
          string(centrality(curriculum, i)), # Centrality
          # Use the curriculum college's year, even though it could vary between
          # colleges
          string((findfirst(course ∈ term.courses for term in degree_plans[curriculum_college].terms) - 1) ÷ 3 + 1),
          string(blocking_factor(curriculum, i)), # Blocking factor
          string(delay_factor(curriculum, i)), # Delay factor
        ])
      end
    end
  end
end

end
