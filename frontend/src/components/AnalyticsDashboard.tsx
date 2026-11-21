"use client";

import {
  AuthStatus,
  RelationshipAnalytics,
  RelationshipListType,
} from "@/types/relationship";

interface AnalyticsDashboardProps {
  analytics: RelationshipAnalytics | null;
  authStatus: AuthStatus | null;
  isLoading: boolean;
  onSelectTab: (tab: RelationshipListType) => void;
  onSelectBucket: (bucket: string) => void;
}

export function AnalyticsDashboard({
  analytics,
  authStatus,
  isLoading,
  onSelectTab,
  onSelectBucket,
}: AnalyticsDashboardProps) {
  if (isLoading && !analytics) {
    return (
      <section aria-label="Carregando painel analítico" className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, idx) => (
          <div
            key={idx}
            className="h-36 animate-pulse rounded-3xl border border-slate-200/80 bg-white/80 dark:border-slate-800 dark:bg-slate-900/70"
          />
        ))}
      </section>
    );
  }

  if (!analytics) {
    return null;
  }

  const totalNetwork = Math.max(analytics.total_cached, 1);
  const mutualPct = Math.round((analytics.mutual_count / totalNetwork) * 100);
  const nonFollowersPct = Math.round((analytics.non_followers_count / totalNetwork) * 100);
  const fansPct = Math.max(0, 100 - mutualPct - nonFollowersPct);
  const maxBucketCount = Math.max(...analytics.top_buckets.map((b) => b.count), 1);

  return (
    <section aria-label="Dashboard analítico do Instagram" className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <button
          type="button"
          onClick={() => onSelectTab("following")}
          className="group flex flex-col justify-between rounded-3xl border border-indigo-200/80 bg-white/95 p-6 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-400 hover:shadow-lg hover:shadow-indigo-500/10 dark:border-indigo-900/60 dark:bg-slate-900/90 dark:hover:border-indigo-500/70"
        >
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-300">
              Seguindo
            </span>
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
              <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </span>
          </div>
          <div className="mt-4">
            <p className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              {analytics.following_count}
            </p>
            <p className="mt-1.5 text-sm font-medium text-slate-600 dark:text-slate-400">
              {analytics.verified_following_count} verificados seguidos
            </p>
          </div>
        </button>

        <button
          type="button"
          onClick={() => onSelectTab("followers")}
          className="group flex flex-col justify-between rounded-3xl border border-emerald-200/80 bg-white/95 p-6 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-400 hover:shadow-lg hover:shadow-emerald-500/10 dark:border-emerald-900/60 dark:bg-slate-900/90 dark:hover:border-emerald-500/70"
        >
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">
              Seguidores
            </span>
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
              <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <polyline points="16 11 18 13 22 9" />
              </svg>
            </span>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-3">
              <p className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                {analytics.followers_count}
              </p>
              <span className="rounded-full bg-emerald-100 px-3 py-0.5 text-sm font-bold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                {analytics.follower_following_ratio.toFixed(2)}x ratio
              </span>
            </div>
            <p className="mt-1.5 text-sm font-medium text-slate-600 dark:text-slate-400">
              {analytics.verified_followers_count} verificados te seguem
            </p>
          </div>
        </button>

        <div className="flex flex-col justify-between rounded-3xl border border-fuchsia-200/80 bg-white/95 p-6 shadow-sm dark:border-fuchsia-900/60 dark:bg-slate-900/90">
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm font-bold uppercase tracking-wider text-fuchsia-700 dark:text-fuchsia-300">
              Conexões Mútuas
            </span>
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-fuchsia-100 text-fuchsia-700 dark:bg-fuchsia-950 dark:text-fuchsia-300">
              <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M17 2l4 4-4 4" />
                <path d="M3 11v-1a4 4 0 0 1 4-4h14" />
                <path d="M7 22l-4-4 4-4" />
                <path d="M21 13v1a4 4 0 0 1-4 4H3" />
              </svg>
            </span>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-3">
              <p className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                {analytics.mutual_count}
              </p>
              <span className="rounded-full bg-fuchsia-100 px-3 py-0.5 text-sm font-bold text-fuchsia-800 dark:bg-fuchsia-950 dark:text-fuchsia-300">
                {analytics.follow_back_rate.toFixed(1)}% retorno
              </span>
            </div>
            <p className="mt-1.5 text-sm font-medium text-slate-600 dark:text-slate-400">
              Taxa de reciprocidade na sua rede
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => onSelectTab("non_followers")}
          className="group flex flex-col justify-between rounded-3xl border border-rose-200/80 bg-white/95 p-6 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-rose-400 hover:shadow-lg hover:shadow-rose-500/10 dark:border-rose-900/60 dark:bg-slate-900/90 dark:hover:border-rose-500/70"
        >
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm font-bold uppercase tracking-wider text-rose-700 dark:text-rose-300">
              Não seguem de volta
            </span>
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
              <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <line x1="17" y1="8" x2="22" y2="13" />
                <line x1="22" y1="8" x2="17" y2="13" />
              </svg>
            </span>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-3">
              <p className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                {analytics.non_followers_count}
              </p>
              <span className="rounded-full bg-amber-100 px-3 py-0.5 text-sm font-bold text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                {analytics.not_following_back_count} fãs
              </span>
            </div>
            <p className="mt-1.5 text-sm font-medium text-slate-600 dark:text-slate-400">
              Clique para revisar e dar unfollow
            </p>
          </div>
        </button>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-12">
        <div className="flex flex-col justify-between rounded-3xl border border-slate-200/90 bg-white/95 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/90 lg:col-span-6">
          <div>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                Saúde e Composição da Rede
              </h2>
              <span className="rounded-full bg-slate-100 px-3.5 py-1 text-sm font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                {analytics.total_cached} perfis únicos
              </span>
            </div>

            <div className="mt-5 h-4 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div className="flex h-full w-full">
                <div
                  style={{ width: `${mutualPct}%` }}
                  title={`Mútuos: ${analytics.mutual_count}`}
                  className="bg-emerald-500 transition-all duration-500"
                />
                <div
                  style={{ width: `${nonFollowersPct}%` }}
                  title={`Não seguem de volta: ${analytics.non_followers_count}`}
                  className="bg-rose-500 transition-all duration-500"
                />
                <div
                  style={{ width: `${fansPct}%` }}
                  title={`Não sigo de volta: ${analytics.not_following_back_count}`}
                  className="bg-amber-500 transition-all duration-500"
                />
              </div>
            </div>

            <div className="mt-4 flex flex-wrap gap-5 text-sm font-semibold">
              <span className="inline-flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <span className="h-3 w-3 rounded-full bg-emerald-500" />
                Mútuos ({mutualPct}%)
              </span>
              <span className="inline-flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <span className="h-3 w-3 rounded-full bg-rose-500" />
                Não te seguem ({nonFollowersPct}%)
              </span>
              <span className="inline-flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <span className="h-3 w-3 rounded-full bg-amber-500" />
                Você não segue ({fansPct}%)
              </span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 border-t border-slate-100 pt-5 dark:border-slate-800 sm:grid-cols-3">
            <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Publicações
              </p>
              <p className="mt-1 text-2xl font-extrabold text-slate-900 dark:text-white">
                {authStatus?.media_count ?? "—"}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Sem nome
              </p>
              <p className="mt-1 text-2xl font-extrabold text-slate-900 dark:text-white">
                {analytics.nameless_profiles_count}
              </p>
            </div>
            <div className="col-span-2 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70 sm:col-span-1">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Privacidade
              </p>
              <p className="mt-1 text-2xl font-extrabold text-slate-900 dark:text-white">
                {authStatus?.is_private === true
                  ? "Privada"
                  : authStatus?.is_private === false
                    ? "Pública"
                    : "—"}
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200/90 bg-white/95 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/90 lg:col-span-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Maiores Grupos Alfabéticos
            </h2>
            <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Clique em uma barra para filtrar
            </span>
          </div>

          {analytics.top_buckets.length === 0 ? (
            <p className="mt-6 text-base text-slate-500 dark:text-slate-400">
              Sincronize sua conta para visualizar a distribuição alfabética.
            </p>
          ) : (
            <div className="mt-5 flex flex-col gap-3">
              {analytics.top_buckets.map((item) => {
                const widthPct = Math.max(8, Math.round((item.count / maxBucketCount) * 100));
                const label = item.bucket === "SPECIAL" ? "Especiais" : item.bucket;
                return (
                  <button
                    key={item.bucket}
                    type="button"
                    onClick={() => onSelectBucket(item.bucket)}
                    className="group flex items-center gap-3 rounded-xl px-2 py-1 text-left transition hover:bg-fuchsia-50/70 dark:hover:bg-slate-800/80"
                  >
                    <span className="w-20 shrink-0 text-sm font-bold text-slate-700 group-hover:text-fuchsia-700 dark:text-slate-300 dark:group-hover:text-fuchsia-300">
                      {label}
                    </span>
                    <div className="h-3.5 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                      <div
                        style={{ width: `${widthPct}%` }}
                        className="h-full rounded-full bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500 transition-all duration-300"
                      />
                    </div>
                    <span className="w-12 text-right text-sm font-bold tabular-nums text-slate-800 dark:text-slate-200">
                      {item.count}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
