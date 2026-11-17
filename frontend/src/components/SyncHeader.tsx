"use client";

import { SyncResponse } from "@/types/relationship";

interface SyncHeaderProps {
  gatewayMode: string;
  isSyncing: boolean;
  lastSync: SyncResponse | null;
  onSync: () => void;
}

export function SyncHeader({
  gatewayMode,
  isSyncing,
  lastSync,
  onSync,
}: SyncHeaderProps) {
  return (
    <header className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Insta Follow Manager
          </h1>
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
              gatewayMode === "instagrapi"
                ? "bg-emerald-100 text-emerald-800"
                : "bg-amber-100 text-amber-800"
            }`}
          >
            Gateway: {gatewayMode}
          </span>
        </div>
        <p className="mt-1 text-sm text-slate-600">
          Triagem alfabética (A–Z, 0–9 e Caracteres Especiais) pelo{" "}
          <span className="font-semibold text-slate-800">nome de exibição</span>{" "}
          com unfollow direto no Instagram.
        </p>
        {lastSync && (
          <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">
            <span>Seguindo: {lastSync.following_count}</span>
            <span>•</span>
            <span>Seguidores: {lastSync.followers_count}</span>
            <span>•</span>
            <span>Não seguem de volta: {lastSync.non_followers_count}</span>
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={onSync}
        disabled={isSyncing}
        className="inline-flex shrink-0 items-center justify-center rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSyncing ? "Sincronizando..." : "Sincronizar Instagram"}
      </button>
    </header>
  );
}
