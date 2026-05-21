"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { driversApi, type Driver } from "@/lib/api";

export default function DriversPage() {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [form, setForm] = useState({ name: "", email: "", vehicle_type: "van" });
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      setDrivers(await driversApi.list());
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
      await driversApi.create(form);
      setForm({ name: "", email: "", vehicle_type: "van" });
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleDelete(id: string) {
    await driversApi.remove(id);
    refresh();
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Drivers
        </h1>
      </header>
      <section className="mx-auto max-w-3xl px-6 py-8">
        <form
          onSubmit={handleCreate}
          className="mb-8 grid grid-cols-1 gap-3 rounded-xl border bg-white p-6 shadow-sm sm:grid-cols-3"
        >
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
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
          <button
            type="submit"
            className="col-span-1 rounded px-4 py-2 text-sm font-semibold text-white sm:col-span-3"
            style={{ backgroundColor: "#10B981" }}
          >
            Add driver
          </button>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}
        <ul className="space-y-2">
          {drivers.map((d) => (
            <li
              key={d.id}
              className="flex items-center justify-between rounded-lg border bg-white p-4 shadow-sm"
            >
              <div>
                <div className="font-medium">{d.name}</div>
                <div className="text-sm text-slate-500">{d.email}</div>
                <div className="text-xs text-slate-400">
                  {d.vehicle_type} · {d.status}
                </div>
              </div>
              <button
                onClick={() => handleDelete(d.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Delete
              </button>
            </li>
          ))}
          {drivers.length === 0 && (
            <li className="rounded-lg border bg-white p-6 text-center text-sm text-slate-500">
              No drivers yet — add one above.
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}
