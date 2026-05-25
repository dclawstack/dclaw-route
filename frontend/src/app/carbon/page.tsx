"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  carbonApi,
  routesApi,
  type CarbonOptimizeResult,
  type FleetEmissions,
  type Route,
  type RouteEmissions,
} from "@/lib/api";

export default function CarbonPage() {
  const [summary, setSummary] = useState<FleetEmissions | null>(null);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [emissions, setEmissions] = useState<Record<string, RouteEmissions>>({});
  const [lastOptimize, setLastOptimize] = useState<CarbonOptimizeResult | null>(null);
  const [optimizing, setOptimizing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [s, r] = await Promise.all([
        carbonApi.summary(),
        routesApi.list(),
      ]);
      setSummary(s);
      setRoutes(r);
      const map: Record<string, RouteEmissions> = {};
      for (const route of r) {
        try {
          map[route.id] = await carbonApi.routeEmissions(route.id);
        } catch {
          /* ignore */
        }
      }
      setEmissions(map);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleOptimize(routeId: string) {
    setOptimizing(routeId);
    setError(null);
    try {
      setLastOptimize(await carbonApi.optimizeVehicle(routeId));
      refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setOptimizing(null);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Carbon emissions
        </h1>
      </header>
      <section className="mx-auto max-w-5xl px-6 py-8">
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        {summary && (
          <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Tile
              label="Total CO₂"
              value={`${summary.total_co2_kg.toFixed(1)} kg`}
            />
            <Tile
              label="Total km"
              value={summary.total_distance_km.toFixed(0)}
            />
            <Tile
              label="Avg g/km"
              value={summary.avg_co2_g_per_km.toFixed(0)}
            />
            <Tile label="Routes" value={summary.route_count.toString()} />
          </div>
        )}

        {lastOptimize && (
          <div className="mb-6 rounded bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            Assigned <strong>{lastOptimize.chosen_plate}</strong> (
            {lastOptimize.chosen_co2_g_per_km} g/km) — saves{" "}
            <strong>{lastOptimize.co2_saved_kg} kg CO₂</strong> vs the worst
            available choice.
          </div>
        )}

        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Per-route emissions
        </h2>
        <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Route</th>
                <th className="px-3 py-2 text-right">km</th>
                <th className="px-3 py-2">Vehicle</th>
                <th className="px-3 py-2 text-right">g/km</th>
                <th className="px-3 py-2 text-right">CO₂ (kg)</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {routes.map((r) => {
                const e = emissions[r.id];
                return (
                  <tr key={r.id} className="border-t">
                    <td className="px-3 py-2 font-medium">{r.name}</td>
                    <td className="px-3 py-2 text-right">
                      {r.total_distance_km.toFixed(1)}
                    </td>
                    <td className="px-3 py-2">
                      {e?.vehicle_plate ?? (
                        <span className="text-slate-400">none</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {e?.co2_g_per_km != null ? e.co2_g_per_km : "—"}
                    </td>
                    <td className="px-3 py-2 text-right font-semibold">
                      {e ? e.co2_total_kg.toFixed(2) : "—"}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <button
                        onClick={() => handleOptimize(r.id)}
                        disabled={optimizing === r.id}
                        className="rounded border px-2 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-50 disabled:opacity-50"
                      >
                        {optimizing === r.id ? "…" : "Optimize"}
                      </button>
                    </td>
                  </tr>
                );
              })}
              {routes.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-3 py-6 text-center text-sm text-slate-500"
                  >
                    No routes yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-white p-3 shadow-sm">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="mt-1 text-xl font-semibold text-slate-900">{value}</div>
    </div>
  );
}
