// Thin wrappers around the shadcn components used by the filter sidebar
import * as React from "react"
import { InfoIcon } from "lucide-react"

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Combobox,
  ComboboxChip,
  ComboboxChips,
  ComboboxChipsInput,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
  ComboboxValue,
  useComboboxAnchor,
} from "@/components/ui/combobox"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Label } from "@/components/ui/label"

export function Field({
  label,
  info,
  children,
}: {
  label: string
  info?: string
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-1">
        <Label className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
          {label}
        </Label>
        {info && (
          <Tooltip>
            <TooltipTrigger
              className="text-muted-foreground hover:text-foreground"
              aria-label={`About ${label}`}
            >
              <InfoIcon className="size-3.5" />
            </TooltipTrigger>
            <TooltipContent className="max-w-64">{info}</TooltipContent>
          </Tooltip>
        )}
      </div>
      {children}
    </div>
  )
}

/** A single choice toggle group (replaces the Mantine SegmentedControl) */
export function Segmented<T extends string>({
  value,
  options,
  onChange,
  disabled,
  label,
}: {
  value: T
  options: readonly T[]
  onChange: (v: T) => void
  disabled?: boolean
  label: string
}) {
  return (
    <ToggleGroup
      variant="outline"
      size="sm"
      spacing={0}
      className="w-full"
      aria-label={label}
      value={[value]}
      disabled={disabled}
      onValueChange={(v: string[]) => {
        const next = v.find((x) => x !== value)
        if (next) onChange(next as T)
      }}
    >
      {options.map((o) => (
        <ToggleGroupItem
          key={o}
          value={o}
          className="flex-1 aria-pressed:border-primary aria-pressed:bg-primary aria-pressed:text-primary-foreground aria-pressed:hover:bg-primary/90"
        >
          {o}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  )
}

export function SimpleSelect({
  value,
  options,
  onChange,
  label,
}: {
  value: string
  options: readonly (string | number)[]
  onChange: (v: string) => void
  label: string
}) {
  const items = options.map((o) => ({ label: String(o), value: String(o) }))
  return (
    <Select
      items={items}
      value={String(value)}
      onValueChange={(v) => v != null && onChange(String(v))}
    >
      <SelectTrigger className="w-full" aria-label={label}>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {items.map((i) => (
          <SelectItem key={i.value} value={i.value}>
            {i.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

/** Searchable single select, for long lists */
export function SearchSelect({
  value,
  options,
  onChange,
  label,
}: {
  value: string
  options: readonly string[]
  onChange: (v: string) => void
  label: string
}) {
  return (
    <Combobox
      items={options as string[]}
      value={value}
      onValueChange={(v) => v != null && onChange(String(v))}
      autoHighlight
    >
      <ComboboxInput
        className="w-full"
        placeholder={`Search ${label.toLowerCase()}…`}
        aria-label={label}
        onFocus={(e: React.FocusEvent<HTMLInputElement>) =>
          e.currentTarget.select()
        }
      />
      <ComboboxContent>
        <ComboboxEmpty>Nothing found.</ComboboxEmpty>
        <ComboboxList>
          {(item: string) => (
            <ComboboxItem key={item} value={item}>
              {item}
            </ComboboxItem>
          )}
        </ComboboxList>
      </ComboboxContent>
    </Combobox>
  )
}

/** Searchable multi select shown as chips */
export function MultiSelect({
  value,
  options,
  onChange,
  placeholder,
  label,
}: {
  value: string[]
  options: readonly string[]
  onChange: (v: string[]) => void
  placeholder: string
  label: string
}) {
  const anchor = useComboboxAnchor()
  return (
    <Combobox
      multiple
      autoHighlight
      items={options as string[]}
      value={value}
      onValueChange={(v) => onChange(v as string[])}
    >
      <ComboboxChips ref={anchor} className="w-full">
        <ComboboxValue>
          {(values: string[]) => (
            <React.Fragment>
              {values.map((v) => (
                <ComboboxChip key={v}>{v}</ComboboxChip>
              ))}
              <ComboboxChipsInput
                placeholder={values.length ? "" : placeholder}
                aria-label={label}
              />
            </React.Fragment>
          )}
        </ComboboxValue>
      </ComboboxChips>
      <ComboboxContent anchor={anchor}>
        <ComboboxEmpty>Nothing found.</ComboboxEmpty>
        <ComboboxList>
          {(item: string) => (
            <ComboboxItem key={item} value={item}>
              {item}
            </ComboboxItem>
          )}
        </ComboboxList>
      </ComboboxContent>
    </Combobox>
  )
}
