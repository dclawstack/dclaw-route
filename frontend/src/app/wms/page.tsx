"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  routesApi,
  wmsApi,
  type LoadingManifest,
  type Route,
  type WmsSyncResult,
} from "@/lib/api";

export default function WmsPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [manifest, setManifest] = useState<LoadingManifest | null>(null);
  const [activeRouteId, setActiveRouteId] = useState<string>("");
  const [dockInput, setDockInput] = useState("");
  const [syncResult, setSyncResult] = useState<WmsSyncResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refreshRoutes() {
    try {
      setRoutes(await routesApi.list());
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refreshRoutes();
  }, []);

  async function loadManifest(routeId: string) {
    setActiveRouteId(routeId);
    setManifest(null);
    setError(null);
    try {
      setManifest(await wmsApi.loadingSequence(routeId));
    } catch (e) {
      setError(String(e));
    }
  }

  async function assignDock() {
    if (!activeRouteId || !dockInput) return;
    setError(null);
    try {
      await wmsApi.assignDock(activeRouteId, dockInput);
      setDockInput("");
      await loadManifest(activeRouteId);
      refreshRoutes();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleSync() {
    try {
      setSyncResult(await wmsApi.sync());
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
          Warehouse / WMS
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm text-slate-500">
            LIFO loading order — last stop loaded first (deepest in truck),
            first stop loaded last (closest to door).
          </p>
          <button
            onClick={handleSync}
            className="rounded border px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100"
          >
            Sync DClaw WMS
          </button>
        </div>
        {syncResult && (
          <div className="mb-3 rounded bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
            Synced at {new Date(syncResult.timestamp).toLocaleTimeString()} ·{" "}
            {syncResult.routes_synced} routes · {syncResult.deliveries_synced}{" "}
            deliveries
          </div>
        )}
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-[260px_1fr]">
          <ul className="space-y-2">
            {routes.map((r) => (
              <li key={r.id}>
                <button
                  onClick={() => loadManifest(r.id)}
                  className={`w-full rounded-lg border bg-white p-3 text-left shadow-sm transition hover:shadow-md ${
                    activeRouteId === r.id ? "ring-2 ring-emerald-500" : ""
                  }`}
                >
                  <div className="font-medium">{r.name}</div>
                  <div className="text-xs text-slate-500">
                    {r.deliveries.length} stops
                    {r.dock_number && ` · dock ${r.dock_number}`}
                  </div>
                </button>
              </li>
            ))}
            {routes.length === 0 && (
              <li className="rounded-lg border bg-white p-4 text-sm text-slate-500">
                No routes yet.
              </li>
            )}
          </ul>

          <div className="rounded-lg border bg-white p-4 shadow-sm">
            {!manifest && (
              <p className="text-sm text-slate-500">
                Select a route to view its loading manifest.
              </p>
            )}
            {manifest && (
              <>
                <div className="mb-3 flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-700">
                    {manifest.route_name} ·{" "}
                    {manifest.dock_number
                      ? `Dock ${manifest.dock_number}`
                      : "No dock assigned"}
                  </h2>
                </div>

                <div className="mb-4 flex gap-2">
                  <input
                    value={dockInput}
                    onChange={(e) => setDockInput(e.target.value)}
                    placeholder="Dock number (e.g. D-12)"
                    className="flex-1 rounded border px-3 py-1 text-sm"
                  />
                  <button
                    onClick={assignDock}
                    disabled={!dockInput}
                    className="rounded px-3 py-1 text-xs font-semibold text-white disabled:opacity-50"
                    style={{ backgroundColor: "#10B981" }}
                  >
                    Assign
                  </button>
                </div>

                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-2 py-2">Load #</th>
                      <th className="px-2 py-2">Stop</th>
                      <th className="px-2 py-2 text-right">Drop order</th>
                    </tr>
                  </thead>
                  <tbody>
                    {manifest.items.map((it) => (
                      <tr key={it.delivery_id} className="border-t">
                        <td className="px-2 py-2 font-mono">
                          {it.load_position + 1}
                        </td>
                        <td className="px-2 py-2">{it.stop_name}</td>
                        <td className="px-2 py-2 text-right text-slate-500">
                          #{it.delivery_sequence + 1}
                        </td>
                      </tr>
                    ))}
                    {manifest.items.length === 0 && (
                      <tr>
                        <td
                          colSpan={3}
                          className="px-2 py-4 text-center text-sm text-slate-500"
                        >
                          Empty route.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
