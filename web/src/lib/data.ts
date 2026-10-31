// Loads the static data exported by `SolomonIslandsDataMap.export_static` (nbs/08_export_static.ipynb)
// and re-implements the small getters the Dash callbacks used (`get_census`, `get_pop`, ...).
import type { FeatureCollection, Geometry } from "geojson"

export type Geo = "Province" | "Constituency" | "Ward"
export type DataType = "Total" | "Proportion"

export interface Meta {
  geoLevels: Geo[]
  dataTypes: DataType[]
  locations: Record<Geo, string[]>
  censusVars: Record<string, string[]>
  populationVars: Record<string, string[]>
  ages: string[]
  popYears: number[]
  elections: string[]
  elecYears: Record<string, number[]>
  partyColors: Record<string, string>
}

export interface Census {
  columns: [string, string][]
  data: Record<Geo, Record<string, Record<DataType, (number | null)[]>>>
}

/** [location, year, age, type, ...values] where values line up with `measures` */
export type PopRow = [string, number, string, DataType, ...number[]]
export interface Population {
  variable: string
  measures: string[]
  fields: string[]
  rows: PopRow[]
}

export interface ElectionRow {
  Type: string
  Year: number
  Geo: string
  loc_name: string
  Candidate: string
  candParty: string
  Party: string
  Total: number
  Proportion: number
  Order: number
}
export interface Elections {
  rows: ElectionRow[]
  winners: {
    Type: string
    Year: number
    Geo: string
    loc_name: string
    party: string
  }[]
}

export type GeoJson = FeatureCollection<Geometry, { name: string; id: string }>

export interface AppData {
  meta: Meta
  census: Census
  population: Population
  elections: Elections
  geo: Record<Geo, GeoJson>
}

/** Prefix a path in `public/` with the site base (the site is served from /SolomonIslandsDataMap/) */
export function asset(path: string) {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "")
  return `${base}/${path.replace(/^\//, "")}`
}

async function getJson<T>(file: string): Promise<T> {
  const res = await fetch(asset(`data/${file}`))
  if (!res.ok) throw new Error(`Failed to load ${file}: ${res.status}`)
  return res.json() as Promise<T>
}

let cache: Promise<AppData> | undefined
export function loadData(): Promise<AppData> {
  cache ??= (async () => {
    const [meta, census, population, elections, province, constituency, ward] =
      await Promise.all([
        getJson<Meta>("meta.json"),
        getJson<Census>("census.json"),
        getJson<Population>("population.json"),
        getJson<Elections>("elections.json"),
        getJson<GeoJson>("geo_province.geojson"),
        getJson<GeoJson>("geo_constituency.geojson"),
        getJson<GeoJson>("geo_ward.geojson"),
      ])
    return {
      meta,
      census,
      population,
      elections,
      geo: { Province: province, Constituency: constituency, Ward: ward },
    }
  })()
  return cache
}

// ---------------------------------------------------------------- Census

function censusIndex(census: Census, variable: string, measure: string) {
  return census.columns.findIndex(([v, m]) => v === variable && m === measure)
}

/** Value of one census measure for every location of a geography (the map data) */
export function censusByLocation(
  d: AppData,
  geo: Geo,
  variable: string,
  measure: string,
  type: DataType
): Map<string, number | null> {
  const i = censusIndex(d.census, variable, measure)
  const out = new Map<string, number | null>()
  for (const [loc, values] of Object.entries(d.census.data[geo]))
    out.set(loc, values[type][i] ?? null)
  return out
}

/** All measures of a census variable for one location */
export function censusVariable(
  d: AppData,
  geo: Geo,
  variable: string,
  loc: string,
  type: DataType
) {
  const measures = d.meta.censusVars[variable]
  const row = d.census.data[geo][loc]?.[type] ?? []
  return measures.map((m) => row[censusIndex(d.census, variable, m)] ?? null)
}

/** Measures of a census variable aggregated over the whole country, as in `get_census(agg=True)` */
export function censusVariableTotal(
  d: AppData,
  geo: Geo,
  variable: string,
  type: DataType
) {
  const measures = d.meta.censusVars[variable]
  const sums = measures.map((m) => {
    const i = censusIndex(d.census, variable, m)
    return Object.values(d.census.data[geo]).reduce(
      (s, v) => s + (v.Total[i] ?? 0),
      0
    )
  })
  if (type === "Total") return sums
  if (variable === "Key Statistics") {
    // Same special case as the Dash app, proportions of "key statistics" are not meaningful
    return measures.map((m) =>
      m === "Male population" ? 0.513 : m === "Female population" ? 0.487 : 1
    )
  }
  const total = sums.reduce((a, b) => a + b, 0)
  return sums.map((s) => (total ? s / total : 0))
}

// ---------------------------------------------------------------- Population projections

export function popMeasureIndex(d: AppData, measure: string) {
  return 4 + d.population.measures.indexOf(measure)
}

/** Sum of a population measure per province and year for the selected ages (the map data) */
export function popByLocationYear(
  d: AppData,
  measure: string,
  type: DataType,
  ages: string[]
) {
  const i = popMeasureIndex(d, measure)
  const ageSet = new Set(ages)
  const out = new Map<number, Map<string, number>>()
  for (const r of d.population.rows) {
    if (r[3] !== type || !ageSet.has(r[2])) continue
    const year = out.get(r[1]) ?? new Map<string, number>()
    year.set(r[0], (year.get(r[0]) ?? 0) + (r[i] as number))
    out.set(r[1], year)
  }
  return out
}

/** Key figure: population for a year, measure, ages and (optional) provinces */
export function popTotal(
  d: AppData,
  year: number,
  measure: string,
  type: DataType,
  ages: string[],
  locs: string[]
) {
  const i = popMeasureIndex(d, measure)
  const ageSet = new Set(ages)
  const locSet = new Set(locs)
  let sum = 0
  for (const r of d.population.rows) {
    if (r[3] !== type || r[1] !== year || !ageSet.has(r[2])) continue
    if (locs.length && !locSet.has(r[0])) continue
    sum += r[i] as number
  }
  return sum
}

/** Males and females by age for the population pyramid */
export function popPyramid(
  d: AppData,
  year: number,
  type: DataType,
  locs: string[]
) {
  const mi = popMeasureIndex(d, "Males")
  const fi = popMeasureIndex(d, "Females")
  const locSet = new Set(locs)
  const byAge = new Map(
    d.meta.ages.map((a) => [a, { age: a, male: 0, female: 0 }])
  )
  for (const r of d.population.rows) {
    if (r[3] !== type || r[1] !== year) continue
    if (locs.length && !locSet.has(r[0])) continue
    const a = byAge.get(r[2])!
    a.male += r[mi] as number
    a.female += r[fi] as number
  }
  return [...byAge.values()]
}

// ---------------------------------------------------------------- Elections

export function electionResults(
  d: AppData,
  election: string,
  year: number,
  loc: string
) {
  return d.elections.rows
    .filter(
      (r) =>
        r.Type === election &&
        r.Year === year &&
        r.loc_name === loc &&
        r.Geo === "Constituency"
    )
    .sort((a, b) => b.Total - a.Total)
}

export function electionWinners(d: AppData, election: string, year: number) {
  const winners = new Map<
    string,
    { party: string; candidate: string; total: number; proportion: number }
  >()
  for (const r of d.elections.rows) {
    if (r.Type !== election || r.Year !== year || r.Order !== 0) continue
    winners.set(r.loc_name, {
      party: r.Party,
      candidate: r.candParty,
      total: r.Total,
      proportion: r.Proportion,
    })
  }
  return winners
}

// ---------------------------------------------------------------- Formatting

export const fmtInt = (v: number | null | undefined) =>
  v == null ? "–" : Math.round(v).toLocaleString("en-AU")
export const fmtPct = (v: number | null | undefined, digits = 1) =>
  v == null ? "–" : `${(v * 100).toFixed(digits)}%`
export const fmt = (v: number | null | undefined, type: DataType) =>
  type === "Proportion" ? fmtPct(v) : fmtInt(v)
