using CurricularAnalytics

colleges = ["RE", "MU", "TH", "WA", "FI", "SI", "SN"]

courses = Dict()

function non_major_unit_count(plan::DegreePlan)
  non_major_unit_count = 0
  if (isdefined(plan, :additional_courses))
    for course in plan.additional_courses
      non_major_unit_count += course.credit_hours
    end
  end
  non_major_unit_count
end

mutable struct CourseStats
  max_centrality::Int
  max_centrality_major::String
end

output = open("./files/metrics.csv", "w")
write(output, "Major,College,Number of GEs,Complexity,Max centrality,Max centrality course,Longest path,Elective units, Total Units, Highest Unit Term Load, Highest Unit Term, Lowest Unit Term Load, Lowest Unit Term, Units not in Major, Units in Major, Max Complexity, Max Complexity Course, Total Number of Courses, Number of Courses with no Prereqs\n")
flush(output)

iselective(course::Course) = occursin(r"\belective\b"i, course.name) && !occursin(r"\bmuir\b"i, course.name)

for major in readdir("./files/output/")
  for college in colleges
    print("\r$major $college")
    plan = nothing
    try
      plan = read_csv("./files/output/$major/$college.csv")
    catch error
      if error isa SystemError
        # Ignore if college degree plan doesn't exist
        continue
      else
        throw(error)
      end
    end
    # Convert to curriculum
    # Is this necessary? the plan has a curriculum already generated. 
    curriculum = Curriculum(plan.name, [course for term in plan.terms for course in term.courses])
    try
      basic_metrics(plan)
      basic_metrics(curriculum)
    catch error
      # BoundsError: attempt to access 0-element Vector{Vector{Course}} at index [1]
      # For curricula like AN26 with no prerequisites, presumably
      if !(error isa BoundsError)
        throw(error)
      end
    end

    write(output, "$major,$college")
    ges = []
    electives = 0
    try
      # UndefRefError: access to undefined reference
      # plan.additional_courses doesn't exist for PS33 MU
      ges = filter(plan.additional_courses) do course
        # Removes: ELECTIVE, UD ELECTIVE, UD AHI or UD ELECTIVE, Elective
        # Does not remove: MUIR UD Elective,
        !iselective(course)
      end
      electives = sum((course.credit_hours for course in plan.additional_courses if iselective(course)), init=0)
    catch error
      if !(error isa UndefRefError)
        throw(error)
      end
    end
    write(output, ",$(length(ges))")
    write(output, ",$(curriculum.metrics["complexity"][1])")
    write(output, ",$(curriculum.metrics["max. centrality"])")
    write(output, ",$(curriculum.metrics["max. centrality courses"][1].name)")
    write(output, isempty(curriculum.metrics["longest paths"]) ? "," : ",$(length(curriculum.metrics["longest paths"][1]))")
    write(output, ",$electives")
    write(output, ",$(plan.metrics["total credit hours"])") # or plan.credit_hours
    write(output, ",$(plan.metrics["max. credits in a term"])")
    write(output, ",$(plan.metrics["max. credit term"])")
    write(output, ",$(plan.metrics["min. credits in a term"])")
    write(output, ",$(plan.metrics["min. credit term"])")
    write(output, ",$(non_major_unit_count(plan))")
    write(output, ",$(plan.credit_hours - non_major_unit_count(plan))")
    write(output, ",$(curriculum.metrics["max. complexity"])")
    write(output, ",$(curriculum.metrics["max. centrality courses"][1].name)")
    write(output, ",$(curriculum.num_courses)")
    write(output, ",$(length( filter(x-> x==1, curriculum.metrics["delay factor"][2])))") # courses with a delay factor of 1 are the only course in the longest path they're in, i.e. have no prereqs AND no unblocked classes (hence they satisfy the condition no prereqs)
    write(output, "\n")
    flush(output)

    for (i, course) in enumerate(curriculum.courses)
      if isempty(course.prefix)
        continue
      end
      course_code = "$(course.prefix) $(course.num)"
      course_centrality = centrality(curriculum, i)
      stats = get!(courses, course_code) do
        CourseStats(course_centrality, "$major $college")
      end
      if course_centrality > stats.max_centrality
        stats.max_centrality = course_centrality
        stats.max_centrality_major = "$major $college"
      end
    end
  end
end

close(output)
println()

open("./files/courses.csv", "w") do file
  write(file, "Course,Max centrality,Major with max centrality\n")

  for course_code in sort(collect(keys(courses)))
    stats = courses[course_code]
    write(file, "$course_code,$(stats.max_centrality),$(stats.max_centrality_major)\n")
  end
end
