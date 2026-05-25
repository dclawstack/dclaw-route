"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  predictiveApi,
  routesApi,
  type Route,
  type RouteForecast,
  type WeatherState,
} from "@/lib/api";

export default function ForecastPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [forecasts, setForecasts] = useState<Record<string, RouteForecast>>({});
  const [weather, setWeather] = useState<WeatherState>({ factor: 1.0 });
  const [weatherInput, setWeatherInput] = useState("1.0");
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [r, w] = await Promise.all([routesApi.list(), predictiveApi.weather()]);
      setRoutes(r);
      setWeather(w);
      setWeatherInput(String(w.factor));
      const map: Record<string, RouteForecast> = {};
      for (const route of r) {
        try {
          map[route.id] = await predictiveApi.routeForecast(route.id);
        } catch {
          /* ignore */
        }
      }
      setForecasts(map);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSetWeather(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await predictiveApi.setWeather(parseFloat(weatherInput));
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
          Predictive forecast
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        <p className="mb-4 text-sm text-slate-500">
          Adjusts route ETA with hour-of-day traffic patterns and a weather
          factor.
        </p>

        <form
          onSubmit={handleSetWeather}
          className="mb-6 flex items-center gap-2 rounded-xl border bg-white p-4 shadow-sm"
        >
          <label className="text-sm font-medium text-slate-700">
            Weather factor:
          </label>
          <input
            type="number"
            step="0.05"
            min="0.1"
            max="3"
            value={weatherInput}
            onChange={(e) => setWeatherInput(e.target.value)}
            className="w-24 rounded border px-3 py-2 text-sm"
          />
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            Update
          </button>
          <span className="ml-2 text-xs text-slate-500">
            Current: {weather.factor.toFixed(2)} (1.0 = clear; &gt;1 = adverse)
          </span>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        {routes.length === 0 ? (
          <div className="rounded-lg border bg-white p-6 text-center text-sm text-slate-500">
            No routes yet.
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Route</th>
                  <th className="px-3 py-2 text-right">Hour</th>
                  <th className="px-3 py-2 text-right">Traffic</th>
                  <th className="px-3 py-2 text-right">Weather</th>
                  <th className="px-3 py-2 text-right">Combined</th>
                  <th className="px-3 py-2 text-right">Baseline</th>
                  <th className="px-3 py-2 text-right">Adjusted</th>
                </tr>
              </thead>
              <tbody>
                {routes.map((r) => {
                  const f = forecasts[r.id];
                  return (
                    <tr key={r.id} className="border-t">
                      <td className="px-3 py-2 font-medium">{r.name}</td>
                      {f ? (
                        <>
                          <td className="px-3 py-2 text-right">{f.hour}:00</td>
                          <td className="px-3 py-2 text-right">{f.traffic_factor}×</td>
                          <td className="px-3 py-2 text-right">{f.weather_factor}×</td>
                          <td className="px-3 py-2 text-right font-semibold">
                            {f.combined_factor}×
                          </td>
                          <td className="px-3 py-2 text-right">
                            {f.baseline_minutes} min
                          </td>
                          <td className="px-3 py-2 text-right text-amber-700">
                            {f.adjusted_minutes} min
                          </td>
                        </>
                      ) : (
                        <td colSpan={6} className="px-3 py-2 text-right text-slate-400">
                          —
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
