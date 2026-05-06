"use client";

import React, { useState } from "react";
import { Map, Navigation } from "lucide-react";
import { api, RoutePlan, Waypoint } from "@/lib/api";

export default function DashboardPage() {
  const [stopsText, setStopsText] = useState("");
  const [plan, setPlan] = useState<RoutePlan | null>(null);
  const [waypoints, setWaypoints] = useState<Waypoint[] | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleOptimize(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setWaypoints(null);
    try {
      const stops = stopsText.split("\n").map((s) => s.trim()).filter(Boolean);
      const result = await api<RoutePlan>("/plans", {
        method: "POST",
        body: JSON.stringify({ stops }),
      });
      setPlan(result);
      const wp = await api<Waypoint[]>(`/plans/${result.id}/map`);
      setWaypoints(wp);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4 flex items-center gap-3">
        <Map className="h-6 w-6" style={{ color: "#2563EB" }} />
        <h1 className="text-xl font-bold" style={{ color: "#2563EB" }}>
          DClaw Route
        </h1>
      </header>

      <section className="mx-auto max-w-2xl px-6 py-10">
        <h2 className="mb-6 text-2xl font-semibold text-slate-800">Dashboard</h2>

        <form onSubmit={handleOptimize} className="mb-8 rounded-xl border bg-white p-6 shadow-sm">
          <div className="mb-6">
            <label htmlFor="stops" className="mb-1 block text-sm font-medium text-slate-700">
              Stops (one per line)
            </label>
            <textarea
              id="stops"
              rows={5}
              value={stopsText}
              onChange={(e) => setStopsText(e.target.value)}
              placeholder="Warehouse A&#10;Store B&#10;Store C"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-60"
            style={{ backgroundColor: "#2563EB" }}
          >
            <Navigation className="h-4 w-4" />
            {loading ? "Optimizing..." : "Optimize Route"}
          </button>
        </form>

        {plan && (
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-slate-800">Route Plan</h3>
            <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Total distance</dt>
                <dd className="mt-1 text-sm font-semibold text-slate-900">{plan.total_distance_km} km</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Estimated time</dt>
                <dd className="mt-1 text-sm font-semibold text-slate-900">{plan.estimated_time_minutes} min</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Fuel cost</dt>
                <dd className="mt-1 text-sm font-semibold text-slate-900">${plan.fuel_cost}</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Plan ID</dt>
                <dd className="mt-1 text-sm font-mono text-slate-900">{plan.id}</dd>
              </div>
            </dl>

            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500 mb-2">Original stops</dt>
                <ol className="list-decimal list-inside text-sm text-slate-900 space-y-1">
                  {plan.stops.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ol>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500 mb-2">Optimized sequence</dt>
                <ol className="list-decimal list-inside text-sm text-slate-900 space-y-1">
                  {plan.optimized_sequence.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ol>
              </div>
            </div>

            {waypoints && waypoints.length > 0 && (
              <div className="mt-6">
                <h4 className="mb-3 text-sm font-semibold text-slate-700">Waypoints</h4>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                  {waypoints.map((wp, i) => (
                    <div key={i} className="rounded-lg bg-slate-50 p-3 text-center">
                      <div className="text-xs font-medium text-slate-900">{wp.name}</div>
                      <div className="text-xs text-slate-500">{wp.lat.toFixed(4)}, {wp.lng.toFixed(4)}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
