import * as React from "react"
import * as maplibregl from "maplibre-gl"
import type { StyleSpecification } from "maplibre-gl"
import "maplibre-gl/dist/maplibre-gl.css"
// MapLibre v6 looks for its worker next to its own module, which doesn't survive bundling, so point it at the file
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url"

import type { GeoJson } from "@/lib/data"
import { useIsDark } from "@/lib/theme"

maplibregl.setWorkerUrl(workerUrl)

const BASEMAPS = {
  light: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  dark: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
}

/** A plain background used if the basemap can't be loaded (offline, blocked, ...) */
const fallbackStyle = (dark: boolean): StyleSpecification => ({
  version: 8,
  sources: {},
  layers: [
    {
      id: "background",
      type: "background",
      paint: { "background-color": dark ? "#1f2328" : "#eef2f4" },
    },
  ],
})

const styleCache = new Map<string, Promise<StyleSpecification>>()
function loadStyle(dark: boolean) {
  const url = dark ? BASEMAPS.dark : BASEMAPS.light
  if (!styleCache.has(url)) {
    styleCache.set(
      url,
      fetch(url)
        .then((r) =>
          r.ok
            ? (r.json() as Promise<StyleSpecification>)
            : Promise.reject(r.status)
        )
        .catch(() => fallbackStyle(dark))
    )
  }
  return styleCache.get(url)!
}

export interface ChoroplethMapProps {
  geojson: GeoJson
  /** Fill colour for each feature name, missing names are drawn grey */
  colors: Map<string, string>
  selected: string[]
  /** HTML shown in the hover popup for a feature */
  tooltip: (name: string) => string
  onFeatureClick?: (name: string) => void
  /** Fade areas that aren't selected (multi-select pages) */
  dimUnselected?: boolean
  className?: string
}

const SOURCE = "areas"

export function ChoroplethMap({
  geojson,
  colors,
  selected,
  tooltip,
  onFeatureClick,
  dimUnselected = true,
  className,
}: ChoroplethMapProps) {
  const container = React.useRef<HTMLDivElement>(null)
  const mapRef = React.useRef<maplibregl.Map | null>(null)
  const [styleReady, setStyleReady] = React.useState(0)
  const dark = useIsDark()

  // keep the latest props available to map event handlers without re-binding
  const props = React.useRef({
    geojson,
    colors,
    selected,
    tooltip,
    onFeatureClick,
  })
  React.useEffect(() => {
    props.current = { geojson, colors, selected, tooltip, onFeatureClick }
  })

  // Create the map once
  React.useEffect(() => {
    if (!container.current) return
    const map = new maplibregl.Map({
      container: container.current,
      style: fallbackStyle(dark),
      center: [162.012453, -9.565766],
      zoom: 5,
      attributionControl: { compact: true },
      dragRotate: false,
      pitchWithRotate: false,
    })
    map.touchZoomRotate.disableRotation()
    map.addControl(
      new maplibregl.NavigationControl({ showCompass: false }),
      "top-right"
    )
    mapRef.current = map

    const popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      className: "map-popup",
      offset: 8,
    })
    let hovered: string | number | undefined

    map.on("mousemove", "areas-fill", (e) => {
      const f = e.features?.[0]
      if (!f) return
      map.getCanvas().style.cursor = "pointer"
      if (hovered !== undefined)
        map.setFeatureState({ source: SOURCE, id: hovered }, { hover: false })
      hovered = f.id
      if (hovered !== undefined)
        map.setFeatureState({ source: SOURCE, id: hovered }, { hover: true })
      popup
        .setLngLat(e.lngLat)
        .setHTML(props.current.tooltip(String(f.properties.name)))
        .addTo(map)
    })
    map.on("mouseleave", "areas-fill", () => {
      map.getCanvas().style.cursor = ""
      if (hovered !== undefined)
        map.setFeatureState({ source: SOURCE, id: hovered }, { hover: false })
      hovered = undefined
      popup.remove()
    })
    map.on("click", "areas-fill", (e) => {
      const f = e.features?.[0]
      if (f) props.current.onFeatureClick?.(String(f.properties.name))
    })
    map.on("style.load", () => setStyleReady((n) => n + 1))

    const ro = new ResizeObserver(() => map.resize())
    ro.observe(container.current)
    return () => {
      ro.disconnect()
      popup.remove()
      map.remove()
      mapRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Swap the basemap with the site theme
  React.useEffect(() => {
    let cancelled = false
    loadStyle(dark).then((style) => {
      if (!cancelled) mapRef.current?.setStyle(style)
    })
    return () => {
      cancelled = true
    }
  }, [dark])

  // (Re)add our layers whenever a style loads, below the basemap's labels
  React.useEffect(() => {
    const map = mapRef.current
    if (!map || !styleReady) return
    if (!map.getSource(SOURCE)) {
      map.addSource(SOURCE, {
        type: "geojson",
        data: props.current.geojson,
        promoteId: "name",
      })
      const firstLabel = map
        .getStyle()
        .layers.find((l) => l.type === "symbol")?.id
      map.addLayer(
        {
          id: "areas-fill",
          type: "fill",
          source: SOURCE,
          paint: {
            "fill-color": [
              "to-color",
              ["coalesce", ["feature-state", "color"], "#c8cdd2"],
            ],
            "fill-opacity": [
              "case",
              ["boolean", ["feature-state", "hover"], false],
              0.95,
              ["boolean", ["feature-state", "dimmed"], false],
              0.3,
              0.8,
            ],
          },
        },
        firstLabel
      )
      map.addLayer(
        {
          id: "areas-line",
          type: "line",
          source: SOURCE,
          paint: {
            "line-color": dark ? "#e5e7eb" : "#334155",
            "line-opacity": [
              "case",
              ["boolean", ["feature-state", "selected"], false],
              1,
              0.35,
            ],
            "line-width": [
              "case",
              ["boolean", ["feature-state", "selected"], false],
              2.5,
              ["boolean", ["feature-state", "hover"], false],
              1.5,
              0.5,
            ],
          },
        },
        firstLabel
      )
    }
    fit(map, props.current.geojson)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [styleReady])

  // New geography: replace the data and zoom to it
  React.useEffect(() => {
    const map = mapRef.current
    const src = map?.getSource(SOURCE) as maplibregl.GeoJSONSource | undefined
    if (!map || !src) return
    src.setData(geojson)
  }, [geojson, styleReady])

  // Colours and selection are feature-state so they update without re-uploading the geometry
  React.useEffect(() => {
    const map = mapRef.current
    if (!map || !map.getSource(SOURCE)) return
    const sel = new Set(selected)
    for (const f of geojson.features) {
      const name = f.properties.name
      map.setFeatureState(
        { source: SOURCE, id: name },
        {
          color: colors.get(name) ?? null,
          selected: sel.has(name),
          dimmed: dimUnselected && sel.size > 0 && !sel.has(name),
        }
      )
    }
  }, [geojson, colors, selected, dimUnselected, styleReady])

  return <div ref={container} className={className} />
}

function fit(map: maplibregl.Map, geojson: GeoJson) {
  const b = new maplibregl.LngLatBounds()
  for (const f of geojson.features) {
    const walk = (c: unknown): void => {
      if (typeof (c as number[])[0] === "number")
        b.extend(c as [number, number])
      else (c as unknown[]).forEach(walk)
    }
    if ("coordinates" in f.geometry) walk(f.geometry.coordinates)
  }
  if (!b.isEmpty()) map.fitBounds(b, { padding: 24, animate: false })
}
