"""
Output a JSON file with the specified curriculum to stdout. This was intended to
be compared with equivalent output from Python.

::ca::check

julia DebugOutput.jl 2016 BI29
julia DebugOutput.jl 2016 BI29 SI
"""
module DebugOutput

include("Output.jl")

import CurricularAnalytics: pre, co
import JSON
import .Output: colleges, output, plans, termname

is_curriculum = length(ARGS) == 2

degree_plan = if is_curriculum
  year, major = ARGS
  degree_plans = output(parse(Int, year), major)
  curriculum_college = first(
    college
    for college in ["TH", "WA", "SN", "MU", "FI", "RE", "SI"]
    if college ∈ keys(degree_plans) && !(college == "SN" && year < 2020)
  )
  degree_plans[curriculum_college]
else
  year, major, college = ARGS
  output(Int(year), major)[college]
end

courses = Dict(
  course.id => course
  for term in degree_plan.terms
  for course in term.courses
  if !is_curriculum || course.prefix == "" || course.institution != "DEPARTMENT"
)
println(JSON.json(Dict(
  "type" => if is_curriculum
    "curriculum"
  else
    "degree_plan"
  end,
  "terms" => [
    [
      Dict(
        "course_name" => course.name,
        "subject" => course.prefix,
        "number" => course.num,
        "units" => course.credit_hours,
      )
      for course in term.courses
      if !is_curriculum || course.prefix == "" || course.institution != "DEPARTMENT"
    ]
    for term in degree_plan.terms
  ],
  "prereqs" => [
    Dict(
      "requisite" => courses[prereq].name,
      "satisfies" => course.name,
      "type" => if type == pre
        "prereq"
      elseif type == co
        "coreq"
      else
        "other"
      end,
    )
    for (course_id, course) in courses
    for (prereq, type) in course.requisites
    if prereq ∈ keys(courses)
  ],
)))

end
