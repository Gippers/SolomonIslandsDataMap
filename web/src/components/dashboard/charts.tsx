import * as React from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ReferenceLine,
  XAxis,
  YAxis,
} from "recharts"

import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import {
  fmt,
  fmtInt,
  fmtPct,
  type DataType,
  type ElectionRow,
} from "@/lib/data"

/** Categorical slots, assigned in order and never cycled past 8 */
export const SERIES = Array.from(
  { length: 8 },
  (_, i) => `var(--series-${i + 1})`
)

const axisTick = { fill: "var(--muted-foreground)", fontSize: 11 }

/** True on phone-width screens, where long category labels get a narrower axis */
function useNarrow() {
  const query = "(max-width: 640px)"
  const [narrow, setNarrow] = React.useState(
    () => typeof window !== "undefined" && window.matchMedia(query).matches
  )
  React.useEffect(() => {
    const m = window.matchMedia(query)
    const on = () => setNarrow(m.matches)
    m.addEventListener("change", on)
    return () => m.removeEventListener("change", on)
  }, [])
  return narrow
}

/** Symmetric "nice" ticks for the pyramid, e.g. -20k, -10k, 0, 10k, 20k */
function niceTicks(max: number) {
  const step0 = max / 2
  const mag = 10 ** Math.floor(Math.log10(step0))
  const step =
    [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= step0) ?? step0
  return [-2 * step, -step, 0, step, 2 * step]
}

function TooltipRow({
  color,
  label,
  value,
}: {
  color?: string
  label: React.ReactNode
  value: string
}) {
  return (
    <div className="flex w-full items-center justify-between gap-4">
      <span className="flex items-center gap-1.5 text-muted-foreground">
        {color && (
          <span
            className="size-2.5 shrink-0 rounded-[2px]"
            style={{ background: color }}
          />
        )}
        {label}
      </span>
      <span className="font-mono font-medium text-foreground tabular-nums">
        {value}
      </span>
    </div>
  )
}

const shortAxis = (type: DataType) => (v: number) =>
  type === "Proportion"
    ? `${Math.round(v * 100)}%`
    : Intl.NumberFormat("en-AU", {
        notation: "compact",
        maximumFractionDigits: 1,
      }).format(v)

// ------------------------------------------------------------------ Census

/** Horizontal bars of every measure in a census variable, one series per selected location */
export function CensusBarChart({
  measures,
  series,
  type,
  highlight,
  onMeasureClick,
}: {
  measures: string[]
  series: { name: string; values: (number | null)[] }[]
  type: DataType
  highlight: string
  onMeasureClick?: (measure: string) => void
}) {
  const shown = series.slice(0, SERIES.length)
  // a single series takes the site accent, several take the categorical slots in selection order
  const config: ChartConfig = Object.fromEntries(
    shown.map((s, i) => [
      `s${i}`,
      {
        label: s.name,
        color: shown.length === 1 ? "var(--primary)" : SERIES[i],
      },
    ])
  )
  const rows = measures
    .map((m, mi) => ({
      measure: m,
      ...Object.fromEntries(shown.map((s, i) => [`s${i}`, s.values[mi] ?? 0])),
      _sum: shown.reduce((a, s) => a + (s.values[mi] ?? 0), 0),
    }))
    .sort((a, b) => b._sum - a._sum) // same as plotly's 'total descending'
  const single = shown.length === 1
  const narrow = useNarrow()
  const labelWidth = narrow ? 112 : 180
  const height = Math.max(
    160,
    rows.length * (single ? 30 : 14 * shown.length + 14) + 40
  )

  return (
    <ChartContainer
      config={config}
      className="aspect-auto w-full"
      style={{ height }}
    >
      <BarChart
        data={rows}
        layout="vertical"
        margin={{ left: 4, right: single ? 56 : 16, top: 4, bottom: 4 }}
        barGap={2}
      >
        <CartesianGrid horizontal={false} strokeDasharray="3 3" />
        <XAxis
          type="number"
          tickFormatter={shortAxis(type)}
          tick={axisTick}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          type="category"
          dataKey="measure"
          width={labelWidth}
          tick={(p) => (
            <MeasureTick
              {...p}
              highlight={highlight}
              maxChars={narrow ? 18 : 30}
            />
          )}
          tickLine={false}
          axisLine={false}
          interval={0}
        />
        <ChartTooltip
          cursor={{ fill: "var(--muted)", opacity: 0.6 }}
          content={
            <ChartTooltipContent
              formatter={(value, name, item) => (
                <TooltipRow
                  color={item.color}
                  label={config[String(name)]?.label}
                  value={fmt(Number(value), type)}
                />
              )}
            />
          }
        />
        {shown.length > 1 && (
          <ChartLegend content={<ChartLegendContent />} verticalAlign="top" />
        )}
        {shown.map((s, i) => (
          <Bar
            key={s.name}
            dataKey={`s${i}`}
            fill={`var(--color-s${i})`}
            radius={[0, 4, 4, 0]}
            maxBarSize={single ? 20 : 12}
            className="cursor-pointer"
            onClick={(d) =>
              onMeasureClick?.((d as unknown as { measure: string }).measure)
            }
          >
            {single && (
              <LabelList
                dataKey={`s${i}`}
                position="right"
                className="fill-muted-foreground"
                fontSize={11}
                formatter={(v) => fmt(Number(v), type)}
              />
            )}
          </Bar>
        ))}
      </BarChart>
    </ChartContainer>
  )
}

function MeasureTick(props: {
  x?: number | string
  y?: number | string
  payload?: { value: string }
  highlight: string
  maxChars: number
}) {
  const { x = 0, y = 0, payload, highlight, maxChars } = props
  const label = payload?.value ?? ""
  const text =
    label.length > maxChars ? `${label.slice(0, maxChars - 1)}…` : label
  return (
    <text
      x={Number(x)}
      y={Number(y)}
      dy={4}
      textAnchor="end"
      fontSize={11}
      className={
        label === highlight
          ? "fill-foreground font-semibold"
          : "fill-muted-foreground"
      }
    >
      <title>{label}</title>
      {text}
    </text>
  )
}

// ------------------------------------------------------------------ Elections

export function ElectionBarChart({
  rows,
  type,
  partyColors,
}: {
  rows: ElectionRow[]
  type: DataType
  partyColors: Record<string, string>
}) {
  const config: ChartConfig = {
    value: { label: type === "Total" ? "Votes" : "Vote share" },
  }
  const data = rows.map((r) => ({
    name: r.candParty,
    party: r.Party,
    value: r[type],
  }))
  const narrow = useNarrow()
  return (
    <ChartContainer
      config={config}
      className="aspect-auto w-full"
      style={{ height: Math.max(160, data.length * 34 + 40) }}
    >
      <BarChart
        data={data}
        layout="vertical"
        margin={{ left: 4, right: 64, top: 4, bottom: 4 }}
      >
        <CartesianGrid horizontal={false} strokeDasharray="3 3" />
        <XAxis
          type="number"
          tickFormatter={shortAxis(type)}
          tick={axisTick}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={narrow ? 120 : 200}
          tick={axisTick}
          tickLine={false}
          axisLine={false}
          interval={0}
        />
        <ChartTooltip
          cursor={{ fill: "var(--muted)", opacity: 0.6 }}
          content={
            <ChartTooltipContent
              hideLabel
              formatter={(value, _name, item) => (
                <TooltipRow
                  color={item.payload.fill}
                  label={item.payload.name}
                  value={
                    type === "Total"
                      ? `${fmtInt(Number(value))} votes`
                      : fmtPct(Number(value))
                  }
                />
              )}
            />
          }
        />
        <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={22}>
          {data.map((d) => (
            <Cell
              key={d.name}
              fill={partyColors[d.party] ?? "var(--muted-foreground)"}
            />
          ))}
          <LabelList
            dataKey="value"
            position="right"
            className="fill-muted-foreground"
            fontSize={11}
            formatter={(v) => fmt(Number(v), type)}
          />
        </Bar>
      </BarChart>
    </ChartContainer>
  )
}

// ------------------------------------------------------------------ Population pyramid

export function PopulationPyramid({
  rows,
  type,
}: {
  rows: { age: string; male: number; female: number }[]
  type: DataType
}) {
  const config: ChartConfig = {
    male: { label: "Male", color: SERIES[0] },
    female: { label: "Female", color: SERIES[1] },
  }
  const data = rows.map((r) => ({
    age: r.age,
    male: -r.male,
    female: r.female,
  }))
  const max = Math.max(1e-9, ...rows.flatMap((r) => [r.male, r.female]))
  const ticks = niceTicks(max)
  const label = (v: number) =>
    type === "Proportion" ? fmtPct(Math.abs(v), 2) : fmtInt(Math.abs(v))
  return (
    <ChartContainer config={config} className="aspect-auto h-[420px] w-full">
      <BarChart
        data={data}
        layout="vertical"
        stackOffset="sign"
        margin={{ left: 4, right: 16, top: 4, bottom: 4 }}
        barCategoryGap={1}
      >
        <CartesianGrid horizontal={false} strokeDasharray="3 3" />
        <XAxis
          type="number"
          domain={[ticks[0], ticks[4]]}
          ticks={ticks}
          tickFormatter={(v: number) => shortAxis(type)(Math.abs(v))}
          tick={axisTick}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          type="category"
          dataKey="age"
          reversed
          width={44}
          tick={axisTick}
          tickLine={false}
          axisLine={false}
          interval={0}
        />
        <ReferenceLine x={0} stroke="var(--border)" />
        <ChartTooltip
          cursor={{ fill: "var(--muted)", opacity: 0.6 }}
          content={
            <ChartTooltipContent
              labelFormatter={(l) => `Age ${l}`}
              formatter={(value, name, item) => (
                <TooltipRow
                  color={item.color}
                  label={config[String(name)]?.label}
                  value={label(Number(value))}
                />
              )}
            />
          }
        />
        <ChartLegend
          content={<ChartLegendContent />}
          verticalAlign="top"
          itemSorter={(i) => (i.dataKey === "male" ? 0 : 1)}
        />
        <Bar
          dataKey="male"
          stackId="a"
          fill="var(--color-male)"
          radius={[4, 0, 0, 4]}
        />
        <Bar
          dataKey="female"
          stackId="a"
          fill="var(--color-female)"
          radius={[0, 4, 4, 0]}
        />
      </BarChart>
    </ChartContainer>
  )
}
