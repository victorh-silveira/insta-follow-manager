"use client";

import {
  AuthStatus,
  RelationshipListType,
  SyncResponse,
} from "@/types/relationship";

interface SyncHeaderProps {
  gatewayMode: string;
  authStatus: AuthStatus | null;
  isSyncing: boolean;
  lastSync: SyncResponse | null;
  onSync: () => void;
  onLogout: () => void;
  onSelectTab?: (tab: RelationshipListType) => void;
}

export function SyncHeader({
  gatewayMode,
  authStatus,
  isSyncing,
  lastSync,
  onSync,
  onLogout,
  onSelectTab,
}: SyncHeaderProps) {
  return (
    <header className="relative overflow-hidden rounded-3xl border border-rose-100/80 bg-white/90 p-6 shadow-lg shadow-rose-500/5 backdrop-blur-md">
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500"
      />

      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-fuchsia-600 via-rose-500 to-amber-500 text-white shadow-md shadow-rose-500/25">
            <svg
              className="h-6 w-6"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
              <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
              <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
            </svg>
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="bg-gradient-to-r from-slate-900 via-fuchsia-950 to-rose-900 bg-clip-text text-2xl font-extrabold tracking-tight text-transparent">
                Insta Follow Manager
              </h1>
              <span
                className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                  gatewayMode === "instagrapi"
                    ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200/80"
                    : "bg-amber-50 text-amber-700 ring-1 ring-amber-200/80"
                }`}
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    gatewayMode === "instagrapi"
                      ? "bg-emerald-500"
                      : "bg-amber-500"
                  }`}
                />
                Gateway: {gatewayMode}
              </span>
              {authStatus?.authenticated && authStatus.username && (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-fuchsia-50 px-2.5 py-0.5 text-xs font-semibold text-fuchsia-700 ring-1 ring-fuchsia-200/80">
                  {authStatus.profile_pic_url && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={authStatus.profile_pic_url}
                      alt={authStatus.username}
                      className="h-4 w-4 rounded-full object-cover"
                    />
                  )}
                  @{authStatus.username}
                </span>
              )}
            </div>
            <p className="mt-1.5 text-sm text-slate-600">
              Triagem alfabética (A–Z, 0–9 e Caracteres Especiais) pelo{" "}
              <span className="font-semibold text-fuchsia-700">
                nome de exibição
              </span>{" "}
              com unfollow direto no Instagram.
            </p>
          </div>
        </div>

        {authStatus?.authenticated && (
          <div className="flex shrink-0 items-center gap-2.5">
            <button
              type="button"
              onClick={onSync}
              disabled={isSyncing}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-rose-500/25 transition hover:brightness-105 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
            >
              <svg
                className={`h-4 w-4 ${isSyncing ? "animate-spin" : ""}`}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
                <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
                <path d="M16 16h5v5" />
              </svg>
              {isSyncing ? "Sincronizando..." : "Sincronizar Instagram"}
            </button>
            <button
              type="button"
              onClick={onLogout}
              className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700"
            >
              <svg
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              Sair
            </button>
          </div>
        )}
      </div>

      {lastSync && (
        <div className="mt-5 grid grid-cols-1 gap-3 border-t border-slate-100 pt-4 sm:grid-cols-3">
          <button
            type="button"
            onClick={() => onSelectTab?.("following")}
            className="flex items-center justify-between rounded-2xl border border-indigo-100 bg-indigo-50/60 px-4 py-3 text-left transition hover:border-indigo-200 hover:bg-indigo-50"
          >
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
                Seguindo
              </p>
              <p className="mt-0.5 text-2xl font-extrabold text-indigo-950">
                {lastSync.following_count}
              </p>
            </div>
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </span>
          </button>

          <button
            type="button"
            onClick={() => onSelectTab?.("followers")}
            className="flex items-center justify-between rounded-2xl border border-emerald-100 bg-emerald-50/60 px-4 py-3 text-left transition hover:border-emerald-200 hover:bg-emerald-50"
          >
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
                Seguidores
              </p>
              <p className="mt-0.5 text-2xl font-extrabold text-emerald-950">
                {lastSync.followers_count}
              </p>
            </div>
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600">
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <polyline points="16 11 18 13 22 9" />
              </svg>
            </span>
          </button>

          <button
            type="button"
            onClick={() => onSelectTab?.("non_followers")}
            className="flex items-center justify-between rounded-2xl border border-rose-100 bg-rose-50/70 px-4 py-3 text-left transition hover:border-rose-200 hover:bg-rose-50"
          >
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-rose-600">
                Não seguem de volta
              </p>
              <p className="mt-0.5 text-2xl font-extrabold text-rose-950">
                {lastSync.non_followers_count}
              </p>
            </div>
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-100 text-rose-600">
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <line x1="17" y1="8" x2="22" y2="13" />
                <line x1="22" y1="8" x2="17" y2="13" />
              </svg>
            </span>
          </button>
        </div>
      )}
    </header>
  );
}
