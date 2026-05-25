"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, X, Send, Bot } from "lucide-react";
import { api } from "@/lib/api";

type Role = "user" | "assistant";
interface Msg {
  role: Role;
  content: string;
}
interface SuggestedAction {
  type: "create_stop" | "create_route" | "assign_driver" | "optimize_route" | "none";
  label: string;
  target_path: string | null;
}
interface ChatResponse {
  reply: string;
  suggested_action: SuggestedAction;
  provider: "openrouter" | "stub";
}

export default function RouteCopilot() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [lastAction, setLastAction] = useState<SuggestedAction | null>(null);

  if (pathname === "/") return null;

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || pending) return;
    const userMsg: Msg = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setPending(true);
    try {
      const resp = await api<ChatResponse>("/api/v1/ai/route-chat", {
        method: "POST",
        body: JSON.stringify({ message: userMsg.content, history: messages }),
      });
      setMessages((m) => [...m, { role: "assistant", content: resp.reply }]);
      setLastAction(resp.suggested_action.type === "none" ? null : resp.suggested_action);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error: ${String(err)}` },
      ]);
    } finally {
      setPending(false);
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        aria-label="Open copilot"
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full text-white shadow-lg transition hover:opacity-90"
        style={{ backgroundColor: "#10B981" }}
      >
        <MessageSquare className="h-6 w-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex h-[480px] w-[360px] flex-col rounded-xl border bg-white shadow-2xl">
      <div
        className="flex items-center justify-between rounded-t-xl px-4 py-3 text-white"
        style={{ backgroundColor: "#10B981" }}
      >
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          <span className="font-semibold">Route Copilot</span>
        </div>
        <button onClick={() => setOpen(false)} aria-label="Close copilot">
          <X className="h-5 w-5" />
        </button>
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-3 text-sm">
        {messages.length === 0 && (
          <div className="rounded bg-slate-50 p-3 text-slate-600">
            Ask me to add a stop, plan a route, assign a driver, or optimize an
            existing route.
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`rounded-lg px-3 py-2 ${
              m.role === "user"
                ? "ml-6 bg-emerald-50 text-slate-900"
                : "mr-6 bg-slate-100 text-slate-900"
            }`}
          >
            {m.content}
          </div>
        ))}
        {pending && (
          <div className="mr-6 rounded-lg bg-slate-100 px-3 py-2 italic text-slate-500">
            Thinking…
          </div>
        )}
        {lastAction && lastAction.target_path && (
          <Link
            href={lastAction.target_path}
            onClick={() => setLastAction(null)}
            className="block rounded-lg border border-emerald-300 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-800 hover:bg-emerald-100"
          >
            → {lastAction.label}
          </Link>
        )}
      </div>
      <form onSubmit={handleSend} className="flex gap-2 border-t p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a command…"
          className="flex-1 rounded border px-3 py-2 text-sm outline-none focus:border-emerald-500"
          disabled={pending}
        />
        <button
          type="submit"
          disabled={pending || !input.trim()}
          className="rounded px-3 py-2 text-white disabled:opacity-50"
          style={{ backgroundColor: "#10B981" }}
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
