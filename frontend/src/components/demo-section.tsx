"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Database, Eraser, Sparkles, ArrowRight } from "lucide-react";
import { ApiError, demoApi, type DemoStatus } from "@/lib/api";

export default function DemoSection() {
  const [status, setStatus] = useState<DemoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setStatus(await demoApi.status());
      setError(null);
    } catch (e) {
      setStatus({
        enabled: false,
        seeded: false,
        stop_count: 0,
        driver_count: 0,
        vehicle_count: 0,
        route_count: 0,
      });
      setError(
        e instanceof ApiError
          ? e.message
          : `Cannot reach the API at ${process.env.NEXT_PUBLIC_API_URL || "(unset)"}. ${String(e)}`
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleSeed() {
    setSeeding(true);
    setError(null);
    try {
      setStatus(await demoApi.seed());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setSeeding(false);
    }
  }

  async function handleReset() {
    setResetting(true);
    setError(null);
    try {
      setStatus(await demoApi.reset());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setResetting(false);
    }
  }

  const isSeeded = !!status?.seeded && status.stop_count > 0;
  const backendReachable = !loading && status !== null && !error;
  const backendDisabled = !loading && status !== null && !status.enabled && !error;

  return (
    <section id="demo" className="bg-emerald-50/40 py-20">
      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-widest text-emerald-700">
            Try it
          </div>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Spin up a demo dataset.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-slate-600">
            One click loads 8 stops, 3 drivers, 3 vehicles, and 2 ready-to-run
            routes around New York City. One click takes it all away.
          </p>
        </div>

        <div className="mt-10 mx-auto max-w-3xl rounded-2xl border bg-white p-6 shadow-sm sm:p-8">
          <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
                <Database className="h-5 w-5" />
              </div>
              <div>
                <div className="font-semibold">Demo dataset</div>
                <div className="text-sm text-slate-500">
                  {loading
                    ? "Checking backend…"
                    : !status
                      ? ""
                      : isSeeded
                        ? `${status.stop_count} stops · ${status.driver_count} drivers · ${status.vehicle_count} vehicles · ${status.route_count} routes`
                        : "Not loaded yet"}
                </div>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {backendReachable && !isSeeded && (
                <button
                  onClick={handleSeed}
                  disabled={seeding}
                  className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
                  style={{ backgroundColor: "#10B981" }}
                >
                  <Sparkles className="h-4 w-4" />
                  {seeding ? "Seeding…" : "Seed demo data"}
                </button>
              )}
              {backendReachable && isSeeded && (
                <>
                  <Link
                    href="/dashboard"
                    className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90"
                    style={{ backgroundColor: "#10B981" }}
                  >
                    Open dashboard <ArrowRight className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={handleReset}
                    disabled={resetting}
                    className="inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                  >
                    <Eraser className="h-4 w-4" />
                    {resetting ? "Clearing…" : "Clear demo data"}
                  </button>
                </>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
              Backend not reachable yet. Start it with{" "}
              <code className="font-mono">docker compose up</code> or run the
              FastAPI app on <code className="font-mono">localhost:18163</code>,
              then refresh. <span className="block mt-1 text-xs text-amber-700">{error}</span>
            </div>
          )}

          {backendDisabled && (
            <div className="mt-4 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700">
              Demo mode is disabled on this deployment (set{" "}
              <code className="font-mono">ENABLE_DEMO_MODE=true</code> to turn it on).
            </div>
          )}

          {backendReachable && isSeeded && (
            <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Stat label="Stops" value={status!.stop_count} />
              <Stat label="Drivers" value={status!.driver_count} />
              <Stat label="Vehicles" value={status!.vehicle_count} />
              <Stat label="Routes" value={status!.route_count} />
            </div>
          )}
        </div>

        <p className="mt-6 text-center text-xs text-slate-500">
          Demo rows are prefixed <code className="font-mono">DEMO </code>;
          clearing only removes those rows.
        </p>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3 text-center">
      <div className="text-2xl font-bold text-slate-900">{value}</div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  );
}
