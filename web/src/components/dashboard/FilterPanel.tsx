import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { AppData, DataType, Geo } from "@/lib/data"
import {
  effectiveGeo,
  type Dataset,
  type Filters,
  type Page,
} from "@/lib/filters"
import {
  Field,
  MultiSelect,
  Segmented,
  SearchSelect,
  SimpleSelect,
} from "./controls"

const GEO_INFO =
  "Provinces are the largest areas, constituencies are electoral areas for the national parliament and wards are the smallest areas."

/** The sidebar of filters, which filters show depends on the page (as in the Dash app) */
export function FilterPanel({
  page,
  data,
  filters: f,
  update,
}: {
  page: Page
  data: AppData
  filters: Filters
  update: (patch: Partial<Filters>) => void
}) {
  const { meta } = data
  const geo = effectiveGeo(page, f)
  const geoLocked =
    geo !== f.geo || page === "population" || page === "election"
  const showCensusVars =
    page === "census" || (page === "table" && f.dataset === "Census")
  const showPopVars =
    page === "population" ||
    (page === "table" && f.dataset === "Population Projections")
  const locations = meta.locations[geo]

  return (
    <div className="flex flex-col gap-5">
      {page === "table" && (
        <Field label="Dataset">
          <Segmented<Dataset>
            label="Dataset"
            value={f.dataset}
            options={["Census", "Population Projections"]}
            onChange={(dataset) => update({ dataset })}
          />
        </Field>
      )}

      <Field
        label="Geography"
        info={
          geoLocked
            ? `${GEO_INFO} This data is only available by ${geo.toLowerCase()}.`
            : GEO_INFO
        }
      >
        <Segmented<Geo>
          label="Geography"
          value={geo}
          options={meta.geoLevels}
          disabled={geoLocked}
          onChange={(g) => update({ geo: g, locs: [] })}
        />
      </Field>

      {page === "population" && (
        <Field label="Age group">
          <MultiSelect
            label="Age group"
            value={f.ages.length === meta.ages.length ? [] : f.ages}
            options={meta.ages}
            placeholder="All ages"
            onChange={(ages) =>
              update({
                ages: ages.length
                  ? meta.ages.filter((a) => ages.includes(a))
                  : meta.ages,
              })
            }
          />
        </Field>
      )}

      {page === "election" ? (
        <>
          <Field label="Election type">
            <SimpleSelect
              label="Election type"
              value={f.election}
              options={meta.elections}
              onChange={(election) =>
                update({ election, elecYear: meta.elecYears[election].at(-1)! })
              }
            />
          </Field>
          <Field label="Election year">
            <SimpleSelect
              label="Election year"
              value={String(f.elecYear)}
              options={meta.elecYears[f.election]}
              onChange={(y) => update({ elecYear: Number(y) })}
            />
          </Field>
          <Field
            label="Constituency"
            info="Click a constituency on the map to select it."
          >
            <SearchSelect
              label="Constituency"
              value={f.elecLoc}
              options={meta.locations.Constituency}
              onChange={(elecLoc) => update({ elecLoc })}
            />
          </Field>
        </>
      ) : (
        page !== "table" && (
          <Field
            label="Location"
            info="Click areas on the map to add or remove them from the selection."
          >
            <MultiSelect
              label="Location"
              value={f.locs.filter((l) => locations.includes(l))}
              options={locations}
              placeholder="All of Solomon Islands"
              onChange={(locs) => update({ locs })}
            />
          </Field>
        )
      )}

      {showCensusVars && (
        <Field label="Data">
          <SearchSelect
            label="Census topic"
            value={f.variable}
            options={Object.keys(meta.censusVars)}
            onChange={(variable) =>
              update({ variable, measure: meta.censusVars[variable][0] })
            }
          />
          {page !== "table" && (
            <SimpleSelect
              label="Measure"
              value={f.measure}
              options={meta.censusVars[f.variable]}
              onChange={(measure) => update({ measure })}
            />
          )}
        </Field>
      )}

      {showPopVars && (
        <Field label="Data">
          {Object.keys(meta.populationVars).length > 1 && (
            <SimpleSelect
              label="Population variable"
              value={f.popVariable}
              options={Object.keys(meta.populationVars)}
              onChange={(popVariable) =>
                update({
                  popVariable,
                  popMeasure: meta.populationVars[popVariable][0],
                })
              }
            />
          )}
          <SimpleSelect
            label="Measure"
            value={f.popMeasure}
            options={meta.populationVars[f.popVariable]}
            onChange={(popMeasure) => update({ popMeasure })}
          />
        </Field>
      )}

      <Field
        label="Data type"
        info="Total shows counts. Proportion shows each value as a share of the total for its area (census) or of the whole country in that year (population projections)."
      >
        <Segmented<DataType>
          label="Data type"
          value={f.type}
          options={meta.dataTypes}
          onChange={(type) => update({ type })}
        />
      </Field>

      {page === "table" && (
        <Field label="Rows per page">
          <Input
            type="number"
            min={1}
            value={f.rows}
            onChange={(e) =>
              update({ rows: Math.max(1, Number(e.target.value) || 1) })
            }
          />
        </Field>
      )}

      {(f.locs.length > 0 || f.type !== "Total") &&
        page !== "election" &&
        page !== "table" && (
          <Button
            variant="ghost"
            size="sm"
            className="self-start"
            onClick={() => update({ locs: [], type: "Total" })}
          >
            Reset selection
          </Button>
        )}
    </div>
  )
}
