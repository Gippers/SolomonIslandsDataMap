// @ts-check

import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "astro/config"
import react from "@astrojs/react"

import icon from "astro-icon"

// Served as a GitHub Pages project site, which sits under the custom domain of the
// user site (Gippers/gippers.github.io): https://thomasmartin.id.au/SolomonIslandsDataMap/
export default defineConfig({
  site: "https://thomasmartin.id.au",
  base: "/SolomonIslandsDataMap",
  trailingSlash: "ignore",
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [react(), icon()],
})
