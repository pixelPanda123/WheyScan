import { ArrowUpRight, ImageOff } from "lucide-react";

import {
  availableListings,
  bestPricePer100g,
  brandOf,
  formatINR,
  formatPer100g,
  storeLabel,
  weightLabel,
  type Product,
} from "@/lib/api";

export function ProductCard({ product }: { product: Product }) {
  const listings = [...availableListings(product)].sort(
    (a, b) => a.current_price - b.current_price,
  );
  const per100g = bestPricePer100g(product);
  const meta = [weightLabel(product), product.flavour].filter(Boolean).join(" · ");

  return (
    <article className="group flex flex-col overflow-hidden rounded-3xl border border-border bg-card transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_18px_40px_-24px_rgb(0_0_0/0.35)]">
      <div className="relative aspect-4/3 overflow-hidden bg-secondary">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            loading="lazy"
            className="h-full w-full object-contain p-6 transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-muted-foreground">
            <ImageOff className="h-6 w-6" />
          </div>
        )}
        <span className="absolute left-4 top-4 rounded-full bg-background/90 px-3 py-1 text-xs font-medium text-foreground">
          {listings.length} retailers
        </span>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
          {brandOf(product)}
        </p>
        <h3 className="mt-1.5 font-display text-lg leading-snug font-semibold text-foreground">
          {product.name}
        </h3>
        {meta && <p className="mt-1 text-sm text-muted-foreground">{meta}</p>}

        <ul className="mt-4 divide-y divide-border rounded-2xl border border-border/80 bg-background">
          {listings.map((listing, index) => {
            return (
              <li
                key={
                  listing.listing_id ?? `${listing.store_name}-${listing.current_price}-${index}`
                }
                className="grid grid-cols-[1fr_auto] items-center gap-x-3 gap-y-1 px-4 py-3"
              >
                <span className="text-sm font-medium text-foreground">
                  {storeLabel(listing.store_name)}
                </span>
                <span className="text-sm font-semibold text-foreground">
                  {formatINR(listing.current_price)}
                </span>
                <span className="text-xs text-muted-foreground">
                  {typeof listing.price_per_100g === "number"
                    ? formatPer100g(listing.price_per_100g)
                    : "Price per 100g unavailable"}
                </span>
                {listing.product_url ? (
                  <a
                    href={listing.product_url}
                    target="_blank"
                    rel="noreferrer noopener"
                    className="inline-flex items-center justify-self-end text-xs font-medium text-foreground underline-offset-4 hover:underline"
                  >
                    Open
                    <ArrowUpRight className="ml-1 h-3.5 w-3.5" />
                  </a>
                ) : (
                  <span className="justify-self-end text-xs text-muted-foreground">No link</span>
                )}
              </li>
            );
          })}
          {listings.length === 0 && (
            <li className="px-4 py-3 text-sm text-muted-foreground">Currently unavailable</li>
          )}
        </ul>

        <div className="mt-auto flex items-center justify-between gap-3 pt-5">
          <span className="text-sm text-muted-foreground">
            {per100g ? formatPer100g(per100g) : "—"}
          </span>
          <span className="text-sm text-muted-foreground">MRP sources</span>
        </div>
      </div>
    </article>
  );
}

export function ProductCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-3xl border border-border bg-card">
      <div className="aspect-4/3 animate-pulse bg-secondary" />
      <div className="space-y-3 p-5">
        <div className="h-3 w-24 animate-pulse rounded-full bg-secondary" />
        <div className="h-5 w-3/4 animate-pulse rounded-full bg-secondary" />
        <div className="h-3 w-1/3 animate-pulse rounded-full bg-secondary" />
        <div className="h-24 animate-pulse rounded-2xl bg-secondary" />
        <div className="flex items-center justify-between pt-1">
          <div className="h-3 w-24 animate-pulse rounded-full bg-secondary" />
          <div className="h-9 w-28 animate-pulse rounded-full bg-secondary" />
        </div>
      </div>
    </div>
  );
}
