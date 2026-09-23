import { Search } from "lucide-react";

export type SortKey = "price" | "price_per_100g" | "relevance";

export interface FilterState {
  q: string;
  brand: string;
  flavour: string;
  weight: string;
  store: string;
  sort: SortKey;
}

export const emptyFilters: FilterState = {
  q: "",
  brand: "all",
  flavour: "all",
  weight: "all",
  store: "all",
  sort: "relevance",
};

interface Props {
  value: FilterState;
  onChange: (next: FilterState) => void;
  brands: string[];
  flavours: string[];
  weights: string[];
  stores: string[];
  resultCount?: number | undefined;
}

const selectClass =
  "h-11 w-full appearance-none rounded-xl border border-border bg-background px-3.5 text-sm text-foreground outline-none transition-colors hover:border-foreground/30 focus:border-foreground/50";

export function Filters({
  value,
  onChange,
  brands,
  flavours,
  weights,
  stores,
  resultCount,
}: Props) {
  const set = <K extends keyof FilterState>(key: K, v: FilterState[K]) =>
    onChange({ ...value, [key]: v });

  return (
    <div className="rounded-3xl border border-border bg-card p-4 sm:p-5">
      <div className="relative">
        <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          value={value.q}
          onChange={(e) => set("q", e.target.value)}
          placeholder="Search for a protein, brand, or flavour..."
          className="h-12 w-full rounded-2xl border border-border bg-background pl-11 pr-4 text-sm text-foreground placeholder:text-muted-foreground outline-none transition-colors focus:border-foreground/50"
        />
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Select
          label="Brand"
          value={value.brand}
          options={brands}
          onChange={(v) => set("brand", v)}
        />
        <Select
          label="Flavour"
          value={value.flavour}
          options={flavours}
          onChange={(v) => set("flavour", v)}
        />
        <Select
          label="Weight"
          value={value.weight}
          options={weights}
          onChange={(v) => set("weight", v)}
        />
        <Select
          label="Retailer"
          value={value.store}
          options={stores}
          onChange={(v) => set("store", v)}
        />
        <div>
          <label className="mb-1.5 block text-xs font-medium text-muted-foreground">Sort by</label>
          <select
            value={value.sort}
            onChange={(e) => set("sort", e.target.value as SortKey)}
            className={selectClass}
          >
            <option value="relevance">Recommended</option>
            <option value="price">MRP: low to high</option>
            <option value="price_per_100g">Price per 100g</option>
          </select>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
        <span>{resultCount === undefined ? "Loading products…" : `${resultCount} products`}</span>
        <button
          type="button"
          onClick={() => onChange(emptyFilters)}
          className="rounded-full px-2 py-1 transition-colors hover:text-foreground"
        >
          Reset filters
        </button>
      </div>
    </div>
  );
}

function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-medium text-muted-foreground">{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)} className={selectClass}>
        <option value="all">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}
