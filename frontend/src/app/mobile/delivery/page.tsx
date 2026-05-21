"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  deliveriesApi,
  proofApi,
  routesApi,
  stopsApi,
  type Delivery,
  type Route,
  type Stop,
} from "@/lib/api";
import SignaturePad from "@/components/signature-pad";

interface DeliveryRow {
  delivery: Delivery;
  route: Route;
  stop: Stop | undefined;
}

export default function MobileDeliveryPage() {
  const [rows, setRows] = useState<DeliveryRow[]>([]);
  const [active, setActive] = useState<DeliveryRow | null>(null);
  const [photo, setPhoto] = useState<string | null>(null);
  const [signature, setSignature] = useState<string | null>(null);
  const [barcode, setBarcode] = useState("");
  const [notes, setNotes] = useState("");
  const [geotag, setGeotag] = useState<[number, number] | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  async function refresh() {
    const [routes, stops] = await Promise.all([routesApi.list(), stopsApi.list()]);
    const all = await deliveriesApi.list();
    const stopMap = new Map(stops.map((s) => [s.id, s]));
    const routeMap = new Map(routes.map((r) => [r.id, r]));
    const pending = all
      .filter((d) => d.status === "pending")
      .map((d) => ({
        delivery: d,
        route: routeMap.get(d.route_id)!,
        stop: stopMap.get(d.stop_id),
      }))
      .filter((row) => row.route);
    setRows(pending);
  }

  useEffect(() => {
    refresh();
  }, []);

  function startCapture(row: DeliveryRow) {
    setActive(row);
    setPhoto(null);
    setSignature(null);
    setBarcode("");
    setNotes("");
    setGeotag(null);
    setResult(null);
    if (typeof navigator !== "undefined" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setGeotag([pos.coords.latitude, pos.coords.longitude]),
        () => {},
        { enableHighAccuracy: false, timeout: 3000 }
      );
    }
  }

  function handlePhoto(file: File | null | undefined) {
    if (!file) {
      setPhoto(null);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => setPhoto(String(reader.result));
    reader.readAsDataURL(file);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!active) return;
    if (!photo && !signature && !barcode) {
      setResult("Need at least one of: photo, signature, or barcode.");
      return;
    }
    setSubmitting(true);
    setResult(null);
    try {
      const proof = await proofApi.complete(active.delivery.id, {
        photo_b64: photo,
        signature_b64: signature,
        barcode: barcode || null,
        geotag_lat: geotag?.[0] ?? null,
        geotag_lng: geotag?.[1] ?? null,
        notes: notes || null,
      });
      setResult(
        `Completed at ${new Date(proof.completed_at!).toLocaleTimeString()}` +
          (proof.photo_validated === true
            ? " · photo validated"
            : proof.photo_validated === false
              ? " · photo flagged"
              : "")
      );
      setActive(null);
      refresh();
    } catch (err) {
      setResult(String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-4 py-3">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-lg font-bold" style={{ color: "#10B981" }}>
          Mobile · Proof of Delivery
        </h1>
      </header>

      <section className="mx-auto max-w-md px-4 py-4">
        {!active && (
          <>
            <h2 className="mb-3 text-sm font-semibold text-slate-600">
              Pending deliveries
            </h2>
            {result && (
              <div className="mb-3 rounded bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                {result}
              </div>
            )}
            <ul className="space-y-2">
              {rows.map((row) => (
                <li key={row.delivery.id} className="rounded-lg border bg-white p-3 shadow-sm">
                  <div className="text-sm font-medium">
                    {row.stop?.name ?? "Unknown stop"}
                  </div>
                  <div className="text-xs text-slate-500">
                    {row.stop?.address} · Route: {row.route.name}
                  </div>
                  <button
                    onClick={() => startCapture(row)}
                    className="mt-2 rounded px-3 py-1 text-xs font-semibold text-white"
                    style={{ backgroundColor: "#10B981" }}
                  >
                    Capture proof
                  </button>
                </li>
              ))}
              {rows.length === 0 && (
                <li className="rounded-lg border bg-white p-6 text-center text-sm text-slate-500">
                  No pending deliveries.
                </li>
              )}
            </ul>
          </>
        )}

        {active && (
          <form
            onSubmit={handleSubmit}
            className="space-y-4 rounded-lg border bg-white p-4 shadow-sm"
          >
            <div>
              <div className="text-sm font-semibold">{active.stop?.name}</div>
              <div className="text-xs text-slate-500">{active.stop?.address}</div>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Photo</label>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={(e) => handlePhoto(e.target.files?.[0])}
                className="text-sm"
              />
              {photo && (
                <img src={photo} alt="proof" className="mt-2 max-h-40 rounded border" />
              )}
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">
                Signature
              </label>
              <SignaturePad onChange={setSignature} />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">
                Barcode
              </label>
              <input
                value={barcode}
                onChange={(e) => setBarcode(e.target.value)}
                placeholder="Scan or type"
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                className="w-full rounded border px-3 py-2 text-sm"
              />
            </div>

            {geotag && (
              <div className="text-xs text-slate-500">
                📍 Geotag captured: {geotag[0].toFixed(4)}, {geotag[1].toFixed(4)}
              </div>
            )}

            {result && <div className="text-sm text-red-600">{result}</div>}

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={submitting}
                className="flex-1 rounded px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                style={{ backgroundColor: "#10B981" }}
              >
                {submitting ? "Submitting…" : "Submit proof"}
              </button>
              <button
                type="button"
                onClick={() => setActive(null)}
                className="rounded border px-4 py-2 text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </section>
    </main>
  );
}
