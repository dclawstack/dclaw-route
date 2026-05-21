"use client";

import dynamic from "next/dynamic";
import Link from "next/link";

const StopsMap = dynamic(() => import("@/components/stops-map"), { ssr: false });

export default function MapPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Map
        </h1>
      </header>
      <section className="mx-auto max-w-5xl px-6 py-8">
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <StopsMap />
        </div>
      </section>
    </main>
  );
}
