"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { stopsApi, type Stop } from "@/lib/api";

export default function StopsPage() {
  const [stops, setStops] = useState<Stop[]>([]);
  const [form, setForm] = useState({ name: "", address: "", lat: "", lng: "" });
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      setStops(await stopsApi.list());
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
      await stopsApi.create({
        name: form.name,
        address: form.address,
        lat: parseFloat(form.lat),
        lng: parseFloat(form.lng),
        notes: null,
      });
      setForm({ name: "", address: "", lat: "", lng: "" });
      refresh();
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleDelete(id: string) {
    await stopsApi.remove(id);
    refresh();
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Stops
        </h1>
      </header>
      <section className="mx-auto max-w-3xl px-6 py-8">
        <form
          onSubmit={handleCreate}
          className="mb-8 grid grid-cols-1 gap-3 rounded-xl border bg-white p-6 shadow-sm sm:grid-cols-4"
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
            placeholder="Address"
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
            required
          />
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Lat"
            type="number"
            step="any"
            value={form.lat}
            onChange={(e) => setForm({ ...form, lat: e.target.value })}
            required
          />
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Lng"
            type="number"
            step="any"
            value={form.lng}
            onChange={(e) => setForm({ ...form, lng: e.target.value })}
            required
          />
          <button
            type="submit"
            className="col-span-1 rounded px-4 py-2 text-sm font-semibold text-white sm:col-span-4"
            style={{ backgroundColor: "#10B981" }}
          >
            Add stop
          </button>
        </form>
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}
        <ul className="space-y-2">
          {stops.map((s) => (
            <li
              key={s.id}
              className="flex items-center justify-between rounded-lg border bg-white p-4 shadow-sm"
            >
              <div>
                <div className="font-medium">{s.name}</div>
                <div className="text-sm text-slate-500">{s.address}</div>
                <div className="text-xs text-slate-400">
                  {s.lat.toFixed(4)}, {s.lng.toFixed(4)}
                </div>
              </div>
              <button
                onClick={() => handleDelete(s.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Delete
              </button>
            </li>
          ))}
          {stops.length === 0 && (
            <li className="rounded-lg border bg-white p-6 text-center text-sm text-slate-500">
              No stops yet — add one above.
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}
