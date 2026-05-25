"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  returnsApi,
  stopsApi,
  type ConsolidationResult,
  type ReturnPickup,
  type Stop,
} from "@/lib/api";

export default function ReturnsPage() {
  const [stops, setStops] = useState<Stop[]>([]);
  const [pending, setPending] = useState<ReturnPickup[]>([]);
  const [stopId, setStopId] = useState("");
  const [notes, setNotes] = useState("");
  const [result, setResult] = useState<ConsolidationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [s, p] = await Promise.all([stopsApi.list(), returnsApi.listPending()]);
      setStops(s);
      setPending(p);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleRequest(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await returnsApi.request(stopId, notes || undefined);
      setStopId("");
      setNotes("");
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleConsolidate() {
    setError(null);
    try {
      setResult(await returnsApi.consolidate());
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
          Returns / Reverse Logistics
        </h1>
      </header>
      <section className="mx-auto max-w-3xl px-6 py-8">
        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Request a pickup
        </h2>
        <form
          onSubmit={handleRequest}
          className="mb-8 grid grid-cols-1 gap-2 rounded-xl border bg-white p-4 shadow-sm sm:grid-cols-3"
        >
          <select
            className="rounded border px-3 py-2 text-sm sm:col-span-1"
            value={stopId}
            onChange={(e) => setStopId(e.target.value)}
            required
          >
            <option value="">— Stop —</option>
            {stops.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
          <input
            className="rounded border px-3 py-2 text-sm sm:col-span-2"
            placeholder="Reason / notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white sm:col-span-3"
            style={{ backgroundColor: "#10B981" }}
          >
            Queue return pickup
          </button>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-600">
            Pending pickup queue ({pending.length})
          </h2>
          <button
            disabled={pending.length < 2}
            onClick={handleConsolidate}
            className="rounded border px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-50"
          >
            Consolidate into route
          </button>
        </div>
        {result && (
          <div className="mb-4 rounded bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
            Consolidated {result.consolidated_count} pickups into{" "}
            <strong>{result.route_name}</strong> · {result.total_distance_km.toFixed(2)} km
            · ~{result.estimated_minutes} min
          </div>
        )}
        <ul className="space-y-2">
          {pending.map((p) => {
            const stop = stops.find((s) => s.id === p.stop_id);
            return (
              <li key={p.id} className="rounded-lg border bg-white p-3 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{stop?.name ?? p.stop_id}</div>
                  <span className="rounded bg-amber-100 px-2 py-0.5 text-xs uppercase text-amber-800">
                    pickup
                  </span>
                </div>
                <div className="text-xs text-slate-500">
                  {stop?.address}
                  {p.notes && ` · ${p.notes}`}
                </div>
              </li>
            );
          })}
          {pending.length === 0 && (
            <li className="rounded-lg border bg-white p-4 text-center text-sm text-slate-500">
              No pending pickups.
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}
