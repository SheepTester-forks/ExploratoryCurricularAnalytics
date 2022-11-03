/** @jsxImportSource https://esm.sh/preact@10.10.6 */
/// <reference no-default-lib="true"/>
/// <reference lib="dom" />
/// <reference lib="deno.ns" />

import { render } from 'https://esm.sh/preact@10.10.6'
import { useState } from 'https://esm.sh/preact@10.10.6/hooks'

type BeforeAfter<T> = [T, T]

type Term = [number, string]

type Change =
  | {
      type: 'removed' | 'added'
      course: string
      units: number
      term: Term
    }
  | {
      type: 'changed'
      course: string
      changes: {
        title?: BeforeAfter<string>
        units?: BeforeAfter<number>
        term?: BeforeAfter<Term>
        type?: BeforeAfter<'COLLEGE' | 'DEPARTMENT'>
        overlap?: BeforeAfter<boolean>
      }
    }

type YearDiff = {
  changes: Change[]
  units?: BeforeAfter<number>
  year: number
  url: string
  complexity?: BeforeAfter<number>
}

type PlanDiffs = {
  changes: YearDiff[]
  first: {
    year: number
    url: string
  }
}

type Diffs = {
  [school: string]: {
    [department: string]: {
      [major: string]: {
        [college: string]: PlanDiffs
      }
    }
  }
}

type Diff = { name: string; diff: PlanDiffs }

const collegeNames = [
  'Revelle',
  'Muir',
  'Marshall',
  'Warren',
  'ERC',
  'Sixth',
  'Seventh'
]

const byKeyLocale = <T,>([a]: [string, T], [b]: [string, T]) =>
  a.localeCompare(b)

const getMetric = {
  maxUnitChange (diff: PlanDiffs) {
    return Math.max(
      ...diff.changes.map(year =>
        year.units ? Math.abs(year.units[1] - year.units[0]) : 0
      )
    )
  },
  maxComplexityChange (diff: PlanDiffs) {
    return Math.max(
      ...diff.changes.map(year =>
        year.complexity ? Math.abs(year.complexity[1] - year.complexity[0]) : 0
      )
    )
  },
  numUnitChanges (diff: PlanDiffs) {
    return diff.changes.filter(year => year.units).length
  }
}

type TableProps = {
  diffs: Diffs
  selected?: string
  onSelect: (diff: Diff) => void
}
function Table ({ diffs, selected, onSelect }: TableProps) {
  const [metric, setMetric] = useState<keyof typeof getMetric>('maxUnitChange')
  let max = 0
  for (const departments of Object.values(diffs)) {
    for (const majors of Object.values(departments)) {
      for (const plans of Object.values(majors)) {
        for (const diffs of Object.values(plans)) {
          const value = getMetric[metric](diffs)
          if (value > max) {
            max = value
          }
        }
      }
    }
  }
  return (
    <>
      <table>
        <tr>
          <th scope='row'>School</th>
          <th scope='row'>Department</th>
          <th scope='row'>Major</th>
          {collegeNames.map(name => (
            <th scope='row'>{name}</th>
          ))}
        </tr>
        {Object.entries(diffs)
          .sort(byKeyLocale)
          .flatMap(([school, departments]) =>
            Object.entries(departments)
              .sort(byKeyLocale)
              .flatMap(([department, majors], j) =>
                Object.entries(majors)
                  .sort(byKeyLocale)
                  .flatMap(([major, colleges], k) => {
                    // https://stackoverflow.com/a/36665251
                    const [code, ...name] = major.split(' ')
                    return (
                      <tr>
                        {j === 0 && k === 0 && (
                          <th
                            scope='col'
                            rowSpan={Object.values(departments)
                              .map(majors => Object.keys(majors).length)
                              .reduce((a, b) => a + b, 0)}
                          >
                            {school}
                          </th>
                        )}
                        {k === 0 && (
                          <th scope='col' rowSpan={Object.keys(majors).length}>
                            {department}
                          </th>
                        )}
                        <td>
                          <abbr title={name.join(' ') || undefined}>
                            {code}
                          </abbr>
                        </td>
                        {collegeNames.map(college => (
                          <td
                            style={{
                              backgroundColor:
                                college in colleges
                                  ? `rgba(0, 0, 255, ${
                                      getMetric[metric](colleges[college]) / max
                                    })`
                                  : null
                            }}
                          >
                            {college in colleges && (
                              <button
                                disabled={selected === `${major} / ${college}`}
                                onClick={() =>
                                  onSelect({
                                    name: `${major} / ${college}`,
                                    diff: colleges[college]
                                  })
                                }
                              >
                                View
                              </button>
                            )}
                          </td>
                        ))}
                      </tr>
                    )
                  })
              )
          )}
      </table>
      <p class='select-metric'>
        Color by{' '}
        <select
          value={metric}
          onChange={e => {
            if (
              e.currentTarget.value === 'maxUnitChange' ||
              e.currentTarget.value === 'maxComplexityChange' ||
              e.currentTarget.value === 'numUnitChanges'
            ) {
              setMetric(e.currentTarget.value)
            }
          }}
        >
          <option value='maxUnitChange'>largest unit change</option>
          <option value='maxComplexityChange'>largest complexity change</option>
          <option value='numUnitChanges'>frequency of unit changes</option>
        </select>
      </p>
    </>
  )
}

type ChangeProps<T> = {
  change: BeforeAfter<T>
  map?: (value: T) => string
}
function Change<T> ({ change: [before, after], map = String }: ChangeProps<T>) {
  return (
    <span class='change'>
      {map(before)} <span class='arrow'>→</span> {map(after)}
    </span>
  )
}

function displayTerm ([year, quarter]: Term) {
  return `Y${year} ${quarter}`
}

type ChangeItemProps = {
  change: Change
}
function ChangeItem ({ change }: ChangeItemProps) {
  return (
    <li class={`change-item ${change.type}`}>
      {change.type === 'changed' && change.changes.title ? (
        <Change change={change.changes.title} />
      ) : (
        change.course
      )}
      {change.type !== 'changed' && (
        <>
          {' '}
          <span class='info'>
            ({displayTerm(change.term)} · {change.units} units)
          </span>
        </>
      )}
      {change.type === 'changed' && change.changes.units && (
        <>
          {' '}
          · <Change change={change.changes.units} /> units
        </>
      )}
      {change.type === 'changed' && change.changes.term && (
        <>
          {' '}
          · <Change change={change.changes.term} map={displayTerm} />
        </>
      )}
      {change.type === 'changed' && change.changes.type && (
        <>
          {' '}
          ·{' '}
          <Change
            change={change.changes.type}
            map={type => type.toLowerCase()}
          />
          -type course
        </>
      )}
      {change.type === 'changed' && change.changes.overlap && (
        <>
          {' '}
          ·{' '}
          <span class='change'>
            {change.changes.overlap[1] ? 'now' : 'no longer'}
          </span>{' '}
          overlaps GE
        </>
      )}
    </li>
  )
}

const isMajorChange = (change: Change) =>
  change.type !== 'changed' || change.changes.units !== undefined

function YearDiff ({ year, url, units, complexity, changes }: YearDiff) {
  const majorChanges = changes.filter(isMajorChange)
  const minorChanges = changes.filter(change => !isMajorChange(change))
  return (
    <>
      <h2>
        Changes in <a href={url}>{year}</a>
        {(units || complexity) && (
          <>
            {' '}
            <span class={`units ${units ? '' : 'complexity'}`}>
              (
              {units && (
                <>
                  {<Change change={units} />}, {units[1] > units[0] && '+'}
                  {units[1] - units[0]} units
                </>
              )}
              {units && complexity && '; '}
              {complexity && (
                <span class='complexity'>
                  {<Change change={complexity} />},{' '}
                  {complexity[1] > complexity[0] && '+'}
                  {complexity[1] - complexity[0]} complexity
                </span>
              )}
              )
            </span>
          </>
        )}
      </h2>
      {changes.length === 0 && (
        <p class='changes'>
          <em>No changes.</em>
        </p>
      )}
      {majorChanges.length > 0 && (
        <ul class='changes'>
          {majorChanges.map(change => (
            <ChangeItem change={change} />
          ))}
        </ul>
      )}
      {minorChanges.length > 0 && (
        <details>
          <summary>View smaller changes</summary>
          <ul class='changes'>
            {minorChanges.map(change => (
              <ChangeItem change={change} />
            ))}
          </ul>
        </details>
      )}
    </>
  )
}

function Diff ({ name, diff }: Diff) {
  return (
    <div>
      <h1>{name}</h1>
      <p>
        <em>
          Starts in <a href={diff.first.url}>{diff.first.year}</a>.
        </em>
      </p>
      {diff.changes.map(change => (
        <YearDiff {...change} />
      ))}
    </div>
  )
}

type AppProps = {
  diffs: Diffs
}
function App ({ diffs }: AppProps) {
  const [diff, setDiff] = useState<Diff | null>(null)
  return (
    <>
      <div class='side'>
        <Table diffs={diffs} selected={diff?.name} onSelect={setDiff} />
      </div>
      <div class='side diff'>
        {diff ? (
          <Diff {...diff} />
        ) : (
          <p>
            <em>Select a major/college to view its changes.</em>
          </p>
        )}
      </div>
    </>
  )
}

render(
  <App diffs={JSON.parse(document.getElementById('diffs')!.textContent!)} />,
  document.getElementById('root')!
)
