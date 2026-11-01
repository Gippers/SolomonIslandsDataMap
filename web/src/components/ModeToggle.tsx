import { Moon, Sun } from "lucide-react"

import { Button } from "@/components/ui/button"

/** One click flips light/dark. The inline script in the layout applies and remembers the choice. */
export function ModeToggle() {
  return (
    <Button
      variant="outline"
      size="icon-lg"
      aria-label="Toggle dark mode"
      onClick={() => document.documentElement.classList.toggle("dark")}
    >
      <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
    </Button>
  )
}
