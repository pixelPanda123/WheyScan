import { createFileRoute } from "@tanstack/react-router";

import { ComparisonSection } from "@/components/wheyscan/ComparisonSection";
import { Footer } from "@/components/wheyscan/Footer";
import { Hero } from "@/components/wheyscan/Hero";
import { Navbar } from "@/components/wheyscan/Navbar";
import { FinalCta, HowItWorks, PopularBrands, ShopSmarter } from "@/components/wheyscan/Sections";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "WheyScan — Browse whey products across Indian retailers" },
      {
        name: "description",
        content:
          "Browse whey protein products across Indian stores, see MRP and cost per 100g, and open retailer listings.",
      },
      { property: "og:title", content: "WheyScan — Find whey products across retailers" },
      {
        property: "og:description",
        content: "Whey protein retailer listings with MRP and price per 100g.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <Hero />
        <ComparisonSection limit={8} />
        <ShopSmarter />
        <PopularBrands />
        <HowItWorks />
        <FinalCta />
      </main>
      <Footer />
    </div>
  );
}
