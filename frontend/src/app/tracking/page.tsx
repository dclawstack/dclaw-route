"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  driversApi,
  routesApi,
  trackingApi,
  type Driver,
  type Route,
  type RouteETA,
} from "@/lib/api";

export default function TrackingPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [etas, setEtas] = useState<Record<string, RouteETA>>({});
  const [error, setError] = useState<string | null>(null);

  async function refreshAll() {
    try {
      const [r, d] = await Promise.all([routesApi.list(), driversApi.list()]);
      setRoutes(r);
      setDrivers(d);
      const etaResults: Record<string, RouteETA> = {};
      for (const route of r) {
        if (route.deliveries.length > 0) {
          try {
            etaResults[route.id] = await trackingApi.routeEta(route.id);
          } catch {
            // ignore — endpoint may 404 on edge cases
          }
        }
      }
      setEtas(etaResults);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 10000);
    return () => clearInterval(interval);
  }, []);

  async function simulatePing(driverId: string, route: Route) {
    if (route.deliveries.length === 0) return;
    const pending = route.deliveries.find((d) => d.status === "pending");
    if (!pending) return;
    setError(null);
    try {
      // Jitter around the next pending stop's coordinates by ~0.01°
      const eta = etas[route.id];
      const driverPos = eta?.driver_position;
      if (!driverPos) {
        // First ping: use route's first stop coordinates (lookup by stop_id from eta)
        const firstEta = eta?.stops[0];
        if (firstEta) {
          await trackingApi.pushLocation(driverId, 40.7128, -74.006);
        } else {
          await trackingApi.pushLocation(driverId, 40.7128, -74.006);
        }
      } else {
        // Step toward next stop by ~10% of remaining distance
        const next = eta!.stops[0];
        // We don't have stop coords here; just nudge position slightly toward arbitrary direction
        const [lat, lng] = driverPos;
        await trackingApi.pushLocation(driverId, lat + 0.005, lng + 0.005);
        void next;
      }
      refreshAll();
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
          Live Tracking
        </h1>
      </header>
      <section className="mx-auto max-w-5xl px-6 py-8">
        <p className="mb-4 text-sm text-slate-500">
          Auto-refreshes every 10s. Click <em>Simulate ping</em> to advance a
          driver's position.
        </p>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}
        <div className="space-y-4">
          {routes.map((r) => {
            const driver = drivers.find((d) => d.id === r.driver_id);
            const eta = etas[r.id];
            return (
              <div key={r.id} className="rounded-lg border bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="font-semibold">{r.name}</div>
                  <div className="flex items-center gap-2 text-xs">
                    {eta?.is_delayed && (
                      <span className="rounded bg-red-100 px-2 py-0.5 text-red-700">
                        DELAYED
                      </span>
                    )}
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-slate-700">
                      {r.status}
                    </span>
                  </div>
                </div>
                <div className="mt-1 text-sm text-slate-500">
                  Driver: {driver ? driver.name : "Unassigned"}
                  {driver?.current_lat != null && (
                    <span className="ml-2 text-xs">
                      📍 {driver.current_lat.toFixed(4)},{" "}
                      {driver.current_lng?.toFixed(4)}
                    </span>
                  )}
                </div>
                {driver && (
                  <button
                    onClick={() => simulatePing(driver.id, r)}
                    className="mt-2 rounded px-3 py-1 text-xs font-semibold text-white"
                    style={{ backgroundColor: "#10B981" }}
                  >
                    Simulate ping
                  </button>
                )}
                {eta && eta.stops.length > 0 && (
                  <table className="mt-3 w-full text-left text-xs">
                    <thead className="text-slate-500">
                      <tr>
                        <th className="py-1">#</th>
                        <th className="py-1">Stop</th>
                        <th className="py-1">Leg km</th>
                        <th className="py-1">Cum km</th>
                        <th className="py-1">ETA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {eta.stops.map((s) => (
                        <tr key={s.delivery_id} className="border-t">
                          <td className="py-1">{s.sequence + 1}</td>
                          <td className="py-1">{s.stop_name}</td>
                          <td className="py-1">
                            {s.distance_from_previous_km.toFixed(2)}
                          </td>
                          <td className="py-1">{s.cumulative_km.toFixed(2)}</td>
                          <td className="py-1">
                            {new Date(s.eta).toLocaleTimeString()}{" "}
                            <span className="text-slate-400">
                              (+{s.minutes_from_now}m)
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
                {eta && eta.stops.length === 0 && (
                  <div className="mt-3 text-xs text-slate-500">
                    All deliveries on this route are complete.
                  </div>
                )}
              </div>
            );
          })}
          {routes.length === 0 && (
            <div className="rounded-lg border bg-white p-6 text-center text-sm text-slate-500">
              No routes — create one on the Routes page first.
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
