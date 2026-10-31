import * as React from "react"
import { SlidersHorizontal } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { TooltipProvider } from "@/components/ui/tooltip"
import { asset, loadData, type AppData } from "@/lib/data"
import { toSearch, useFilters, type Page } from "@/lib/filters"
import { cn } from "@/lib/utils"
import { FilterPanel } from "./FilterPanel"
import { TableView } from "./TableView"
import { CensusView, ElectionView, PopulationView } from "./views"

export const PAGES: { page: Page; label: string; path: string }[] = [
  { page: "census", label: "2009 Census", path: "" },
  { page: "election", label: "Election map", path: "election/" },
  { page: "population", label: "Population projections", path: "population/" },
  { page: "table", label: "Data table", path: "table/" },
]

export default function Dashboard({ page }: { page: Page }) {
  const [data, setData] = React.useState<AppData>()
  const [error, setError] = React.useState<string>()
  const [filters, update] = useFilters(data?.meta)
  const [sheetOpen, setSheetOpen] = React.useState(false)

  React.useEffect(() => {
    loadData().then(setData, (e: Error) => setError(e.message))
  }, [])

  const search = data && filters ? toSearch(filters, data.meta) : ""
  const ready = data && filters

  const panel = ready && (
    <FilterPanel page={page} data={data} filters={filters} update={update} />
  )

  return (
    <TooltipProvider delay={200}>
      <div className="flex min-h-0 flex-1">
        {/* Filters: fixed sidebar on large screens, a sheet on small ones */}
        <aside className="hidden w-72 shrink-0 border-r lg:block">
          <div className="sticky top-0 max-h-[calc(100vh)] overflow-y-auto p-4">
            <h2 className="mb-4 text-sm font-semibold">Filters</h2>
            {panel || <PanelSkeleton />}
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="flex items-center border-b">
            <nav
              className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto px-4"
              aria-label="Dashboard pages"
            >
              {PAGES.map((p) => (
                <a
                  key={p.page}
                  href={asset(p.path) + search}
                  aria-current={p.page === page ? "page" : undefined}
                  className={cn(
                    "-mb-px border-b-2 px-3 py-2.5 text-sm whitespace-nowrap transition-colors",
                    p.page === page
                      ? "border-primary text-foreground"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  )}
                >
                  {p.label}
                </a>
              ))}
            </nav>
            <div className="shrink-0 pr-4 pl-2 lg:hidden">
              <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
                <SheetTrigger render={<Button variant="outline" size="sm" />}>
                  <SlidersHorizontal data-icon="inline-start" />
                  Filters
                </SheetTrigger>
                <SheetContent side="left" className="w-80 overflow-y-auto">
                  <SheetHeader>
                    <SheetTitle>Filters</SheetTitle>
                    <SheetDescription className="sr-only">
                      Choose what the dashboard shows
                    </SheetDescription>
                  </SheetHeader>
                  <div className="px-4 pb-6">{panel}</div>
                </SheetContent>
              </Sheet>
            </div>
          </div>

          <main className="flex flex-col gap-4 p-4 lg:p-6">
            {error ? (
              <p className="text-sm text-destructive">
                Could not load the data: {error}
              </p>
            ) : !ready ? (
              <ContentSkeleton />
            ) : page === "census" ? (
              <CensusView data={data} filters={filters} update={update} />
            ) : page === "population" ? (
              <PopulationView data={data} filters={filters} update={update} />
            ) : page === "election" ? (
              <ElectionView data={data} filters={filters} update={update} />
            ) : (
              <TableView data={data} filters={filters} />
            )}
          </main>
        </div>
      </div>
    </TooltipProvider>
  )
}

function PanelSkeleton() {
  return (
    <div className="flex flex-col gap-5">
      {Array.from({ length: 5 }, (_, i) => (
        <div key={i} className="flex flex-col gap-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-8 w-full" />
        </div>
      ))}
    </div>
  )
}

function ContentSkeleton() {
  return (
    <>
      <Skeleton className="h-7 w-80 max-w-full" />
      <Skeleton className="h-[46vh] min-h-[320px] w-full lg:h-[52vh]" />
      <Skeleton className="h-64 w-full" />
    </>
  )
}
