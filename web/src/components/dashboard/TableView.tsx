import * as React from "react"
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table"
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Download,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { censusVariable, fmt, popMeasureIndex, type AppData } from "@/lib/data"
import { effectiveGeo, type Filters } from "@/lib/filters"
import { PageTitle } from "./views"

type Row = Record<string, string | number | null>

function buildTable(
  data: AppData,
  f: Pick<
    Filters,
    "dataset" | "geo" | "variable" | "popVariable" | "popMeasure" | "type"
  >
) {
  const geo = effectiveGeo("table", f)
  if (f.dataset === "Census") {
    const measures = data.meta.censusVars[f.variable]
    const rows: Row[] = data.meta.locations[geo].map((loc) => {
      const values = censusVariable(data, geo, f.variable, loc, f.type)
      return {
        [geo]: loc,
        ...Object.fromEntries(measures.map((m, i) => [m, values[i]])),
      }
    })
    return {
      geo,
      keys: [geo],
      columns: measures,
      rows,
      title: `Census ${f.variable} by ${geo}`,
      file: `Solomons 2009 Census Data ${f.variable} by ${geo} - ${f.type}.csv`,
    }
  }
  // Population projections: one row per province and year, one column per age group
  const i = popMeasureIndex(data, f.popMeasure)
  const byKey = new Map<string, Row>()
  for (const r of data.population.rows) {
    if (r[3] !== f.type) continue
    const key = `${r[0]}|${r[1]}`
    const row = byKey.get(key) ?? { [geo]: r[0], Year: r[1] }
    row[r[2]] = r[i] as number
    byKey.set(key, row)
  }
  return {
    geo,
    keys: [geo, "Year"],
    columns: data.meta.ages,
    rows: [...byKey.values()],
    title: `Projections of ${f.popMeasure.toLowerCase()} population by ${geo}`,
    file: `Solomons 2009 Population Projections for ${f.popVariable} Population by ${geo} - ${f.type}.csv`,
  }
}

function downloadCsv(file: string, header: string[], rows: Row[]) {
  const cell = (v: unknown) => {
    const s = v == null ? "" : String(v)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  const csv = [header, ...rows.map((r) => header.map((h) => r[h]))]
    .map((r) => r.map(cell).join(","))
    .join("\n")
  const url = URL.createObjectURL(
    new Blob([csv], { type: "text/csv;charset=utf-8" })
  )
  const a = Object.assign(document.createElement("a"), {
    href: url,
    download: file,
  })
  a.click()
  URL.revokeObjectURL(url)
}

export function TableView({
  data,
  filters: f,
}: {
  data: AppData
  filters: Filters
}) {
  const { dataset, geo, variable, popVariable, popMeasure, type } = f
  const t = React.useMemo(
    () =>
      buildTable(data, {
        dataset,
        geo,
        variable,
        popVariable,
        popMeasure,
        type,
      }),
    [data, dataset, geo, variable, popVariable, popMeasure, type]
  )
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [search, setSearch] = React.useState("")

  const columns = React.useMemo<ColumnDef<Row>[]>(
    () => [
      ...t.keys.map((k) => ({
        accessorKey: k,
        header: k,
      })),
      ...t.columns.map((c) => ({
        accessorKey: c,
        header: c,
        cell: ({ getValue }: { getValue: () => unknown }) =>
          fmt(getValue() as number | null, f.type),
        sortUndefined: "last" as const,
      })),
    ],
    [t, f.type]
  )

  const table = useReactTable({
    data: t.rows,
    columns,
    state: { sorting, globalFilter: search },
    onSortingChange: setSorting,
    onGlobalFilterChange: setSearch,
    globalFilterFn: (row, _id, value: string) =>
      String(row.original[t.geo] ?? "")
        .toLowerCase()
        .includes(value.toLowerCase()),
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: f.rows } },
  })
  React.useEffect(() => table.setPageSize(f.rows), [f.rows, table])
  React.useEffect(() => table.setPageIndex(0), [t, table])

  const { pageIndex, pageSize } = table.getState().pagination
  const total = table.getFilteredRowModel().rows.length

  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <PageTitle
          description={
            f.dataset === "Census"
              ? "2009 Census"
              : "Population projections from the 2009 census"
          }
        >
          {t.title}
        </PageTitle>
        <Button
          variant="outline"
          onClick={() => downloadCsv(t.file, [...t.keys, ...t.columns], t.rows)}
        >
          <Download data-icon="inline-start" />
          Download CSV
        </Button>
      </div>
      <Card className="gap-3">
        <CardContent className="flex flex-col gap-3">
          <Input
            className="max-w-xs"
            placeholder={`Filter by ${t.geo.toLowerCase()}…`}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="border">
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((hg) => (
                  <TableRow key={hg.id}>
                    {hg.headers.map((h, i) => {
                      const sorted = h.column.getIsSorted()
                      const Icon =
                        sorted === "asc"
                          ? ArrowUp
                          : sorted === "desc"
                            ? ArrowDown
                            : ArrowUpDown
                      return (
                        <TableHead
                          key={h.id}
                          className={
                            i === 0
                              ? "sticky left-0 z-10 bg-background"
                              : i < t.keys.length
                                ? ""
                                : "text-right"
                          }
                        >
                          <button
                            className="inline-flex max-w-44 items-center gap-1 text-left whitespace-normal hover:text-foreground"
                            onClick={h.column.getToggleSortingHandler()}
                          >
                            {flexRender(
                              h.column.columnDef.header,
                              h.getContext()
                            )}
                            <Icon className="size-3 shrink-0 text-muted-foreground" />
                          </button>
                        </TableHead>
                      )
                    })}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell, i) => (
                      <TableCell
                        key={cell.id}
                        className={
                          i === 0
                            ? "sticky left-0 z-10 bg-background font-medium"
                            : i < t.keys.length
                              ? "font-mono tabular-nums"
                              : "text-right font-mono tabular-nums"
                        }
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
                {!total && (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length}
                      className="h-20 text-center text-muted-foreground"
                    >
                      No rows match.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
          <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
            <span>
              {total
                ? `${pageIndex * pageSize + 1}–${Math.min(total, (pageIndex + 1) * pageSize)} of ${total}`
                : "0 rows"}
            </span>
            <div className="flex gap-1">
              <Button
                variant="outline"
                size="icon-sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                aria-label="Previous page"
              >
                <ChevronLeft />
              </Button>
              <Button
                variant="outline"
                size="icon-sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                aria-label="Next page"
              >
                <ChevronRight />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  )
}
