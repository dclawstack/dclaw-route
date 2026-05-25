"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  gigApi,
  routesApi,
  type GigAssignment,
  type GigDriver,
  type Route,
} from "@/lib/api";

export default function GigPage() {
  const [drivers, setDrivers] = useState<GigDriver[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [form, setForm] = useState({
    name: "",
    rating: "4.5",
    vehicle_type: "car",
  });
  const [routeId, setRouteId] = useState("");
  const [vehicleType, setVehicleType] = useState("");
  const [result, setResult] = useState<GigAssignment | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [d, r] = await Promise.all([gigApi.list(), routesApi.list()]);
      setDrivers(d);
      setRoutes(r);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleAddDriver(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await gigApi.create({
        name: form.name,
        rating: parseFloat(form.rating),
        vehicle_type: form.vehicle_type,
        status: "available",
      });
      setForm({ name: "", rating: "4.5", vehicle_type: "car" });
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleRequest(e: React.FormEvent) {
    e.preventDefault();
    if (!routeId) return;
    setError(null);
    setResult(null);
    try {
      const res = await gigApi.request({
        route_id: routeId,
        vehicle_type: vehicleType || undefined,
      });
      setResult(res);
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleRelease(gigId: string) {
    try {
      await gigApi.release(gigId);
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  const statusColor = (s: string) =>
    s === "available"
      ? "bg-emerald-100 text-emerald-800"
      : s === "busy"
        ? "bg-amber-100 text-amber-800"
        : "bg-slate-200 text-slate-600";

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Crowdsourced gig drivers
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Request a gig driver for a route
        </h2>
        <form
          onSubmit={handleRequest}
          className="mb-8 grid grid-cols-1 gap-2 rounded-xl border bg-white p-4 shadow-sm sm:grid-cols-3"
        >
          <select
            value={routeId}
            onChange={(e) => setRouteId(e.target.value)}
            className="rounded border px-3 py-2 text-sm"
            required
          >
            <option value="">— Route —</option>
            {routes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
          <select
            value={vehicleType}
            onChange={(e) => setVehicleType(e.target.value)}
            className="rounded border px-3 py-2 text-sm"
          >
            <option value="">— Any vehicle —</option>
            <option value="car">Car</option>
            <option value="bike">Bike</option>
            <option value="van">Van</option>
            <option value="truck">Truck</option>
          </select>
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            Find driver
          </button>
        </form>
        {result && (
          <div className="mb-6 rounded bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            Assigned <strong>{result.gig_driver_name}</strong> (★{result.rating},{" "}
            {result.vehicle_type})
            {result.distance_km !== null && ` · ${result.distance_km} km away`}
          </div>
        )}
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Gig driver pool
        </h2>
        <ul className="mb-8 space-y-2">
          {drivers.map((d) => (
            <li
              key={d.id}
              className="flex items-center justify-between rounded-lg border bg-white p-3 shadow-sm"
            >
              <div>
                <div className="font-medium">
                  {d.name}{" "}
                  <span className="text-xs text-amber-600">★{d.rating.toFixed(1)}</span>
                </div>
                <div className="text-xs text-slate-500">
                  {d.vehicle_type}
                  {d.current_lat != null &&
                    ` · 📍 ${d.current_lat.toFixed(3)}, ${d.current_lng?.toFixed(3)}`}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-2 py-0.5 text-xs uppercase ${statusColor(
                    d.status
                  )}`}
                >
                  {d.status}
                </span>
                {d.status === "busy" && (
                  <button
                    onClick={() => handleRelease(d.id)}
                    className="text-xs text-slate-500 hover:underline"
                  >
                    Release
                  </button>
                )}
              </div>
            </li>
          ))}
          {drivers.length === 0 && (
            <li className="rounded-lg border bg-white p-4 text-center text-sm text-slate-500">
              No gig drivers yet — add one below.
            </li>
          )}
        </ul>

        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Add gig driver
        </h2>
        <form
          onSubmit={handleAddDriver}
          className="grid grid-cols-1 gap-2 rounded-xl border bg-white p-4 shadow-sm sm:grid-cols-4"
        >
          <input
            className="rounded border px-3 py-2 text-sm sm:col-span-2"
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <input
            type="number"
            step="0.1"
            min="1"
            max="5"
            className="rounded border px-3 py-2 text-sm"
            placeholder="Rating"
            value={form.rating}
            onChange={(e) => setForm({ ...form, rating: e.target.value })}
          />
          <select
            value={form.vehicle_type}
            onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}
            className="rounded border px-3 py-2 text-sm"
          >
            <option value="car">Car</option>
            <option value="bike">Bike</option>
            <option value="van">Van</option>
            <option value="truck">Truck</option>
          </select>
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white sm:col-span-4"
            style={{ backgroundColor: "#10B981" }}
          >
            Add to pool
          </button>
        </form>
      </section>
    </main>
  );
}
