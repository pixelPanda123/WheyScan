import { createFileRoute } from "@tanstack/react-router";

import { Footer } from "@/components/wheyscan/Footer";
import { Navbar } from "@/components/wheyscan/Navbar";
import { FinalCta, HowItWorks } from "@/components/wheyscan/Sections";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About WheyScan" },
      {
        name: "description",
        content:
          "WheyScan matches identical whey protein products across Indian retailers so you can check MRP and open retailer listings.",
      },
      { property: "og:title", content: "About WheyScan" },
      {
        property: "og:description",
        content: "Why WheyScan exists and how retailer listing discovery works.",
      },
    ],
  }),
  component: AboutPage,
});

function AboutPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <section className="mx-auto w-full max-w-7xl px-5 pt-16 sm:px-8">
          <h1 className="max-w-3xl font-display text-4xl font-semibold leading-tight tracking-tight text-foreground sm:text-6xl">
            Protein pricing, without the guesswork.
          </h1>
          <p className="mt-5 max-w-xl text-base text-muted-foreground">
            The same tub can be listed differently depending on where you buy it. WheyScan matches
            identical products across Indian retailers and normalises everything to a price per
            100g, so you can review each source with less guesswork.
          </p>
        </section>
        <HowItWorks />
        <FinalCta />
      </main>
      <Footer />
    </div>
  );
}
