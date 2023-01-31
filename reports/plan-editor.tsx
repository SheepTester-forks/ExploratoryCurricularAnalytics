/** @jsxImportSource https://esm.sh/preact@10.11.2 */
/// <reference no-default-lib="true"/>
/// <reference lib="dom" />
/// <reference lib="deno.ns" />

import { render } from 'https://esm.sh/preact@10.11.2'
import {
  useEffect,
  useRef,
  useState
} from 'https://esm.sh/preact@10.11.2/hooks'
import type { JSX } from 'https://esm.sh/preact@10.11.2/jsx-runtime'

type CourseCode = string
type Prereqs = Record<CourseCode, CourseCode[][]>

type Course = {
  title: string
  units: string
  requirement: {
    college: boolean
    major: boolean
  }
}
type TermPlan = Course[]
type YearPlan = TermPlan[]
type AcademicPlan = {
  startYear: string
  type: '4-year' | 'transfer'
  years: YearPlan[]
  name: string
}

type DragState = {
  pointerId: number
  width: number
  height: number
  offsetX: number
  offsetY: number
  pointerX: number
  pointerY: number
}
type CourseProps = {
  course: Course
  onCourse: (course: Course) => void
  onRemove: () => void
  new?: boolean
}
function Course ({ course, onCourse, onRemove, new: isNew }: CourseProps) {
  const [dragState, setDragState] = useState<DragState | null>(null)

  const onPointerEnd = (e: JSX.TargetedPointerEvent<HTMLElement>) => {
    if (e.pointerId === dragState?.pointerId) {
      setDragState(null)
    }
  }

  return (
    <li
      class={`course-editor ${isNew ? 'add-course' : ''} ${
        dragState ? 'dragged' : ''
      }`}
      style={
        dragState
          ? {
              left: `${dragState.pointerX - dragState.offsetX}px`,
              top: `${dragState.pointerY - dragState.offsetY}px`,
              width: `${dragState.width}px`,
              height: `${dragState.height}px`
            }
          : {}
      }
    >
      <input
        class='course-field course-title'
        type='text'
        list='courses'
        value={course.title}
        onInput={e => onCourse({ ...course, title: e.currentTarget.value })}
        placeholder={isNew ? 'Add a course' : 'Course name'}
      />
      {!isNew && (
        <input
          class='course-field course-units term-units'
          type='text'
          inputMode='numeric'
          pattern='[0-9]*'
          value={course.units}
          onInput={e => onCourse({ ...course, units: e.currentTarget.value })}
          onChange={e =>
            onCourse({
              ...course,
              units: Number.isFinite(+e.currentTarget.value)
                ? +e.currentTarget.value < 0
                  ? '0'
                  : String(+e.currentTarget.value)
                : '4'
            })
          }
        />
      )}
      {!isNew && (
        <span
          class='term-icon-btn drag-btn'
          title='Move course'
          onPointerDown={e => {
            if (!dragState) {
              e.currentTarget.setPointerCapture(e.pointerId)
              const rect =
                e.currentTarget.parentElement!.getBoundingClientRect()
              setDragState({
                pointerId: e.pointerId,
                width: rect.width,
                height: rect.height,
                offsetX: e.clientX - rect.left,
                offsetY: e.clientY - rect.top,
                pointerX: e.clientX,
                pointerY: e.clientY
              })
            }
          }}
          onPointerMove={e => {
            if (e.pointerId === dragState?.pointerId) {
              setDragState({
                ...dragState,
                pointerX: e.clientX,
                pointerY: e.clientY
              })
            }
          }}
          onPointerUp={onPointerEnd}
          onPointerCancel={onPointerEnd}
        >
          ⠿
        </span>
      )}
    </li>
  )
}

const emptyCourse = {
  title: '',
  units: '4',
  requirement: { college: false, major: false }
}
type TermProps = {
  name: string
  plan: TermPlan
  onPlan: (plan: TermPlan) => void
}
function Term ({ name, plan, onPlan }: TermProps) {
  const termUnits = plan.reduce((cum, curr) => cum + +curr.units, 0)
  return (
    <section class='term-editor'>
      <h3
        class={`heading term-heading ${
          termUnits < 12
            ? 'term-units-error'
            : termUnits > 18
            ? 'term-units-warning'
            : ''
        }`}
      >
        {name}{' '}
        <span class='total-units term-units'>
          Units:{' '}
          <span
            class={
              termUnits < 12 || termUnits > 18 ? 'units units-bad' : 'units'
            }
          >
            {termUnits}
          </span>
        </span>
        <button
          class='term-icon-btn add-course-btn'
          title='Add course'
          onClick={() => onPlan([...plan, emptyCourse])}
        >
          +
        </button>
      </h3>
      <ul class='courses'>
        {[...plan, emptyCourse].map((course, i) => (
          <Course
            course={course}
            onCourse={newCourse =>
              onPlan(
                i === plan.length
                  ? [...plan, newCourse]
                  : plan.map((course, index) =>
                      index === i ? newCourse : course
                    )
              )
            }
            onRemove={() => onPlan(plan.filter((_, index) => i !== index))}
            new={i === plan.length}
            key={i}
          />
        ))}
      </ul>
    </section>
  )
}

const termNames = ['Fall', 'Winter', 'Spring']
type YearProps = {
  planStartYear: string
  index: number
  plan: YearPlan
  onPlan: (plan: YearPlan) => void
  onYear?: ((year: string) => void) | null
}
function Year ({ planStartYear, index, plan, onPlan, onYear }: YearProps) {
  return (
    <section class='year-editor'>
      <h2 class='heading year-heading'>
        <strong>Year {index + 1}</strong>:{' '}
        {/* TODO: Move the start year input elsewhere. It's kind of unintuitive where it is now */}
        {onYear ? (
          <input
            class='start-year'
            type='text'
            inputMode='numeric'
            pattern='[0-9]*'
            aria-label='Starting year'
            value={planStartYear}
            onInput={e => {
              onYear(e.currentTarget.value)
            }}
            onChange={e => {
              onYear(
                Number.isFinite(+e.currentTarget.value)
                  ? String(Math.trunc(+e.currentTarget.value))
                  : String(new Date().getFullYear())
              )
            }}
          />
        ) : (
          +planStartYear + index
        )}
        –{+planStartYear + index + 1}{' '}
        <span class='total-units'>
          Annual units:{' '}
          <span class='units'>
            {plan.reduce(
              (cum, curr) =>
                cum + curr.reduce((cum, curr) => cum + +curr.units, 0),
              0
            )}
          </span>
        </span>
      </h2>
      <div class='terms'>
        {plan.map((term, i) => (
          <Term
            name={termNames[i]}
            plan={term}
            onPlan={newPlan =>
              onPlan(plan.map((term, index) => (index === i ? newPlan : term)))
            }
            key={i}
          />
        ))}
      </div>
    </section>
  )
}

type EditorProps = {
  plan: AcademicPlan
  onPlan: (plan: AcademicPlan) => void
}
function Editor ({ plan, onPlan }: EditorProps) {
  return (
    <div class='plan-editor'>
      {plan.years.map((year, i) => (
        <Year
          planStartYear={plan.startYear}
          index={i}
          plan={year}
          onPlan={newPlan =>
            onPlan({
              ...plan,
              years: plan.years.map((year, index) =>
                index === i ? newPlan : year
              )
            })
          }
          onYear={i === 0 ? startYear => onPlan({ ...plan, startYear }) : null}
          key={i}
        />
      ))}
    </div>
  )
}

type AppProps = {
  prereqs: Prereqs
  initPlan: AcademicPlan
}
function App ({ prereqs, initPlan }: AppProps) {
  const [plan, setPlan] = useState(initPlan)

  return (
    <>
      <div class='info'>
        <input
          class='plan-name'
          type='text'
          placeholder='Plan name'
          aria-label='Plan name'
          value={plan.name}
          onInput={e => setPlan({ ...plan, name: e.currentTarget.value })}
        />
        <span class='total-units plan-units'>
          Total units:{' '}
          <span class='units'>
            {plan.years.reduce(
              (cum, curr) =>
                cum +
                curr.reduce(
                  (cum, curr) =>
                    cum + curr.reduce((cum, curr) => cum + +curr.units, 0),
                  0
                ),
              0
            )}
          </span>
        </span>
      </div>
      <Editor plan={plan} onPlan={setPlan} />
      <datalist id='courses'>
        {Object.keys(prereqs).map(code => (
          <option value={code} key={code} />
        ))}
      </datalist>
    </>
  )
}

render(
  <App
    prereqs={JSON.parse(document.getElementById('prereqs')!.textContent!)}
    initPlan={{
      startYear: '2021',
      type: '4-year',
      years: [
        [
          [
            {
              title: 'CSE 8A',
              units: '4',
              requirement: { college: true, major: true }
            },
            {
              title: 'MATH 20A',
              units: '4',
              requirement: { college: true, major: true }
            },
            {
              title: 'CAT 1',
              units: '4',
              requirement: { college: true, major: false }
            },
            {
              title: 'GE',
              units: '4',
              requirement: { college: true, major: false }
            }
          ],
          [
            {
              title: 'CSE 8B',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'MATH 20B',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 20',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CAT 2',
              units: '6',
              requirement: { college: true, major: false }
            }
          ],
          [
            {
              title: 'PHYS 2A',
              units: '4',
              requirement: { college: true, major: true }
            },
            {
              title: 'MATH 18',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 12',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 15L',
              units: '2',
              requirement: { college: false, major: true }
            },
            {
              title: 'CAT 3',
              units: '6',
              requirement: { college: true, major: false }
            }
          ]
        ],
        [
          [
            {
              title: 'ECE 35',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'PHYS 2B',
              units: '4',
              requirement: { college: true, major: true }
            },
            {
              title: 'MATH 20C',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 21',
              units: '4',
              requirement: { college: false, major: true }
            }
          ],
          [
            {
              title: 'PHYS 2C',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 30',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'MATH 20D',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'ECE 45',
              units: '4',
              requirement: { college: false, major: true }
            }
          ],
          [
            {
              title: 'ECE 65',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 100',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'ECE 109',
              units: '4',
              requirement: { college: true, major: true }
            },
            {
              title: 'GE',
              units: '4',
              requirement: { college: true, major: false }
            }
          ]
        ],
        [
          [
            {
              title: 'CSE 110',
              units: '4',
              requirement: { college: true, major: true }
            },
            {
              title: 'CSE / ECE ELECTIVE',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 101',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CAT 125',
              units: '4',
              requirement: { college: true, major: false }
            }
          ],
          [
            {
              title: 'ECE 101',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 140L',
              units: '2',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 140',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'GE / DEI',
              units: '4',
              requirement: { college: true, major: false }
            }
          ],
          [
            {
              title: 'CSE 141 (OR CSE 142)',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE 141L (OR CSE 142L)',
              units: '2',
              requirement: { college: false, major: true }
            },
            {
              title: 'TECHNICAL ELECTIVE',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'ECE 111 (OR ECE 140B)',
              units: '4',
              requirement: { college: false, major: true }
            }
          ]
        ],
        [
          [
            {
              title: 'CSE 120',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE / ECE ELECTIVE',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'GE',
              units: '4',
              requirement: { college: true, major: false }
            }
          ],
          [
            {
              title: 'ECE 108',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE / ECE ELECTIVE',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'GE',
              units: '4',
              requirement: { college: true, major: false }
            }
          ],
          [
            {
              title: 'CSE / ECE ELECTIVE',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'CSE / ECE ELECTIVE',
              units: '4',
              requirement: { college: false, major: true }
            },
            {
              title: 'GE',
              units: '4',
              requirement: { college: true, major: false }
            }
          ]
        ]
      ],
      name: '2021 CS25-Computer Engineering/Sixth'
    }}
  />,
  document.getElementById('root')!
)
