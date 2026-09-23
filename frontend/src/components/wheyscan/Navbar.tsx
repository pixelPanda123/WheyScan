import { Link } from "@tanstack/react-router";
import { Search } from "lucide-react";

const links = [
  { to: "/", label: "Home" },
  { to: "/compare", label: "Products" },
  { to: "/brands", label: "Brands" },
  { to: "/about", label: "About" },
] as const;

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-md">
      <nav className="mx-auto flex h-16 w-full max-w-7xl items-center gap-6 px-5 sm:px-8">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-foreground text-[11px] font-bold text-background">
            WS
          </span>
          <span className="font-display text-lg font-semibold tracking-tight text-foreground">
            WheyScan
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              activeOptions={{ exact: l.to === "/" }}
              className="rounded-full px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              activeProps={{ className: "text-foreground" }}
            >
              {l.label}
            </Link>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Link
            to="/compare"
            search={{ q: "" }}
            className="hidden h-9 items-center gap-2 rounded-full border border-border bg-card px-3 text-sm text-muted-foreground transition-colors hover:text-foreground sm:flex"
          >
            <Search className="h-4 w-4" />
            Search
          </Link>
          <Link
            to="/compare"
            search={{ q: "" }}
            className="inline-flex h-9 items-center rounded-full bg-foreground px-4 text-sm font-medium text-background transition-transform hover:-translate-y-0.5"
          >
            Browse Products
          </Link>
        </div>
      </nav>
    </header>
  );
}
