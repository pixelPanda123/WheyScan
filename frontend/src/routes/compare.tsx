import { createFileRoute } from "@tanstack/react-router";

import { ComparisonSection } from "@/components/wheyscan/ComparisonSection";
import { Footer } from "@/components/wheyscan/Footer";
import { Navbar } from "@/components/wheyscan/Navbar";

export const Route = createFileRoute("/compare")({
  validateSearch: (search: Record<string, unknown>) => ({
    q: typeof search["q"] === "string" ? search["q"] : "",
  }),
  head: () => ({
    meta: [
      { title: "Browse whey products — WheyScan" },
      {
        name: "description",
        content:
          "Filter whey protein by brand, flavour, weight and retailer, then open live listings with MRP and cost per 100g.",
      },
      { property: "og:title", content: "Browse whey products — WheyScan" },
      {
        property: "og:description",
        content: "Live whey protein listings across Indian retailers.",
      },
    ],
  }),
  component: ComparePage,
});

function ComparePage() {
  const { q } = Route.useSearch();
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pt-4">
        <ComparisonSection
          title="Whey Product Listings"
          description="Every product below is listed by at least two retailers, so you can open the retailer source you prefer."
          initialQuery={q}
        />
      </main>
      <Footer />
    </div>
  );
}
