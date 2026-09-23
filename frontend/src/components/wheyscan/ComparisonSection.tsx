import { useQuery } from "@tanstack/react-query";
import { AlertCircle, PackageSearch } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  bestListing,
  bestPricePer100g,
  brandOf,
  searchProducts,
  storeLabel,
  weightLabel,
  type Product,
} from "@/lib/api";
import { Filters, emptyFilters, type FilterState } from "./Filters";
import { ProductCard, ProductCardSkeleton } from "./ProductCard";

const unique = (values: (string | null | undefined)[]) =>
  Array.from(new Set(values.filter((v): v is string => Boolean(v)))).sort((a, b) =>
    a.localeCompare(b),
  );

function useDebounced<T>(value: T, delay = 350) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function ComparisonSection({
  title = "Browse Whey Products",
  description = "Live retailer listings matched product by product, with MRP and price per 100g in one place.",
  limit,
  initialQuery = "",
}: {
  title?: string;
  description?: string;
  limit?: number | undefined;
  initialQuery?: string | undefined;
}) {
  const [filters, setFilters] = useState<FilterState>({ ...emptyFilters, q: initialQuery });
  const debouncedQuery = useDebounced(filters.q);

  const query = useQuery({
    queryKey: ["products", debouncedQuery, filters.brand, filters.flavour, filters.store],
    queryFn: () =>
      searchProducts({
        q: debouncedQuery || undefined,
        brand: filters.brand,
        flavour: filters.flavour,
        store: filters.store,
      }),
    retry: 1,
  });

  const products = useMemo(() => query.data ?? [], [query.data]);

  const options = useMemo(
    () => ({
      brands: unique(products.map((p) => brandOf(p))),
      flavours: unique(products.map((p) => p.flavour)),
      weights: unique(products.map((p) => weightLabel(p))),
      stores: unique(products.flatMap((p) => p.listings.map((l) => storeLabel(l.store_name)))),
    }),
    [products],
  );

  const visible = useMemo(() => {
    const q = filters.q.trim().toLowerCase();
    let list = products.filter((p: Product) => {
      if (q) {
        const haystack = `${p.name} ${brandOf(p)} ${p.flavour ?? ""}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      if (filters.brand !== "all" && brandOf(p) !== filters.brand) return false;
      if (filters.flavour !== "all" && p.flavour !== filters.flavour) return false;
      if (filters.weight !== "all" && weightLabel(p) !== filters.weight) return false;
      if (
        filters.store !== "all" &&
        !p.listings.some((l) => storeLabel(l.store_name) === filters.store)
      )
        return false;
      return true;
    });

    if (filters.sort === "price") {
      list = [...list].sort(
        (a, b) =>
          (bestListing(a)?.current_price ?? Infinity) - (bestListing(b)?.current_price ?? Infinity),
      );
    } else if (filters.sort === "price_per_100g") {
      list = [...list].sort(
        (a, b) => (bestPricePer100g(a) ?? Infinity) - (bestPricePer100g(b) ?? Infinity),
      );
    }

    return limit ? list.slice(0, limit) : list;
  }, [products, filters, limit]);

  return (
    <section id="compare" className="mx-auto w-full max-w-7xl px-5 py-16 sm:px-8 sm:py-20">
      <div className="rounded-[32px] bg-secondary/60 p-5 sm:p-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <h2 className="font-display text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            {title}
          </h2>
          <p className="max-w-md text-sm text-muted-foreground">{description}</p>
        </div>

        <div className="mt-6">
          <Filters
            value={filters}
            onChange={setFilters}
            brands={options.brands}
            flavours={options.flavours}
            weights={options.weights}
            stores={options.stores}
            resultCount={query.isLoading ? undefined : visible.length}
          />
        </div>

        <div className="mt-6">
          {query.isLoading ? (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {Array.from({ length: limit ?? 8 }).map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))}
            </div>
          ) : query.isError ? (
            <StateCard
              icon={<AlertCircle className="h-5 w-5" />}
              title="We couldn't load prices"
              body="The WheyScan product service isn't responding right now. Check that it's running, then try again."
              action={
                <button
                  onClick={() => query.refetch()}
                  className="inline-flex h-10 items-center rounded-full bg-foreground px-5 text-sm font-medium text-background"
                >
                  Try again
                </button>
              }
            />
          ) : visible.length === 0 ? (
            <StateCard
              icon={<PackageSearch className="h-5 w-5" />}
              title="No matching products"
              body="Try a different brand, flavour or weight, or reset the filters to see every matched product."
              action={
                <button
                  onClick={() => setFilters(emptyFilters)}
                  className="inline-flex h-10 items-center rounded-full border border-border bg-card px-5 text-sm font-medium text-foreground"
                >
                  Reset filters
                </button>
              }
            />
          ) : (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {visible.map((p) => (
                <ProductCard key={`${p.product_id ?? "product"}-${p.id}`} product={p} />
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function StateCard({
  icon,
  title,
  body,
  action,
}: {
  icon: React.ReactNode;
  title: string;
  body: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-3xl border border-border bg-card px-6 py-16 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-secondary text-foreground">
        {icon}
      </span>
      <h3 className="font-display text-lg font-semibold text-foreground">{title}</h3>
      <p className="max-w-sm text-sm text-muted-foreground">{body}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
