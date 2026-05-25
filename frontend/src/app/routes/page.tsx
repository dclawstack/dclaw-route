"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  driversApi,
  routesApi,
  stopsApi,
  type Driver,
  type InsertUrgentResult,
  type OptimizeResult,
  type Route,
  type Stop,
} from "@/lib/api";

export default function RoutesPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [stops, setStops] = useState<Stop[]>([]);
  const [name, setName] = useState("");
  const [driverId, setDriverId] = useState<string>("");
  const [selectedStops, setSelectedStops] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [optimizing, setOptimizing] = useState<string | null>(null);
  const [optimizeResults, setOptimizeResults] = useState<Record<string, OptimizeResult>>({});
  const [urgentStop, setUrgentStop] = useState<Record<string, string>>({});
  const [urgentResults, setUrgentResults] = useState<Record<string, InsertUrgentResult>>({});

  async function refresh() {
    try {
      const [r, d, s] = await Promise.all([
        routesApi.list(),
        driversApi.list(),
        stopsApi.list(),
      ]);
      setRoutes(r);
      setDrivers(d);
      setStops(s);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await routesApi.create({
        name,
        driver_id: driverId || null,
        stop_ids: selectedStops,
      });
      setName("");
      setDriverId("");
      setSelectedStops([]);
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  function toggleStop(id: string) {
    setSelectedStops((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleOptimize(routeId: string) {
    setOptimizing(routeId);
    setError(null);
    try {
      const result = await routesApi.optimize(routeId);
      setOptimizeResults((prev) => ({ ...prev, [routeId]: result }));
      refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setOptimizing(null);
    }
  }

  async function handleInsertUrgent(routeId: string) {
    const stopId = urgentStop[routeId];
    if (!stopId) return;
    setError(null);
    try {
      const result = await routesApi.insertUrgent(routeId, stopId);
      setUrgentResults((prev) => ({ ...prev, [routeId]: result }));
      setUrgentStop((prev) => ({ ...prev, [routeId]: "" }));
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Routes
        </h1>
      </header>
      <section className="mx-auto max-w-3xl px-6 py-8">
        <form
          onSubmit={handleCreate}
          className="mb-8 space-y-3 rounded-xl border bg-white p-6 shadow-sm"
        >
          <input
            className="w-full rounded border px-3 py-2 text-sm"
            placeholder="Route name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={driverId}
            onChange={(e) => setDriverId(e.target.value)}
          >
            <option value="">— Unassigned —</option>
            {drivers.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
          <div>
            <div className="mb-2 text-sm font-medium text-slate-700">
              Stops ({selectedStops.length} selected)
            </div>
            <div className="max-h-48 space-y-1 overflow-y-auto rounded border bg-slate-50 p-2">
              {stops.length === 0 && (
                <div className="text-xs text-slate-500">
                  No stops — add some on the Stops page first.
                </div>
              )}
              {stops.map((s) => (
                <label
                  key={s.id}
                  className="flex items-center gap-2 rounded px-2 py-1 hover:bg-white"
                >
                  <input
                    type="checkbox"
                    checked={selectedStops.includes(s.id)}
                    onChange={() => toggleStop(s.id)}
                  />
                  <span className="text-sm">
                    {s.name} <span className="text-slate-400">— {s.address}</span>
                  </span>
                </label>
              ))}
            </div>
          </div>
          <button
            type="submit"
            className="rounded px-4 py-2 text-sm font-semibold text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            Create route
          </button>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}
        <ul className="space-y-2">
          {routes.map((r) => {
            const driver = drivers.find((d) => d.id === r.driver_id);
            const result = optimizeResults[r.id];
            return (
              <li key={r.id} className="rounded-lg border bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{r.name}</div>
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                    {r.status}
                  </span>
                </div>
                <div className="text-sm text-slate-500">
                  {driver ? driver.name : "Unassigned"} · {r.deliveries.length} stops ·{" "}
                  {r.total_distance_km.toFixed(2)} km
                </div>
                {r.deliveries.length >= 2 && (
                  <button
                    onClick={() => handleOptimize(r.id)}
                    disabled={optimizing === r.id}
                    className="mt-2 rounded px-3 py-1 text-xs font-semibold text-white disabled:opacity-50"
                    style={{ backgroundColor: "#10B981" }}
                  >
                    {optimizing === r.id ? "Optimizing…" : "Optimize"}
                  </button>
                )}
                {result && (
                  <div className="mt-3 grid grid-cols-3 gap-2 rounded bg-slate-50 p-3 text-xs">
                    <div>
                      <div className="font-semibold text-slate-500">Before</div>
                      <div className="text-slate-900">
                        {result.original_distance_km.toFixed(2)} km
                      </div>
                    </div>
                    <div>
                      <div className="font-semibold text-slate-500">After</div>
                      <div className="text-slate-900">
                        {result.optimized_distance_km.toFixed(2)} km
                      </div>
                    </div>
                    <div>
                      <div className="font-semibold text-slate-500">Saved</div>
                      <div className="text-emerald-700">
                        {result.improvement_percent.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                )}
                <div className="mt-3 flex gap-2">
                  <select
                    value={urgentStop[r.id] || ""}
                    onChange={(e) =>
                      setUrgentStop({ ...urgentStop, [r.id]: e.target.value })
                    }
                    className="flex-1 rounded border px-2 py-1 text-xs"
                  >
                    <option value="">— Insert urgent stop —</option>
                    {stops.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => handleInsertUrgent(r.id)}
                    disabled={!urgentStop[r.id]}
                    className="rounded border px-3 py-1 text-xs font-semibold text-amber-700 hover:bg-amber-50 disabled:opacity-50"
                  >
                    Insert
                  </button>
                </div>
                {urgentResults[r.id] && (
                  <div className="mt-2 rounded bg-amber-50 p-2 text-xs text-amber-900">
                    Inserted at position {urgentResults[r.id].inserted_at_position} ·
                    +{urgentResults[r.id].extra_distance_km.toFixed(2)} km · +
                    {urgentResults[r.id].extra_minutes} min ·{" "}
                    {urgentResults[r.id].shifted_stops.length} stops shifted
                  </div>
                )}
              </li>
            );
          })}
          {routes.length === 0 && (
            <li className="rounded-lg border bg-white p-6 text-center text-sm text-slate-500">
              No routes yet.
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}
