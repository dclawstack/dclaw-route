"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  analyticsApi,
  type FleetSummary,
  type RoutePnL,
} from "@/lib/api";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<FleetSummary | null>(null);
  const [routes, setRoutes] = useState<RoutePnL[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [s, r] = await Promise.all([
        analyticsApi.summary(),
        analyticsApi.routes(),
      ]);
      setSummary(s);
      setRoutes(r);
    } catch (e) {
      setError(String(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Analytics
        </h1>
      </header>
      <section className="mx-auto max-w-5xl px-6 py-8">
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        {summary && (
          <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-5">
            <Tile label="Routes" value={summary.route_count.toString()} />
            <Tile
              label="Total km"
              value={summary.total_distance_km.toFixed(0)}
            />
            <Tile
              label="Total cost"
              value={`$${summary.total_cost_usd.toFixed(0)}`}
            />
            <Tile
              label="Avg cost/delivery"
              value={`$${summary.avg_cost_per_delivery.toFixed(2)}`}
            />
            <Tile
              label="On-time rate"
              value={`${summary.avg_on_time_rate_pct.toFixed(0)}%`}
            />
          </div>
        )}

        {summary && (
          <div className="mb-6 rounded bg-slate-50 px-3 py-2 text-xs text-slate-600">
            Cost model: fuel ${summary.rates.fuel_per_km_usd}/km · labor $
            {summary.rates.labor_per_hour_usd}/hr · vehicle $
            {summary.rates.vehicle_per_km_usd}/km
          </div>
        )}

        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Per-route P&L
        </h2>
        <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Route</th>
                <th className="px-3 py-2 text-right">km</th>
                <th className="px-3 py-2 text-right">Stops</th>
                <th className="px-3 py-2 text-right">Done</th>
                <th className="px-3 py-2 text-right">On-time</th>
                <th className="px-3 py-2 text-right">Fuel</th>
                <th className="px-3 py-2 text-right">Labor</th>
                <th className="px-3 py-2 text-right">Vehicle</th>
                <th className="px-3 py-2 text-right">Total</th>
                <th className="px-3 py-2 text-right">$/stop</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((r) => (
                <tr key={r.route_id} className="border-t">
                  <td className="px-3 py-2 font-medium">{r.route_name}</td>
                  <td className="px-3 py-2 text-right">
                    {r.total_distance_km.toFixed(1)}
                  </td>
                  <td className="px-3 py-2 text-right">{r.stop_count}</td>
                  <td className="px-3 py-2 text-right">{r.completed_count}</td>
                  <td className="px-3 py-2 text-right">
                    {r.on_time_rate_pct.toFixed(0)}%
                  </td>
                  <td className="px-3 py-2 text-right">
                    ${r.fuel_cost_usd.toFixed(2)}
                  </td>
                  <td className="px-3 py-2 text-right">
                    ${r.labor_cost_usd.toFixed(2)}
                  </td>
                  <td className="px-3 py-2 text-right">
                    ${r.vehicle_cost_usd.toFixed(2)}
                  </td>
                  <td className="px-3 py-2 text-right font-semibold">
                    ${r.total_cost_usd.toFixed(2)}
                  </td>
                  <td className="px-3 py-2 text-right">
                    ${r.cost_per_delivery.toFixed(2)}
                  </td>
                </tr>
              ))}
              {routes.length === 0 && (
                <tr>
                  <td
                    colSpan={10}
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
