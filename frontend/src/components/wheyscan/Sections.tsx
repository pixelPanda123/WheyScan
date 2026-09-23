import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { PackageSearch, Scale, Store } from "lucide-react";

import { brandOf, searchProducts } from "@/lib/api";

export function ShopSmarter() {
  const items = [
    {
      icon: Store,
      title: "See retailer listings",
      body: "Every matched product shows store listings and direct retailer links.",
    },
    {
      icon: Scale,
      title: "Track price per 100g",
      body: "Different tub sizes, one normalised number for quick review.",
    },
    {
      icon: PackageSearch,
      title: "Find the right product",
      body: "Filter by brand, flavour and weight until it's exactly what you want.",
    },
  ];

  return (
    <section className="mx-auto w-full max-w-7xl px-5 py-10 sm:px-8">
      <h2 className="font-display text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
        Shop Smarter
      </h2>
      <div className="mt-6 grid gap-5 md:grid-cols-3">
        {items.map(({ icon: Icon, title, body }) => (
          <div
            key={title}
            className="rounded-3xl border border-border bg-card p-6 transition-colors hover:border-foreground/25"
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-foreground">
              <Icon className="h-5 w-5" />
            </span>
            <h3 className="mt-4 font-display text-lg font-semibold text-foreground">{title}</h3>
            <p className="mt-1.5 text-sm text-muted-foreground">{body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function PopularBrands() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["products", "", "all", "all", "all"],
    queryFn: ({ signal }) => searchProducts({}, signal),
    retry: 1,
  });

  const brands = Array.from(new Set((data ?? []).map((p) => brandOf(p)))).slice(0, 8);

  return (
    <section className="mx-auto w-full max-w-7xl px-5 py-10 sm:px-8">
      <div className="flex items-end justify-between gap-4">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
          Popular Brands
        </h2>
        <Link to="/brands" className="text-sm text-muted-foreground hover:text-foreground">
          View all
        </Link>
      </div>

      <div className="mt-6 flex gap-4 overflow-x-auto pb-2">
        {isLoading &&
          Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-24 w-44 shrink-0 animate-pulse rounded-3xl border border-border bg-secondary"
            />
          ))}

        {!isLoading && (isError || brands.length === 0) && (
          <p className="text-sm text-muted-foreground">
            Brands appear here once the product service returns listings.
          </p>
        )}

        {brands.map((brand) => (
          <div
            key={brand}
            className="flex h-24 w-44 shrink-0 items-center justify-center rounded-3xl border border-border bg-card px-4 text-center transition-all hover:-translate-y-1 hover:shadow-[0_14px_30px_-22px_rgb(0_0_0/0.4)]"
          >
            <span className="font-display text-sm font-semibold text-foreground">{brand}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function HowItWorks() {
  const steps = [
    { n: "01", title: "Search", body: "Look up a protein, brand or flavour." },
    { n: "02", title: "Review", body: "See retailer MRP, availability, and cost per 100g." },
    { n: "03", title: "Open", body: "Go straight to the retailer listing you want." },
  ];

  return (
    <section className="mx-auto w-full max-w-7xl px-5 py-10 sm:px-8">
      <h2 className="font-display text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
        How WheyScan Works
      </h2>
      <div className="mt-6 grid gap-5 md:grid-cols-3">
        {steps.map((s) => (
          <div key={s.n} className="rounded-3xl bg-secondary/70 p-6">
            <span className="font-display text-sm font-semibold text-muted-foreground">{s.n}</span>
            <h3 className="mt-3 font-display text-xl font-semibold text-foreground">{s.title}</h3>
            <p className="mt-1.5 text-sm text-muted-foreground">{s.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function FinalCta() {
  return (
    <section className="mx-auto w-full max-w-7xl px-5 py-12 sm:px-8">
      <div className="flex flex-col items-start gap-6 rounded-[32px] bg-foreground px-8 py-14 text-background sm:px-14">
        <h2 className="max-w-2xl font-display text-3xl leading-tight font-semibold tracking-tight sm:text-5xl">
          Stop checking five stores for one protein.
        </h2>
        <p className="text-lg text-background/70">Find it on WheyScan.</p>
        <Link
          to="/compare"
          search={{ q: "" }}
          className="inline-flex h-12 items-center rounded-full bg-background px-7 text-sm font-medium text-foreground transition-transform hover:-translate-y-0.5"
        >
          Browse Products
        </Link>
      </div>
    </section>
  );
}
