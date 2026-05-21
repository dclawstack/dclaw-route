"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  driversApi,
  routesApi,
  stopsApi,
  type Driver,
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
            return (
              <li key={r.id} className="rounded-lg border bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{r.name}</div>
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                    {r.status}
                  </span>
                </div>
                <div className="text-sm text-slate-500">
                  {driver ? driver.name : "Unassigned"} · {r.deliveries.length} stops
                </div>
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
