import * as React from "react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import {
  censusByLocation,
  censusVariable,
  censusVariableTotal,
  electionResults,
  electionWinners,
  fmt,
  popByLocationYear,
  popPyramid,
  popTotal,
  type AppData,
} from "@/lib/data"
import { effectiveGeo, type Filters } from "@/lib/filters"
import { deepGradient, scaleColors, useIsDark } from "@/lib/theme"
import { ChoroplethMap } from "./ChoroplethMap"
import { CensusBarChart, ElectionBarChart, PopulationPyramid } from "./charts"

interface ViewProps {
  data: AppData
  filters: Filters
  update: (patch: Partial<Filters>) => void
}

const esc = (s: string) =>
  s.replace(
    /[&<>"]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!
  )
const tip = (title: string, rows: [string, string][]) =>
  `<div class="font-medium mb-0.5">${esc(title)}</div>` +
  rows
    .map(
      ([k, v]) =>
        `<div class="flex justify-between gap-4"><span class="text-muted-foreground">${esc(k)}</span><span class="font-mono tabular-nums">${esc(v)}</span></div>`
    )
    .join("")

const toggle = (list: string[], item: string) =>
  list.includes(item) ? list.filter((l) => l !== item) : [...list, item]

export function PageTitle({
  children,
  description,
}: {
  children: React.ReactNode
  description?: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-1">
      <h1 className="text-xl font-semibold tracking-tight text-balance sm:text-2xl">
        {children}
      </h1>
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
    </div>
  )
}

function MapCard({
  children,
  legend,
}: {
  children: React.ReactNode
  legend?: React.ReactNode
}) {
  return (
    <Card className="relative gap-0 overflow-hidden p-0">
      {children}
      {legend && (
        <div className="pointer-events-none absolute bottom-2 left-2 border bg-background/90 px-2.5 py-2 text-xs backdrop-blur">
          {legend}
        </div>
      )}
    </Card>
  )
}

function SequentialLegend({
  min,
  max,
  format,
  title,
}: {
  min: number
  max: number
  format: (v: number) => string
  title: string
}) {
  const dark = useIsDark()
  return (
    <div className="flex w-44 flex-col gap-1">
      <span className="font-medium">{title}</span>
      <div
        className="h-2.5 w-full"
        style={{ background: deepGradient(dark) }}
      />
      <div className="flex justify-between font-mono text-[10px] text-muted-foreground tabular-nums">
        <span>{format(min)}</span>
        <span>{format(max)}</span>
      </div>
    </div>
  )
}

const mapClass = "h-[46vh] min-h-[320px] w-full lg:h-[52vh]"

// ------------------------------------------------------------------ Census

export function CensusView({ data, filters: f, update }: ViewProps) {
  const geo = effectiveGeo("census", f)
  const locs = f.locs.filter((l) => data.meta.locations[geo].includes(l))
  const values = React.useMemo(
    () => censusByLocation(data, geo, f.variable, f.measure, f.type),
    [data, geo, f.variable, f.measure, f.type]
  )
  const dark = useIsDark()
  const { colors, min, max } = React.useMemo(
    () => scaleColors(values, dark),
    [values, dark]
  )
  const measures = data.meta.censusVars[f.variable]
  const series = locs.length
    ? locs.map((l) => ({
        name: l,
        values: censusVariable(data, geo, f.variable, l, f.type),
      }))
    : [
        {
          name: "Solomon Islands",
          values: censusVariableTotal(data, geo, f.variable, f.type),
        },
      ]

  const title =
    f.type === "Proportion"
      ? `Proportion of ${f.measure.toLowerCase()} by ${geo.toLowerCase()}`
      : `${/^total/i.test(f.measure) ? f.measure : `Total ${f.measure.toLowerCase()}`} by ${geo.toLowerCase()}`
  return (
    <>
      <PageTitle description={`2009 Census · ${f.variable}`}>{title}</PageTitle>
      <MapCard
        legend={
          <SequentialLegend
            min={min}
            max={max}
            format={(v) => fmt(v, f.type)}
            title={f.measure}
          />
        }
      >
        <ChoroplethMap
          className={mapClass}
          geojson={data.geo[geo]}
          colors={colors}
          selected={locs}
          tooltip={(name) =>
            tip(name, [[f.measure, fmt(values.get(name), f.type)]])
          }
          onFeatureClick={(name) => update({ locs: toggle(locs, name) })}
        />
      </MapCard>
      <Card>
        <CardHeader>
          <CardTitle>{f.variable}</CardTitle>
          <CardDescription>
            Showing {f.type === "Proportion" ? "proportions" : "totals"} for{" "}
            {locs.length ? locs.join(", ") : "Solomon Islands"}. Click a bar to
            show that measure on the map.
            {locs.length > 8 &&
              " Only the first 8 selected locations are charted."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CensusBarChart
            measures={measures}
            series={series}
            type={f.type}
            highlight={f.measure}
            onMeasureClick={(measure) => update({ measure })}
          />
        </CardContent>
      </Card>
    </>
  )
}

// ------------------------------------------------------------------ Population projections

export function PopulationView({ data, filters: f, update }: ViewProps) {
  const { meta } = data
  const locs = f.locs.filter((l) => meta.locations.Province.includes(l))
  const byYear = React.useMemo(
    () => popByLocationYear(data, f.popMeasure, f.type, f.ages),
    [data, f.popMeasure, f.type, f.ages]
  )
  // Colour range is fixed across all years so the slider shows change over time
  const domain = React.useMemo<[number, number]>(() => {
    const all = [...byYear.values()].flatMap((m) => [...m.values()])
    return [Math.min(...all), Math.max(...all)]
  }, [byYear])
  const values = React.useMemo(
    () => new Map<string, number | null>(byYear.get(f.year) ?? []),
    [byYear, f.year]
  )
  const dark = useIsDark()
  const { colors } = React.useMemo(
    () => scaleColors(values, dark, domain),
    [values, dark, domain]
  )
  const kpi = popTotal(data, f.year, f.popMeasure, f.type, f.ages, locs)
  const pyramid = popPyramid(data, f.year, f.type, locs)
  const allAges = f.ages.length === meta.ages.length
  const measureLabel = f.popMeasure === "Total" ? "Population" : f.popMeasure

  return (
    <>
      <PageTitle
        description={`Projections from the 2009 census by province${allAges ? "" : ` · ages ${f.ages.join(", ")}`}`}
      >
        {locs.length
          ? `Projected population for ${locs.join(", ")} in ${f.year}`
          : `Projected population for Solomon Islands in ${f.year}`}
      </PageTitle>
      <MapCard
        legend={
          <SequentialLegend
            min={domain[0]}
            max={domain[1]}
            format={(v) => fmt(v, f.type)}
            title={`${measureLabel}, all years`}
          />
        }
      >
        <ChoroplethMap
          className={mapClass}
          geojson={data.geo.Province}
          colors={colors}
          selected={locs}
          tooltip={(name) =>
            tip(name, [
              [`${measureLabel} ${f.year}`, fmt(values.get(name), f.type)],
            ])
          }
          onFeatureClick={(name) => update({ locs: toggle(locs, name) })}
        />
      </MapCard>
      <Card size="sm">
        <CardContent className="flex items-center gap-4">
          <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
            Year
          </span>
          <span className="font-mono text-sm tabular-nums">
            {meta.popYears[0]}
          </span>
          <Slider
            className="flex-1"
            min={meta.popYears[0]}
            max={meta.popYears.at(-1)}
            step={1}
            value={[f.year]}
            onValueChange={(v) =>
              update({ year: Array.isArray(v) ? v[0] : (v as number) })
            }
            aria-label="Projection year"
          />
          <span className="font-mono text-sm tabular-nums">
            {meta.popYears.at(-1)}
          </span>
          <span className="w-14 border px-2 py-1 text-center font-mono text-sm font-semibold tabular-nums">
            {f.year}
          </span>
        </CardContent>
      </Card>
      <div className="grid items-start gap-4 lg:grid-cols-[minmax(0,16rem)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardDescription>
              {f.type === "Proportion"
                ? "Share of projected population"
                : `Projected ${measureLabel.toLowerCase()}`}{" "}
              in {f.year}
            </CardDescription>
            <CardTitle className="font-mono text-4xl font-semibold tabular-nums">
              {fmt(kpi, f.type)}
            </CardTitle>
            <CardDescription>
              {locs.length ? locs.join(", ") : "Solomon Islands"}
              {allAges ? ", all ages" : `, ages ${f.ages.join(", ")}`}
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>
              {locs.length
                ? "Aggregated projected population pyramid"
                : "Projected population pyramid"}
              , {f.year}
            </CardTitle>
            <CardDescription>
              {locs.length ? locs.join(", ") : "Solomon Islands"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <PopulationPyramid rows={pyramid} type={f.type} />
          </CardContent>
        </Card>
      </div>
    </>
  )
}

// ------------------------------------------------------------------ Elections

export function ElectionView({ data, filters: f, update }: ViewProps) {
  const winners = React.useMemo(
    () => electionWinners(data, f.election, f.elecYear),
    [data, f.election, f.elecYear]
  )
  const colors = React.useMemo(
    () =>
      new Map(
        [...winners].map(([loc, w]) => [
          loc,
          data.meta.partyColors[w.party] ?? "#9ca3af",
        ])
      ),
    [winners, data]
  )
  const parties = [...new Set([...winners.values()].map((w) => w.party))]
    .map((p) => ({
      party: p,
      seats: [...winners.values()].filter((w) => w.party === p).length,
    }))
    .sort((a, b) => b.seats - a.seats)
  const results = electionResults(data, f.election, f.elecYear, f.elecLoc)

  return (
    <>
      <PageTitle description="Winning party by constituency. Click a constituency to see its results.">
        {f.elecYear} {f.election} election
      </PageTitle>
      <MapCard
        legend={
          <div className="flex flex-col gap-1">
            <span className="font-medium">Winning party (seats)</span>
            <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
              {parties.map((p) => (
                <span key={p.party} className="flex items-center gap-1.5">
                  <span
                    className="size-2.5 shrink-0 rounded-[2px] ring-1 ring-foreground/20"
                    style={{ background: data.meta.partyColors[p.party] }}
                  />
                  {p.party}{" "}
                  <span className="font-mono text-muted-foreground tabular-nums">
                    {p.seats}
                  </span>
                </span>
              ))}
            </div>
          </div>
        }
      >
        <ChoroplethMap
          className={mapClass}
          geojson={data.geo.Constituency}
          colors={colors}
          selected={[f.elecLoc]}
          dimUnselected={false}
          tooltip={(name) => {
            const w = winners.get(name)
            return w
              ? tip(name, [
                  ["Winning party", w.party],
                  ["Candidate", w.candidate.replace(/\s*\(.*\)$/, "")],
                ])
              : tip(name, [])
          }}
          onFeatureClick={(elecLoc) => update({ elecLoc })}
        />
      </MapCard>
      <Card>
        <CardHeader>
          <CardTitle>
            {f.elecYear} {f.election} election results in {f.elecLoc}
          </CardTitle>
          <CardDescription>
            {f.type === "Total"
              ? "Votes per candidate"
              : "Share of the vote per candidate"}
            , coloured by party.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ElectionBarChart
            rows={results}
            type={f.type}
            partyColors={data.meta.partyColors}
          />
        </CardContent>
      </Card>
    </>
  )
}
