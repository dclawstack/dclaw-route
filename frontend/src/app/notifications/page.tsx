"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  notificationsApi,
  type NotificationEvent,
  type NotificationTemplate,
} from "@/lib/api";

export default function NotificationsPage() {
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [events, setEvents] = useState<NotificationEvent[]>([]);
  const [editing, setEditing] = useState<Record<string, { subject: string; body: string }>>(
    {}
  );
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const [t, e] = await Promise.all([
        notificationsApi.listTemplates(),
        notificationsApi.listEvents(),
      ]);
      setTemplates(t);
      setEvents(e);
    } catch (err) {
      setError(String(err));
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handleSave(tpl: NotificationTemplate) {
    const draft = editing[tpl.id];
    if (!draft) return;
    setError(null);
    try {
      await notificationsApi.updateTemplate(tpl.id, draft);
      const next = { ...editing };
      delete next[tpl.id];
      setEditing(next);
      refresh();
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4">
        <Link href="/" className="text-sm text-slate-500 hover:underline">
          ← Back
        </Link>
        <h1 className="text-xl font-bold" style={{ color: "#10B981" }}>
          Customer Notifications
        </h1>
      </header>
      <section className="mx-auto max-w-4xl px-6 py-8">
        {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

        <h2 className="mb-3 text-sm font-semibold text-slate-600">Templates</h2>
        <p className="mb-3 text-xs text-slate-500">
          Variables: <code>{"{customer_name}"}</code> <code>{"{address}"}</code>{" "}
          <code>{"{route_name}"}</code> <code>{"{driver_name}"}</code>{" "}
          <code>{"{minutes_away}"}</code>
        </p>
        <ul className="mb-8 space-y-3">
          {templates.map((t) => {
            const isEditing = editing[t.id];
            return (
              <li key={t.id} className="rounded-lg border bg-white p-4 shadow-sm">
                <div className="mb-2 flex items-center justify-between">
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-mono">
                    {t.kind}
                  </span>
                  {!isEditing && (
                    <button
                      onClick={() =>
                        setEditing({
                          ...editing,
                          [t.id]: { subject: t.subject, body: t.body },
                        })
                      }
                      className="text-xs text-emerald-700 hover:underline"
                    >
                      Edit
                    </button>
                  )}
                </div>
                {isEditing ? (
                  <div className="space-y-2">
                    <input
                      value={isEditing.subject}
                      onChange={(e) =>
                        setEditing({
                          ...editing,
                          [t.id]: { ...isEditing, subject: e.target.value },
                        })
                      }
                      className="w-full rounded border px-3 py-2 text-sm"
                    />
                    <textarea
                      value={isEditing.body}
                      onChange={(e) =>
                        setEditing({
                          ...editing,
                          [t.id]: { ...isEditing, body: e.target.value },
                        })
                      }
                      rows={3}
                      className="w-full rounded border px-3 py-2 text-sm"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSave(t)}
                        className="rounded px-3 py-1 text-xs font-semibold text-white"
                        style={{ backgroundColor: "#10B981" }}
                      >
                        Save
                      </button>
                      <button
                        onClick={() => {
                          const next = { ...editing };
                          delete next[t.id];
                          setEditing(next);
                        }}
                        className="rounded border px-3 py-1 text-xs"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="font-medium">{t.subject}</div>
                    <div className="mt-1 whitespace-pre-line text-sm text-slate-600">
                      {t.body}
                    </div>
                  </>
                )}
              </li>
            );
          })}
        </ul>

        <h2 className="mb-3 text-sm font-semibold text-slate-600">Recent events</h2>
        <ul className="space-y-2">
          {events.map((e) => (
            <li key={e.id} className="rounded-lg border bg-white p-3 shadow-sm">
              <div className="flex items-center justify-between text-xs">
                <span className="rounded bg-slate-100 px-2 py-0.5 font-mono">
                  {e.kind}
                </span>
                <span className="text-slate-500">
                  {e.channel} → {e.recipient} ·{" "}
                  {new Date(e.sent_at).toLocaleString()}
                </span>
              </div>
              <div className="mt-1 text-sm font-medium">{e.subject}</div>
              <div className="text-sm text-slate-600">{e.body}</div>
            </li>
          ))}
          {events.length === 0 && (
            <li className="rounded-lg border bg-white p-4 text-center text-sm text-slate-500">
              No notifications sent yet. Customers need an email or phone on
              the stop record to receive notifications.
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}
