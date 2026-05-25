"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  vehiclesApi,
  type FleetSyncResult,
  type MaintenanceAlert,
  type Vehicle,
} from "@/lib/api";

export default function VehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [alerts, setAlerts] = useState<MaintenanceAlert[]>([]);
  const [syncResult, setSyncResult] = useState<FleetSyncResult | null>(null);
  const [form, setForm] = useState({
    plate: "",
    vehicle_type: "van",
    capacity_kg: "1000",
    odometer_km: "0",
  });
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [v, a] = await Promise.all([
        vehiclesApi.list(),
        vehiclesApi.maintenanceAlerts(),
      ]);
      setVehicles(v);
      setAlerts(a);
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
      await vehiclesApi.create({
        plate: form.plate,
        vehicle_type: form.vehicle_type,
        capacity_kg: parseFloat(form.capacity_kg),
        odometer_km: parseInt(form.odometer_km),
      });
      setForm({ plate: "", vehicle_type: "van", capacity_kg: "1000", odometer_km: "0" });
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleSync() {
    try {
      setSyncResult(await vehiclesApi.sync());
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  const sevColor = (s: string) =>
    s === "overdue"
      ? "bg-red-100 text-red-800"
      : s === "due_soon"
        ? "bg-amber-100 text-amber-800"
        : "bg-emerald-100 text-emerald-800";

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Fleet
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-600">Maintenance alerts</h2>
          <button
            onClick={handleSync}
            className="rounded border px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100"
          >
            Sync DClaw Fleet
          </button>
        </div>
        {syncResult && (
          <div className="mb-3 rounded bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
            Synced at {new Date(syncResult.timestamp).toLocaleTimeString()} ·{" "}
            pulled {syncResult.pulled} · pushed {syncResult.pushed}
          </div>
        )}
        <div className="mb-8 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {alerts.map((a) => (
            <div
              key={a.vehicle_id}
              className="rounded-lg border bg-white p-3 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="font-mono text-sm font-medium">{a.plate}</div>
                <span
                  className={`rounded px-2 py-0.5 text-xs uppercase ${sevColor(
                    a.severity
                  )}`}
                >
                  {a.severity.replace("_", " ")}
                </span>
              </div>
              <div className="mt-1 text-xs text-slate-500">
                {a.km_since_service} / {a.interval_km} km since last service
              </div>
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-emerald-500"
                  style={{
                    width: `${Math.min(
                      100,
                      (a.km_since_service / a.interval_km) * 100
                    )}%`,
                  }}
                />
              </div>
            </div>
          ))}
          {alerts.length === 0 && (
            <div className="rounded-lg border bg-white p-4 text-sm text-slate-500">
              No vehicles yet — add one below.
            </div>
          )}
        </div>

        <form
          onSubmit={handleCreate}
          className="mb-8 grid grid-cols-1 gap-2 rounded-xl border bg-white p-4 shadow-sm sm:grid-cols-5"
        >
          <input
            className="rounded border px-3 py-2 text-sm sm:col-span-2"
            placeholder="Plate"
            value={form.plate}
            onChange={(e) => setForm({ ...form, plate: e.target.value })}
            required
          />
          <select
            className="rounded border px-3 py-2 text-sm"
            value={form.vehicle_type}
            onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}
          >
            <option value="van">Van</option>
            <option value="truck">Truck</option>
            <option value="bike">Bike</option>
            <option value="car">Car</option>
          </select>
          <input
            type="number"
            className="rounded border px-3 py-2 text-sm"
            placeholder="Capacity kg"
            value={form.capacity_kg}
            onChange={(e) => setForm({ ...form, capacity_kg: e.target.value })}
            required
          />
          <input
            type="number"
            className="rounded border px-3 py-2 text-sm"
            placeholder="Odometer km"
            value={form.odometer_km}
            onChange={(e) => setForm({ ...form, odometer_km: e.target.value })}
          />
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white sm:col-span-5"
            style={{ backgroundColor: "#10B981" }}
          >
            Add vehicle
          </button>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        <ul className="space-y-2">
          {vehicles.map((v) => (
            <li
              key={v.id}
              className="flex items-center justify-between rounded-lg border bg-white p-3 shadow-sm"
            >
              <div>
                <div className="font-mono text-sm font-medium">{v.plate}</div>
                <div className="text-xs text-slate-500">
                  {v.vehicle_type} · {v.capacity_kg.toFixed(0)} kg ·{" "}
                  {v.odometer_km.toLocaleString()} km · {v.status}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
