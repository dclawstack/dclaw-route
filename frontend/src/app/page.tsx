import Link from "next/link";
import { MapPin, Truck, Route as RouteIcon, Map } from "lucide-react";

const tiles = [
  { href: "/stops", title: "Stops", desc: "Manage destinations and addresses", Icon: MapPin },
  { href: "/drivers", title: "Drivers", desc: "Driver roster and assignments", Icon: Truck },
  { href: "/routes", title: "Routes", desc: "Plan and dispatch routes", Icon: RouteIcon },
  { href: "/map", title: "Map", desc: "Visualize stops geographically", Icon: Map },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          DClaw Route
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-10">
        <h2 className="mb-6 text-2xl font-semibold">Dashboard</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {tiles.map(({ href, title, desc, Icon }) => (
            <Link
              key={href}
              href={href}
              className="rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md"
            >
              <Icon className="mb-3 h-6 w-6" style={{ color: "#10B981" }} />
              <div className="text-lg font-semibold">{title}</div>
              <p className="text-sm text-slate-600">{desc}</p>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
