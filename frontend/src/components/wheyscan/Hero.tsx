import { Link, useNavigate } from "@tanstack/react-router";
import { Search } from "lucide-react";
import { useState } from "react";

import heroImage from "@/assets/hero-protein.jpg";

export function Hero() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  return (
    <section className="mx-auto w-full max-w-7xl px-5 pt-6 sm:px-8">
      <div className="relative overflow-hidden rounded-[32px] border border-border">
        <img
          src={heroImage}
          alt="Protein tub with a scoop of whey powder"
          width={1600}
          height={1104}
          className="h-[520px] w-full object-cover sm:h-[560px]"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-background/95 via-background/70 to-background/10" />

        <div className="absolute inset-0 flex items-center">
          <div className="w-full max-w-xl px-6 py-10 sm:px-12">
            <span className="inline-flex items-center rounded-full border border-border bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground">
              Retailer listings for Indian whey products
            </span>
            <h1 className="mt-5 font-display text-4xl leading-[1.05] font-semibold tracking-tight text-foreground sm:text-6xl">
              Find Whey Products Across Retailers
            </h1>
            <p className="mt-4 max-w-md text-base text-muted-foreground">
              WheyScan gathers retailer listings for the same whey product so you can check MRP,
              price per 100g, and open the store page that suits you.
            </p>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                void navigate({ to: "/compare", search: { q: query } });
              }}
              className="mt-7 flex flex-col gap-2 sm:flex-row"
            >
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search for a protein, brand, or flavour..."
                  className="h-12 w-full rounded-2xl border border-border bg-background pl-11 pr-4 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-foreground/50"
                />
              </div>
              <button
                type="submit"
                className="inline-flex h-12 items-center justify-center rounded-2xl bg-foreground px-6 text-sm font-medium text-background transition-transform hover:-translate-y-0.5"
              >
                Find Products
              </button>
            </form>

            <div className="mt-6 flex flex-wrap gap-x-8 gap-y-2 text-sm text-muted-foreground">
              <span>Matched across 2+ retailers</span>
              <span>Price per 100g on every product</span>
              <Link to="/about" className="underline underline-offset-4 hover:text-foreground">
                How it works
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
