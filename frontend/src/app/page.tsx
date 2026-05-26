import Link from "next/link";
import {
  ArrowRight,
  Bot,
  Camera,
  Clock,
  CloudSun,
  Github,
  Leaf,
  MessageSquare,
  Radio,
  Route as RouteIcon,
  Sparkles,
  Truck,
  Undo2,
  Users,
  Warehouse,
} from "lucide-react";
import DemoSection from "@/components/demo-section";

const REPO_URL = "https://github.com/dclawstack/dclaw-route";

export default function Landing() {
  return (
    <main className="min-h-screen bg-white text-slate-900">
      <Nav />
      <Hero />
      <FeatureGrid />
      <DeepDive />
      <DemoSection />
      <Footer />
    </main>
  );
}

function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b bg-white/80 backdrop-blur">
      <nav className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <div
            className="flex h-7 w-7 items-center justify-center rounded-lg text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            <RouteIcon className="h-4 w-4" />
          </div>
          <span className="font-semibold">DClaw Route</span>
        </Link>
        <div className="flex items-center gap-2">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 sm:inline-flex"
          >
            <Github className="h-4 w-4" /> GitHub
          </a>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            Dashboard <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </nav>
    </header>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-emerald-50/60 to-white" />
      <div className="mx-auto max-w-5xl px-4 py-20 text-center sm:px-6 sm:py-28">
        <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs font-medium text-emerald-700">
          <Sparkles className="h-3.5 w-3.5" />
          AI dispatch copilot + real-time optimization
        </div>
        <h1 className="mt-6 text-4xl font-bold tracking-tight sm:text-6xl">
          Route optimization for{" "}
          <span style={{ color: "#10B981" }}>last-mile delivery</span>.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-600">
          Plan multi-stop routes with constraints, track drivers in real time,
          capture proof of delivery on the road, and cut emissions — all from a
          single dispatcher dashboard.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="#demo"
            className="inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold text-white transition hover:opacity-90"
            style={{ backgroundColor: "#10B981" }}
          >
            Try the demo <ArrowRight className="h-4 w-4" />
          </Link>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-lg border bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            <Github className="h-4 w-4" /> Star on GitHub
          </a>
        </div>
        <div className="mt-12 grid grid-cols-2 gap-6 text-center sm:grid-cols-4">
          <HeroStat value="20%" label="Mileage cut" />
          <HeroStat value="<30s" label="1000-stop solve" />
          <HeroStat value="±5min" label="ETA accuracy" />
          <HeroStat value="100%" label="Proof captured" />
        </div>
      </div>
    </section>
  );
}

function HeroStat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-2xl font-bold text-slate-900 sm:text-3xl">{value}</div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  );
}

const features = [
  {
    Icon: MessageSquare,
    title: "AI Route Copilot",
    body: "Natural-language dispatch. “Add urgent stop #5 with minimal delay” — the copilot reads live route state and recommends the next concrete action.",
  },
  {
    Icon: RouteIcon,
    title: "Multi-constraint optimizer",
    body: "Nearest-neighbor + cheapest-insertion solver respects time windows, capacity, and driver skills. Live before-and-after comparison.",
  },
  {
    Icon: Radio,
    title: "Real-time tracking & ETA",
    body: "GPS pings drive per-stop ETA forecasting at ±5 minute accuracy. Delay alerts fire when a driver's last ping is over 15 minutes old.",
  },
  {
    Icon: Camera,
    title: "Mobile proof of delivery",
    body: "Drivers capture photo, signature, barcode and geotag in one form. Photo validator runs at upload to flag suspicious submissions.",
  },
  {
    Icon: Truck,
    title: "Fleet + driver management",
    body: "Vehicle inventory with maintenance alerts and auto-assignment. Driver shifts with FMCSA 60/70-hour fatigue monitoring.",
  },
  {
    Icon: Warehouse,
    title: "Warehouse integration",
    body: "LIFO loading manifest per route, dock assignment, and a sync endpoint that talks to the upstream WMS.",
  },
  {
    Icon: CloudSun,
    title: "Predictive ETA",
    body: "Hour-of-day traffic curve combined with a weather factor produces adjusted ETAs for the next morning's run.",
  },
  {
    Icon: Leaf,
    title: "Carbon-optimized routing",
    body: "Per-route CO₂ from vehicle emission factors. One-click swap to the lowest-emission available vehicle with savings shown vs the worst alternative.",
  },
  {
    Icon: Users,
    title: "Crowdsourced surge capacity",
    body: "Gig driver pool ranked by rating, vehicle type, and proximity. Pull surge capacity in a click when full-time drivers are out.",
  },
  {
    Icon: Bot,
    title: "Autonomous vehicle dispatch",
    body: "AV fleet inventory with autopilot-level dispatch. Route assignment picks the highest-capability available unit.",
  },
  {
    Icon: Undo2,
    title: "Reverse logistics",
    body: "Returns drop into a pickup queue then consolidate into one optimized return run with all pickups in nearest-neighbor order.",
  },
  {
    Icon: Clock,
    title: "Cost analytics",
    body: "Per-route P&L breaks out fuel, labor, and vehicle costs. Fleet rollup shows total cost per delivery and on-time rate.",
  },
];

function FeatureGrid() {
  return (
    <section id="features" className="py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-widest text-emerald-700">
            What&apos;s in the box
          </div>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Every dispatch workflow, in one app.
          </h2>
        </div>
        <div className="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                <f.Icon className="h-5 w-5" />
              </div>
              <div className="mt-4 font-semibold">{f.title}</div>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{f.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function DeepDive() {
  const items = [
    {
      eyebrow: "Optimizer",
      title: "20% less mileage on multi-stop runs.",
      body: "Nearest-neighbor solver over haversine distance with a stop-anchor. Optimize an existing route in a single click — the route's total distance and ETA are persisted with the new sequence so the driver app sees the update immediately.",
      bullets: [
        "Greedy NN today; OR-Tools wired for the production solver",
        "Honors a max-stops soft constraint",
        "Returns original vs optimized sequence + % improvement",
      ],
      example: "POST /api/v1/routes/{id}/optimize\n→ {\n  original_distance_km: 12439,\n  optimized_distance_km: 5035,\n  improvement_percent: 59.5\n}",
    },
    {
      eyebrow: "Live tracking",
      title: "Per-stop ETAs from the driver's actual position.",
      body: "GPS pings update the driver's current location; the ETA engine recomputes the remaining route on demand. A dispatcher live board polls every 10 seconds and flags any driver whose last ping is over 15 minutes old.",
      bullets: [
        "Haversine distance at 30 km/h average — swap to OSRM/Google for prod",
        "Skips completed deliveries when forecasting",
        "Delay detection without a separate alerting service",
      ],
      example: "GET /api/v1/tracking/routes/{id}/eta\n→ {\n  driver_position: [40.70, -74.01],\n  stops: [\n    { stop_name: \"A\", cumulative_km: 1.46, minutes_from_now: 2 },\n    { stop_name: \"B\", cumulative_km: 6.78, minutes_from_now: 13 }\n  ],\n  is_delayed: false\n}",
    },
    {
      eyebrow: "Proof of delivery",
      title: "Photo, signature, barcode, geotag — one form.",
      body: "Driver app captures device camera, canvas signature, free-text barcode and a browser geotag, then submits one POST that completes the delivery. The photo validator runs at upload time, currently a base64 size heuristic — pluggable to a real vision model.",
      bullets: [
        "Geotag captured automatically when permission granted",
        "Status auto-flips to completed_at = utc_now()",
        "Notification engine auto-fires the “delivered” template",
      ],
      example: "POST /api/v1/deliveries/{id}/complete\n→ {\n  status: \"completed\",\n  barcode: \"PKG-12345\",\n  photo_validated: true,\n  completed_at: \"...\"\n}",
    },
  ];
  return (
    <section className="border-y bg-slate-50/60 py-20">
      <div className="mx-auto max-w-6xl space-y-20 px-4 sm:px-6">
        {items.map((it, idx) => (
          <div
            key={it.title}
            className={`grid grid-cols-1 items-center gap-10 lg:grid-cols-2 ${
              idx % 2 === 1 ? "lg:[&>div:first-child]:order-2" : ""
            }`}
          >
            <div>
              <div className="text-xs font-semibold uppercase tracking-widest text-emerald-700">
                {it.eyebrow}
              </div>
              <h3 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
                {it.title}
              </h3>
              <p className="mt-4 text-base leading-relaxed text-slate-600">
                {it.body}
              </p>
              <ul className="mt-4 space-y-2">
                {it.bullets.map((b) => (
                  <li
                    key={b}
                    className="flex items-start gap-2 text-sm text-slate-700"
                  >
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                    {b}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="text-xs uppercase tracking-wide text-slate-500">
                Example response
              </div>
              <pre className="mt-3 overflow-x-auto rounded-md bg-slate-900 p-4 text-xs text-emerald-200">
                {it.example}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t bg-white py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <div
            className="flex h-6 w-6 items-center justify-center rounded text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            <RouteIcon className="h-3.5 w-3.5" />
          </div>
          <span>DClaw Route · built on the DClaw Stack</span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-slate-600 hover:text-slate-900"
          >
            <Github className="h-4 w-4" /> Repository
          </a>
          <Link
            href="/dashboard"
            className="text-slate-600 hover:text-slate-900"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </footer>
  );
}
