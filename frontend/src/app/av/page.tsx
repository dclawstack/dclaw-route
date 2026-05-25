"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  avApi,
  routesApi,
  type AutonomousVehicle,
  type DispatchResult,
  type Route,
} from "@/lib/api";

export default function AvPage() {
  const [avs, setAvs] = useState<AutonomousVehicle[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [form, setForm] = useState({
    vendor: "Waymo",
    model: "",
    autopilot_level: "4",
    capacity_kg: "500",
  });
  const [routeId, setRouteId] = useState("");
  const [minLevel, setMinLevel] = useState("4");
  const [result, setResult] = useState<DispatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [a, r] = await Promise.all([avApi.list(), routesApi.list()]);
      setAvs(a);
      setRoutes(r);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await avApi.create({
        vendor: form.vendor,
        model: form.model,
        autopilot_level: parseInt(form.autopilot_level),
        capacity_kg: parseFloat(form.capacity_kg),
        status: "available",
      });
      setForm({ vendor: "Waymo", model: "", autopilot_level: "4", capacity_kg: "500" });
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleDispatch(e: React.FormEvent) {
    e.preventDefault();
    if (!routeId) return;
    setError(null);
    setResult(null);
    try {
      setResult(await avApi.dispatch(routeId, parseInt(minLevel)));
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleRecall(avId: string) {
    try {
      await avApi.recall(avId);
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  const statusColor = (s: string) =>
    s === "available"
      ? "bg-emerald-100 text-emerald-800"
      : s === "dispatched"
        ? "bg-blue-100 text-blue-800"
        : "bg-slate-200 text-slate-600";

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Autonomous fleet
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        <p className="mb-4 text-sm text-slate-500">
          Dispatch AVs by autopilot level. Levels: 3 (conditional), 4 (high),
          5 (full).
        </p>

        <form
          onSubmit={handleDispatch}
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
            value={minLevel}
            onChange={(e) => setMinLevel(e.target.value)}
            className="rounded border px-3 py-2 text-sm"
          >
            <option value="3">Min level 3</option>
            <option value="4">Min level 4</option>
            <option value="5">Min level 5 only</option>
          </select>
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            Dispatch
          </button>
        </form>
        {result && (
          <div className="mb-6 rounded bg-blue-50 px-3 py-2 text-sm text-blue-800">
            Dispatched <strong>{result.vendor} {result.model}</strong> (Level{" "}
            {result.autopilot_level})
          </div>
        )}
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        <h2 className="mb-3 text-sm font-semibold text-slate-600">AV fleet</h2>
        <ul className="mb-8 space-y-2">
          {avs.map((a) => (
            <li
              key={a.id}
              className="flex items-center justify-between rounded-lg border bg-white p-3 shadow-sm"
            >
              <div>
                <div className="font-medium">
                  {a.vendor} {a.model}
                </div>
                <div className="text-xs text-slate-500">
                  Level {a.autopilot_level} · {a.capacity_kg.toFixed(0)} kg
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-2 py-0.5 text-xs uppercase ${statusColor(
                    a.status
                  )}`}
                >
                  {a.status}
                </span>
                {a.status === "dispatched" && (
                  <button
                    onClick={() => handleRecall(a.id)}
                    className="text-xs text-slate-500 hover:underline"
                  >
                    Recall
                  </button>
                )}
              </div>
            </li>
          ))}
          {avs.length === 0 && (
            <li className="rounded-lg border bg-white p-4 text-center text-sm text-slate-500">
              No AVs in the fleet — add one below.
            </li>
          )}
        </ul>

        <h2 className="mb-3 text-sm font-semibold text-slate-600">Add AV</h2>
        <form
          onSubmit={handleAdd}
          className="grid grid-cols-1 gap-2 rounded-xl border bg-white p-4 shadow-sm sm:grid-cols-4"
        >
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Vendor"
            value={form.vendor}
            onChange={(e) => setForm({ ...form, vendor: e.target.value })}
            required
          />
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Model"
            value={form.model}
            onChange={(e) => setForm({ ...form, model: e.target.value })}
            required
          />
          <select
            value={form.autopilot_level}
            onChange={(e) => setForm({ ...form, autopilot_level: e.target.value })}
            className="rounded border px-3 py-2 text-sm"
          >
            <option value="3">Level 3</option>
            <option value="4">Level 4</option>
            <option value="5">Level 5</option>
          </select>
          <input
            type="number"
            className="rounded border px-3 py-2 text-sm"
            placeholder="Capacity kg"
            value={form.capacity_kg}
            onChange={(e) => setForm({ ...form, capacity_kg: e.target.value })}
          />
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white sm:col-span-4"
            style={{ backgroundColor: "#10B981" }}
          >
            Add to fleet
          </button>
        </form>
      </section>
    </main>
  );
}
