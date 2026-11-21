"use client";

import { ThemeToggle } from "@/components/ThemeToggle";
import { AuthStatus, SyncResponse } from "@/types/relationship";

interface SyncHeaderProps {
  gatewayMode: string;
  authStatus: AuthStatus | null;
  isSyncing: boolean;
  lastSync: SyncResponse | null;
  onSync: () => void;
  onLogout: () => void;
}

export function SyncHeader({
  gatewayMode,
  authStatus,
  isSyncing,
  lastSync,
  onSync,
  onLogout,
}: SyncHeaderProps) {
  return (
    <header className="relative overflow-hidden rounded-3xl border border-rose-200/70 bg-white/95 p-6 shadow-lg shadow-rose-500/5 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/90 dark:shadow-black/30 sm:p-8">
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500"
      />

      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-start gap-5">
          {authStatus?.authenticated && authStatus.profile_pic_url ? (
            <div className="rounded-2xl bg-gradient-to-br from-fuchsia-600 via-rose-500 to-amber-500 p-0.5 shadow-md shadow-rose-500/20">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={authStatus.profile_pic_url}
                alt={authStatus.username ?? "Conta Instagram"}
                className="h-16 w-16 rounded-[14px] bg-white object-cover dark:bg-slate-900"
              />
            </div>
          ) : (
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-fuchsia-600 via-rose-500 to-amber-500 text-white shadow-md shadow-rose-500/25">
              <svg
                className="h-8 w-8"
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
          )}

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="bg-gradient-to-r from-slate-900 via-fuchsia-950 to-rose-900 bg-clip-text text-3xl font-extrabold tracking-tight text-transparent dark:from-white dark:via-fuchsia-200 dark:to-rose-200 sm:text-4xl">
                Insta Follow Manager
              </h1>
              <span
                className={`inline-flex items-center gap-2 rounded-full px-3.5 py-1 text-sm font-semibold ${
                  gatewayMode === "instagrapi"
                    ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200 dark:bg-emerald-950/70 dark:text-emerald-300 dark:ring-emerald-800"
                    : "bg-amber-50 text-amber-700 ring-1 ring-amber-200 dark:bg-amber-950/70 dark:text-amber-300 dark:ring-amber-800"
                }`}
              >
                <span
                  className={`h-2 w-2 rounded-full ${
                    gatewayMode === "instagrapi"
                      ? "bg-emerald-500"
                      : "bg-amber-500"
                  }`}
                />
                Gateway: {gatewayMode}
              </span>
              {authStatus?.authenticated && authStatus.username && (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-fuchsia-50 px-3.5 py-1 text-sm font-bold text-fuchsia-700 ring-1 ring-fuchsia-200 dark:bg-fuchsia-950/70 dark:text-fuchsia-300 dark:ring-fuchsia-800">
                  @{authStatus.username}
                  {authStatus.is_verified && (
                    <span
                      title="Conta verificada"
                      className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-sky-500 text-xs font-bold text-white"
                    >
                      ✓
                    </span>
                  )}
                </span>
              )}
            </div>

            {authStatus?.authenticated && authStatus.biography ? (
              <p className="mt-2 max-w-3xl text-base text-slate-600 dark:text-slate-300">
                {authStatus.biography}
              </p>
            ) : (
              <p className="mt-2 text-base text-slate-600 dark:text-slate-300">
                Dashboard analítico e triagem alfabética (A–Z, 0–9 e Especiais) com gestão direta de seguidores e seguindo.
              </p>
            )}

            {lastSync && (
              <p className="mt-1.5 text-sm font-medium text-emerald-700 dark:text-emerald-400">
                Última sincronização: {lastSync.total_profiles} perfis atualizados ({lastSync.following_count} seguindo, {lastSync.followers_count} seguidores).
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-wrap shrink-0 items-center gap-3">
          <ThemeToggle />
          {authStatus?.authenticated && (
            <>
              <button
                type="button"
                onClick={onSync}
                disabled={isSyncing}
                className="inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500 px-6 py-3 text-base font-semibold text-white shadow-md shadow-rose-500/25 transition hover:brightness-105 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
              >
                <svg
                  className={`h-5 w-5 ${isSyncing ? "animate-spin" : ""}`}
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
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-base font-semibold text-slate-700 transition hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700 dark:border-slate-700 dark:bg-slate-800/90 dark:text-slate-200 dark:hover:border-rose-700 dark:hover:bg-rose-950/60 dark:hover:text-rose-300"
              >
                <svg
                  className="h-5 w-5"
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
            </>
          )}
        </div>
      </div>
    </header>
  );
}
