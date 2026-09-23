export const API_BASE_URL =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? "http://localhost:8001";

export interface Listing {
  listing_id?: number | undefined;
  store_id?: number | undefined;
  store_name: string;
  current_price: number;
  price_per_100g: number | null;
  availability: boolean;
  product_url: string | null;
}

export interface Product {
  id: number;
  product_id?: number | undefined;
  name: string;
  brand: string | null;
  brand_id?: number | null | undefined;
  brand_name?: string | null | undefined;
  protein_type?: string | null | undefined;
  flavour: string | null;
  weight: number | null;
  weight_unit: string | null;
  image_url: string | null;
  listings: Listing[];
}

export interface SearchParams {
  q?: string | undefined;
  brand?: string | undefined;
  flavour?: string | undefined;
  weight?: string | undefined;
  store?: string | undefined;
}

/** Fetches retailer-backed products from the existing discovery API. */
export async function searchProducts(
  params: SearchParams = {},
  signal?: AbortSignal,
): Promise<Product[]> {
  const url = new URL("/discovery/search", API_BASE_URL);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "" && value !== "all") {
      url.searchParams.set(key, String(value));
    }
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Search failed (${res.status})`);
  }

  const data: unknown = await res.json();
  if (Array.isArray(data)) return data as Product[];
  if (data && typeof data === "object") {
    const record = data as Record<string, unknown>;
    for (const key of ["results", "items", "products", "data"]) {
      if (Array.isArray(record[key])) return record[key] as Product[];
    }
  }
  return [];
}

/* ---------- derived helpers ---------- */

export function availableListings(product: Product): Listing[] {
  return product.listings.filter((l) => l.availability !== false);
}

export function bestListing(product: Product): Listing | undefined {
  return [...availableListings(product)].sort((a, b) => a.current_price - b.current_price)[0];
}

export function bestPricePer100g(product: Product): number | undefined {
  const values = availableListings(product)
    .map((l) => l.price_per_100g)
    .filter((v): v is number => typeof v === "number");
  return values.length ? Math.min(...values) : undefined;
}

export function formatINR(value: number): string {
  return `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

export function formatPer100g(value: number): string {
  return `₹${value.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} / 100g`;
}

export function storeLabel(name: string): string {
  return name
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function brandOf(product: Product): string {
  return product.brand_name ?? product.brand ?? "Unbranded";
}

export function weightLabel(product: Product): string | null {
  if (!product.weight) return null;
  return `${product.weight}${product.weight_unit ?? "g"}`;
}
