// Filter state shared by every page. Stored in the URL query string so views can be bookmarked
// and the selection carries over when moving between pages.
import * as React from "react"
import type { DataType, Geo, Meta } from "@/lib/data"

export type Page = "census" | "election" | "population" | "table"
export type Dataset = "Census" | "Population Projections"

export interface Filters {
  geo: Geo
  type: DataType
  variable: string
  measure: string
  locs: string[]
  popVariable: string
  popMeasure: string
  ages: string[]
  year: number
  election: string
  elecYear: number
  elecLoc: string
  dataset: Dataset
  rows: number
}

export function defaultFilters(meta: Meta): Filters {
  const variable = Object.keys(meta.censusVars)[0]
  const popVariable = Object.keys(meta.populationVars)[0]
  const election = meta.elections.includes("National Parliament")
    ? "National Parliament"
    : meta.elections[0]
  const years = meta.elecYears[election]
  return {
    geo: meta.geoLevels[0],
    type: meta.dataTypes[0],
    variable,
    measure: meta.censusVars[variable][0],
    locs: [],
    popVariable,
    popMeasure: meta.populationVars[popVariable].includes("Total")
      ? "Total"
      : meta.populationVars[popVariable][0],
    ages: meta.ages,
    year: meta.popYears.includes(2025)
      ? 2025
      : meta.popYears[meta.popYears.length - 1],
    election,
    elecYear: years[years.length - 1],
    elecLoc: meta.locations.Constituency.includes("Central Honiara")
      ? "Central Honiara"
      : meta.locations.Constituency[0],
    dataset: "Census",
    rows: 10,
  }
}

const listKeys = ["locs", "ages"] as const
const numKeys = ["year", "elecYear", "rows"] as const

/** Read filters from the query string, ignoring anything that isn't valid for the data */
function parse(search: string, meta: Meta): Filters {
  const d = defaultFilters(meta)
  const q = new URLSearchParams(search)
  const raw: Record<string, unknown> = { ...d }
  for (const key of Object.keys(d)) {
    if (!q.has(key)) continue
    if ((listKeys as readonly string[]).includes(key)) raw[key] = q.getAll(key)
    else if ((numKeys as readonly string[]).includes(key))
      raw[key] = Number(q.get(key))
    else raw[key] = q.get(key)
  }
  const f = raw as unknown as Filters
  // validate
  if (!meta.geoLevels.includes(f.geo)) f.geo = d.geo
  if (!meta.dataTypes.includes(f.type)) f.type = d.type
  if (!meta.censusVars[f.variable]) f.variable = d.variable
  if (!meta.censusVars[f.variable].includes(f.measure))
    f.measure = meta.censusVars[f.variable][0]
  if (!meta.populationVars[f.popVariable]) f.popVariable = d.popVariable
  if (!meta.populationVars[f.popVariable].includes(f.popMeasure))
    f.popMeasure = d.popMeasure
  f.ages = f.ages.filter((a) => meta.ages.includes(a))
  if (!f.ages.length) f.ages = d.ages
  if (!meta.popYears.includes(f.year)) f.year = d.year
  if (!meta.elections.includes(f.election)) f.election = d.election
  if (!meta.elecYears[f.election].includes(f.elecYear)) f.elecYear = d.elecYear
  if (!meta.locations.Constituency.includes(f.elecLoc)) f.elecLoc = d.elecLoc
  if (f.dataset !== "Census" && f.dataset !== "Population Projections")
    f.dataset = d.dataset
  if (!(f.rows > 0)) f.rows = d.rows
  return f
}

/** Only non-default values are written to the URL */
export function toSearch(f: Filters, meta: Meta) {
  const d = defaultFilters(meta)
  const q = new URLSearchParams()
  for (const key of Object.keys(d) as (keyof Filters)[]) {
    const v = f[key]
    if (Array.isArray(v)) {
      if (JSON.stringify(v) !== JSON.stringify(d[key]))
        v.forEach((x) => q.append(key, x))
    } else if (v !== d[key]) q.set(key, String(v))
  }
  const s = q.toString()
  return s ? `?${s}` : ""
}

/** The geography actually shown on a page, population data only exists by province and elections by constituency */
export function effectiveGeo(
  page: Page,
  f: Pick<Filters, "geo" | "dataset">
): Geo {
  if (page === "population") return "Province"
  if (page === "election") return "Constituency"
  if (page === "table" && f.dataset === "Population Projections")
    return "Province"
  return f.geo
}

export function useFilters(meta: Meta | undefined) {
  const [filters, setFilters] = React.useState<Filters | undefined>()
  // Initialise from the URL as soon as the data (and so the valid options) is known
  if (meta && !filters) setFilters(parse(window.location.search, meta))

  React.useEffect(() => {
    if (!meta || !filters) return
    const url =
      window.location.pathname + toSearch(filters, meta) + window.location.hash
    window.history.replaceState(null, "", url)
  }, [filters, meta])

  const update = React.useCallback((patch: Partial<Filters>) => {
    setFilters((f) => (f ? { ...f, ...patch } : f))
  }, [])

  return [filters, update] as const
}
