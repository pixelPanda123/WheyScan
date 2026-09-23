import { Link } from "@tanstack/react-router";

export function Footer() {
  return (
    <footer className="mx-auto w-full max-w-7xl px-5 pb-12 sm:px-8">
      <div className="flex flex-col gap-4 border-t border-border pt-8 sm:flex-row sm:items-center sm:justify-between">
        <span className="font-display text-sm font-semibold text-foreground">WheyScan</span>
        <div className="flex flex-wrap gap-5 text-sm text-muted-foreground">
          <Link to="/compare" search={{ q: "" }} className="hover:text-foreground">
            Products
          </Link>
          <Link to="/brands" className="hover:text-foreground">
            Brands
          </Link>
          <Link to="/about" className="hover:text-foreground">
            About
          </Link>
        </div>
        <p className="text-xs text-muted-foreground">
          Prices are indicative and sourced from retailer listings.
        </p>
      </div>
    </footer>
  );
}
