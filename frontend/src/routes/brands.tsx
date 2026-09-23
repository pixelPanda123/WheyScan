import { createFileRoute } from "@tanstack/react-router";

import { Footer } from "@/components/wheyscan/Footer";
import { Navbar } from "@/components/wheyscan/Navbar";
import { PopularBrands } from "@/components/wheyscan/Sections";

export const Route = createFileRoute("/brands")({
  head: () => ({
    meta: [
      { title: "Protein brands on WheyScan" },
      {
        name: "description",
        content:
          "Browse the whey protein brands WheyScan tracks across Indian retailers, from Optimum Nutrition onwards.",
      },
      { property: "og:title", content: "Protein brands on WheyScan" },
      {
        property: "og:description",
        content: "The whey protein brands currently listed on WheyScan.",
      },
    ],
  }),
  component: BrandsPage,
});

function BrandsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <section className="mx-auto w-full max-w-7xl px-5 pt-16 sm:px-8">
          <h1 className="font-display text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">
            Brands on WheyScan
          </h1>
          <p className="mt-4 max-w-xl text-sm text-muted-foreground">
            Pulled live from the products currently matched across two or more retailers.
          </p>
        </section>
        <PopularBrands />
      </main>
      <Footer />
    </div>
  );
}
