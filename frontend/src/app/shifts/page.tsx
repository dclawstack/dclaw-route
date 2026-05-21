"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  driversApi,
  shiftsApi,
  type Driver,
  type DriverShift,
  type FatigueAlert,
} from "@/lib/api";

export default function ShiftsPage() {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [shifts, setShifts] = useState<DriverShift[]>([]);
  const [alerts, setAlerts] = useState<FatigueAlert[]>([]);
  const [form, setForm] = useState({
    driver_id: "",
    start_at: "",
    end_at: "",
    hours_worked: "8",
  });
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [d, s, a] = await Promise.all([
        driversApi.list(),
        shiftsApi.list(),
        shiftsApi.fatigueAlerts(),
      ]);
      setDrivers(d);
      setShifts(s);
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
      await shiftsApi.create({
        driver_id: form.driver_id,
        start_at: new Date(form.start_at).toISOString(),
        end_at: form.end_at ? new Date(form.end_at).toISOString() : null,
        hours_worked: parseFloat(form.hours_worked),
        status: "scheduled",
      });
      setForm({ driver_id: "", start_at: "", end_at: "", hours_worked: "8" });
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  const sevColor = (s: string) =>
    s === "critical"
      ? "bg-red-100 text-red-800"
      : s === "warning"
        ? "bg-amber-100 text-amber-800"
        : "bg-emerald-100 text-emerald-800";

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Driver Shifts & HOS
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        <h2 className="mb-3 text-sm font-semibold text-slate-600">
          Fatigue alerts (rolling 7-day window, 60 h FMCSA limit)
        </h2>
        <div className="mb-8 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {alerts.map((a) => (
            <div
              key={a.driver_id}
              className="rounded-lg border bg-white p-3 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="font-medium">{a.driver_name}</div>
                <span
                  className={`rounded px-2 py-0.5 text-xs uppercase ${sevColor(
                    a.severity
                  )}`}
                >
                  {a.severity}
                </span>
              </div>
              <div className="mt-1 text-xs text-slate-500">
                {a.hours_last_7_days.toFixed(1)} / {a.limit_hours.toFixed(0)} h ·{" "}
                {a.remaining_hours.toFixed(1)} h remaining
              </div>
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-emerald-500"
                  style={{
                    width: `${Math.min(
                      100,
                      (a.hours_last_7_days / a.limit_hours) * 100
                    )}%`,
                  }}
                />
              </div>
            </div>
          ))}
          {alerts.length === 0 && (
            <div className="rounded-lg border bg-white p-4 text-sm text-slate-500">
              No drivers — add some on the Drivers page.
            </div>
          )}
        </div>

        <form
          onSubmit={handleCreate}
          className="mb-8 grid grid-cols-1 gap-2 rounded-xl border bg-white p-4 shadow-sm sm:grid-cols-5"
        >
          <select
            className="rounded border px-3 py-2 text-sm"
            value={form.driver_id}
            onChange={(e) => setForm({ ...form, driver_id: e.target.value })}
            required
          >
            <option value="">— Driver —</option>
            {drivers.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
          <input
            type="datetime-local"
            className="rounded border px-3 py-2 text-sm"
            value={form.start_at}
            onChange={(e) => setForm({ ...form, start_at: e.target.value })}
            required
          />
          <input
            type="datetime-local"
            className="rounded border px-3 py-2 text-sm"
            value={form.end_at}
            onChange={(e) => setForm({ ...form, end_at: e.target.value })}
          />
          <input
            type="number"
            step="0.25"
            className="rounded border px-3 py-2 text-sm"
            value={form.hours_worked}
            onChange={(e) => setForm({ ...form, hours_worked: e.target.value })}
            placeholder="Hours"
            required
          />
          <button
            type="submit"
            className="rounded px-3 py-2 text-sm font-semibold text-white"
            style={{ backgroundColor: "#10B981" }}
          >
            Schedule
          </button>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        <h2 className="mb-3 text-sm font-semibold text-slate-600">Recent shifts</h2>
        <ul className="space-y-2">
          {shifts.map((s) => {
            const driver = drivers.find((d) => d.id === s.driver_id);
            return (
              <li key={s.id} className="rounded-lg border bg-white p-3 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{driver?.name ?? s.driver_id}</div>
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                    {s.status}
                  </span>
                </div>
                <div className="text-xs text-slate-500">
                  {new Date(s.start_at).toLocaleString()}{" "}
                  {s.end_at && `→ ${new Date(s.end_at).toLocaleTimeString()}`} ·{" "}
                  {s.hours_worked} h
                </div>
              </li>
            );
          })}
          {shifts.length === 0 && (
            <li className="rounded-lg border bg-white p-4 text-center text-sm text-slate-500">
              No shifts logged yet.
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}
