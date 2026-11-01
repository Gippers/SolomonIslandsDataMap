import * as React from "react"

/** Tracks the `dark` class the ModeToggle puts on <html> */
export function useIsDark() {
  const [dark, setDark] = React.useState(
    () =>
      typeof document !== "undefined" &&
      document.documentElement.classList.contains("dark")
  )
  React.useEffect(() => {
    const el = document.documentElement
    const obs = new MutationObserver(() =>
      setDark(el.classList.contains("dark"))
    )
    obs.observe(el, { attributes: true, attributeFilter: ["class"] })
    return () => obs.disconnect()
  }, [])
  return dark
}

/** Plotly's "deep" colour scale (cmocean), as used by the original Dash map */
export const DEEP = [
  [253, 253, 204],
  [206, 236, 179],
  [156, 219, 165],
  [111, 201, 163],
  [86, 177, 163],
  [76, 153, 160],
  [68, 130, 155],
  [62, 108, 150],
  [62, 82, 143],
  [64, 60, 115],
  [54, 43, 77],
  [39, 26, 44],
]

/** Colour for t in [0, 1] on the deep scale */
export function deepColor(t: number) {
  const x =
    Math.min(1, Math.max(0, Number.isFinite(t) ? t : 0)) * (DEEP.length - 1)
  const i = Math.min(DEEP.length - 2, Math.floor(x))
  const f = x - i
  const c = DEEP[i].map((v, k) => Math.round(v + (DEEP[i + 1][k] - v) * f))
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`
}

/** Legend gradient. On a dark surface the ramp is reversed so that high values stay visible (light on dark) */
export const deepGradient = (dark: boolean) =>
  `linear-gradient(to right, ${(dark ? [...DEEP].reverse() : DEEP).map((c) => `rgb(${c.join(",")})`).join(", ")})`

/** Colours for a set of values on the deep scale, with the min/max used */
export function scaleColors(
  values: Map<string, number | null>,
  dark: boolean,
  domain?: [number, number]
) {
  const nums = [...values.values()].filter((v): v is number => v != null)
  const [min, max] = domain ?? [Math.min(...nums), Math.max(...nums)]
  const colors = new Map<string, string>()
  for (const [k, v] of values)
    if (v != null) {
      const t = max > min ? (v - min) / (max - min) : 0.5
      colors.set(k, deepColor(dark ? 1 - t : t))
    }
  return { colors, min, max }
}
