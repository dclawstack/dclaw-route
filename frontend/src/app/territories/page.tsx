"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  stopsApi,
  territoriesApi,
  type ClusterResult,
  type Stop,
  type Territory,
} from "@/lib/api";

export default function TerritoriesPage() {
  const [stops, setStops] = useState<Stop[]>([]);
  const [territories, setTerritories] = useState<Territory[]>([]);
  const [n, setN] = useState("3");
  const [result, setResult] = useState<ClusterResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      const [s, t] = await Promise.all([stopsApi.list(), territoriesApi.list()]);
      setStops(s);
      setTerritories(t);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleCluster(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      setResult(await territoriesApi.cluster(parseInt(n)));
      refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  const territoryById = new Map(territories.map((t) => [t.id, t]));

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Territories
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        <form
          onSubmit={handleCluster}
          className="mb-8 flex items-center gap-2 rounded-xl border bg-white p-4 shadow-sm"
        >
          <label className="text-sm font-medium text-slate-700">
            Number of territories:
          </label>
          <input
            type="number"
            min={1}
            max={20}
            value={n}
            onChange={(e) => setN(e.target.value)}
            className="w-20 rounded border px-3 py-2 text-sm"
          />
          <button
            type="submit"
            disabled={busy}
            className="rounded px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
            style={{ backgroundColor: "#10B981" }}
          >
            {busy ? "Clustering…" : "Cluster stops"}
          </button>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        {result && (
          <div className="mb-6 rounded bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
            Assigned {result.assigned_stops} stops to {result.territories.length}{" "}
            territories ({result.iterations} k-means iterations).
          </div>
        )}

        <h2 className="mb-3 text-sm font-semibold text-slate-600">Territory summary</h2>
        <div className="mb-8 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {territories.map((t) => {
            const summary = result?.territories.find((a) => a.territory_id === t.id);
            return (
              <div key={t.id} className="rounded-lg border bg-white p-3 shadow-sm">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block h-3 w-3 rounded-full"
                    style={{ backgroundColor: t.color }}
                  />
                  <div className="font-medium">{t.name}</div>
                </div>
                {summary && (
                  <div className="mt-1 text-xs text-slate-500">
                    {summary.stop_count} stops · center {summary.center_lat.toFixed(3)},{" "}
                    {summary.center_lng.toFixed(3)}
                  </div>
                )}
              </div>
            );
          })}
          {territories.length === 0 && (
            <div className="rounded-lg border bg-white p-4 text-sm text-slate-500">
              No territories yet. Add some stops then cluster.
            </div>
          )}
        </div>

        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Stop assignments
        </h2>
        <ul className="space-y-1">
          {stops.map((s) => {
            const t = s.territory_id ? territoryById.get(s.territory_id) : null;
            return (
              <li
                key={s.id}
                className="flex items-center justify-between rounded-lg border bg-white p-2 shadow-sm"
              >
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block h-3 w-3 rounded-full"
                    style={{ backgroundColor: t?.color ?? "#cbd5e1" }}
                  />
                  <span className="text-sm">{s.name}</span>
                </div>
                <span className="text-xs text-slate-500">
                  {t?.name ?? "Unassigned"}
                </span>
              </li>
            );
          })}
        </ul>
      </section>
    </main>
  );
}
