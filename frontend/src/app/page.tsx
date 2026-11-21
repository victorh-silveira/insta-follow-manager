"use client";

import { useCallback, useEffect, useState } from "react";

import { AlphabetBar } from "@/components/AlphabetBar";
import { AnalyticsDashboard } from "@/components/AnalyticsDashboard";
import { InstagramLoginCard } from "@/components/InstagramLoginCard";
import { ProfileCard } from "@/components/ProfileCard";
import { RelationshipTabs } from "@/components/RelationshipTabs";
import { SyncHeader } from "@/components/SyncHeader";
import { relationshipApi } from "@/services/relationshipApi";
import {
  AuthStatus,
  LoginPayload,
  Profile,
  RelationshipAnalytics,
  RelationshipListType,
  SyncResponse,
} from "@/types/relationship";

export default function HomePage() {
  const [gatewayMode, setGatewayMode] = useState<string>("instagrapi");
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState<boolean>(true);
  const [isLoggingIn, setIsLoggingIn] = useState<boolean>(false);

  const [activeTab, setActiveTab] = useState<RelationshipListType>("following");
  const [selectedBucket, setSelectedBucket] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [bucketCounts, setBucketCounts] = useState<Record<string, number>>({});
  const [totalInList, setTotalInList] = useState<number>(0);
  const [analytics, setAnalytics] = useState<RelationshipAnalytics | null>(null);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState<boolean>(false);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [processingPk, setProcessingPk] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<SyncResponse | null>(null);
  const [feedback, setFeedback] = useState<{
    type: "error" | "success";
    message: string;
  } | null>(null);

  const loadAnalytics = useCallback(async () => {
    setIsLoadingAnalytics(true);
    try {
      const data = await relationshipApi.getAnalytics();
      setAnalytics(data);
    } catch {
      setAnalytics(null);
    } finally {
      setIsLoadingAnalytics(false);
    }
  }, []);

  const loadProfiles = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await relationshipApi.list({
        listType: activeTab,
        bucket: selectedBucket,
        search: searchQuery,
      });
      setProfiles(data.profiles);
      setBucketCounts(data.bucket_counts);
      setTotalInList(data.total_in_list);
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err instanceof Error ? err.message : "Erro ao carregar perfis.",
      });
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, selectedBucket, searchQuery]);

  useEffect(() => {
    relationshipApi
      .getAuthStatus()
      .then((status) => {
        setAuthStatus(status);
        setGatewayMode(status.gateway_mode);
      })
      .catch(() => {
        setAuthStatus({
          authenticated: false,
          gateway_mode: "instagrapi",
          username: null,
          full_name: null,
          profile_pic_url: null,
        });
      })
      .finally(() => setIsCheckingAuth(false));
  }, []);

  useEffect(() => {
    if (!authStatus?.authenticated) return;
    let active = true;
    relationshipApi
      .getAnalytics()
      .then((data) => {
        if (active) setAnalytics(data);
      })
      .catch(() => {
        if (active) setAnalytics(null);
      });
    return () => {
      active = false;
    };
  }, [authStatus?.authenticated]);

  useEffect(() => {
    if (!authStatus?.authenticated) return;
    const timer = setTimeout(() => {
      void loadProfiles();
    }, 150);
    return () => clearTimeout(timer);
  }, [authStatus?.authenticated, loadProfiles]);

  const handleSync = async () => {
    setIsSyncing(true);
    setFeedback(null);
    try {
      const result = await relationshipApi.sync();
      setLastSync(result);
      setGatewayMode(result.gateway_mode);
      setFeedback({
        type: "success",
        message: `Sincronizado! ${result.following_count} seguindo e ${result.followers_count} seguidores carregados.`,
      });
      await Promise.all([loadProfiles(), loadAnalytics()]);
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err instanceof Error
            ? err.message
            : "Falha ao sincronizar com o Instagram.",
      });
    } finally {
      setIsSyncing(false);
    }
  };

  const handleLogin = async (payload: LoginPayload) => {
    setIsLoggingIn(true);
    setFeedback(null);
    try {
      const status = await relationshipApi.login(payload);
      setAuthStatus(status);
      setGatewayMode(status.gateway_mode);
      await handleSync();
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = async () => {
    const status = await relationshipApi.logout();
    setAuthStatus(status);
    setProfiles([]);
    setAnalytics(null);
    setLastSync(null);
    setFeedback({
      type: "success",
      message: "Sessão do Instagram encerrada.",
    });
  };

  const handleUnfollow = async (pk: string) => {
    setProcessingPk(pk);
    setFeedback(null);
    try {
      const result = await relationshipApi.unfollow(pk);
      const nameLabel = `${result.full_name || result.username} (@${result.username})`;
      setFeedback({
        type: "success",
        message: result.follower_removed
          ? `Deixou de seguir ${nameLabel} e removeu dos seguidores.`
          : `Deixou de seguir ${nameLabel}.`,
      });
      await Promise.all([loadProfiles(), loadAnalytics()]);
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err instanceof Error ? err.message : "Falha ao executar unfollow.",
      });
    } finally {
      setProcessingPk(null);
    }
  };

  const handleRemoveFollower = async (pk: string) => {
    setProcessingPk(pk);
    setFeedback(null);
    try {
      const result = await relationshipApi.removeFollower(pk);
      setFeedback({
        type: "success",
        message: `Seguidor removido: ${result.full_name || result.username} (@${result.username}).`,
      });
      await Promise.all([loadProfiles(), loadAnalytics()]);
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err instanceof Error ? err.message : "Falha ao remover seguidor.",
      });
    } finally {
      setProcessingPk(null);
    }
  };

  const handleClearFilters = () => {
    setSelectedBucket("ALL");
    setSearchQuery("");
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-rose-50/80 via-slate-50 to-indigo-50/80 px-4 py-8 text-slate-900 dark:from-slate-950 dark:via-slate-950 dark:to-indigo-950/60 dark:text-slate-100 sm:px-8 lg:px-10">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-24 left-1/4 h-80 w-80 rounded-full bg-fuchsia-200/35 blur-3xl dark:bg-fuchsia-900/20"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-16 right-1/4 h-80 w-80 rounded-full bg-amber-200/35 blur-3xl dark:bg-indigo-900/20"
      />

      <div className="relative mx-auto flex max-w-[1440px] flex-col gap-7">
        <SyncHeader
          gatewayMode={gatewayMode}
          authStatus={authStatus}
          isSyncing={isSyncing}
          lastSync={lastSync}
          onSync={handleSync}
          onLogout={handleLogout}
        />

        {feedback && (
          <div
            role="status"
            className={`flex items-center justify-between gap-4 rounded-2xl border px-5 py-4 text-base font-medium shadow-sm ${
              feedback.type === "error"
                ? "border-rose-200 bg-rose-50/95 text-rose-800 dark:border-rose-900 dark:bg-rose-950/70 dark:text-rose-200"
                : "border-emerald-200 bg-emerald-50/95 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/70 dark:text-emerald-200"
            }`}
          >
            <div className="flex items-center gap-3">
              <span
                className={`h-2.5 w-2.5 shrink-0 rounded-full ${
                  feedback.type === "error" ? "bg-rose-500" : "bg-emerald-500"
                }`}
              />
              <span>{feedback.message}</span>
            </div>
            <button
              type="button"
              onClick={() => setFeedback(null)}
              aria-label="Fechar aviso"
              className="rounded-lg p-1.5 opacity-70 transition hover:bg-black/5 hover:opacity-100 dark:hover:bg-white/10"
            >
              <svg
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                aria-hidden="true"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        )}

        {isCheckingAuth ? (
          <div className="h-56 animate-pulse rounded-3xl border border-rose-100 bg-white/80 dark:border-slate-800 dark:bg-slate-900/70" />
        ) : !authStatus?.authenticated ? (
          <InstagramLoginCard
            isLoggingIn={isLoggingIn}
            onLogin={handleLogin}
          />
        ) : (
          <>
            <AnalyticsDashboard
              analytics={analytics}
              authStatus={authStatus}
              isLoading={isLoadingAnalytics}
              onSelectTab={setActiveTab}
              onSelectBucket={setSelectedBucket}
            />

            <RelationshipTabs
              activeTab={activeTab}
              searchQuery={searchQuery}
              totalInList={totalInList}
              onTabChange={setActiveTab}
              onSearchChange={setSearchQuery}
            />

            <AlphabetBar
              selectedBucket={selectedBucket}
              bucketCounts={bucketCounts}
              totalInList={totalInList}
              onSelectBucket={setSelectedBucket}
            />

            {isLoading ? (
              <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, idx) => (
                  <div
                    key={idx}
                    className="h-28 animate-pulse rounded-3xl border border-rose-100/70 bg-white/80 dark:border-slate-800 dark:bg-slate-900/70"
                  />
                ))}
              </div>
            ) : profiles.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-4 rounded-3xl border border-dashed border-fuchsia-200 bg-white/90 p-14 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-fuchsia-50 text-fuchsia-600 dark:bg-fuchsia-950 dark:text-fuchsia-300">
                  <svg
                    className="h-7 w-7"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    aria-hidden="true"
                  >
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                </div>
                <p className="text-base font-semibold text-slate-700 dark:text-slate-200">
                  {totalInList === 0
                    ? "Nenhum perfil em cache nesta lista. Clique em \"Sincronizar Instagram\" para carregar."
                    : "Nenhum perfil encontrado para este filtro alfabético ou busca."}
                </p>
                {totalInList === 0 ? (
                  <button
                    type="button"
                    onClick={handleSync}
                    disabled={isSyncing}
                    className="mt-1 rounded-xl bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500 px-5 py-3 text-base font-semibold text-white shadow-sm transition hover:brightness-105"
                  >
                    Sincronizar agora
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleClearFilters}
                    className="mt-1 rounded-xl border border-fuchsia-200 bg-fuchsia-50 px-5 py-3 text-base font-semibold text-fuchsia-700 transition hover:bg-fuchsia-100 dark:border-fuchsia-800 dark:bg-fuchsia-950 dark:text-fuchsia-300 dark:hover:bg-fuchsia-900"
                  >
                    Limpar filtros
                  </button>
                )}
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between px-1 text-base font-medium text-slate-600 dark:text-slate-400">
                  <span>
                    Exibindo{" "}
                    <strong className="text-slate-900 dark:text-white">{profiles.length}</strong>{" "}
                    {profiles.length === 1 ? "perfil" : "perfis"}
                    {selectedBucket !== "ALL"
                      ? ` no grupo "${selectedBucket === "SPECIAL" ? "Especiais" : selectedBucket}"`
                      : ""}
                  </span>
                </div>
                <section
                  aria-label="Lista de perfis"
                  className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3"
                >
                  {profiles.map((profile) => (
                    <ProfileCard
                      key={profile.pk}
                      profile={profile}
                      activeTab={activeTab}
                      isProcessing={processingPk === profile.pk}
                      onUnfollow={handleUnfollow}
                      onRemoveFollower={handleRemoveFollower}
                    />
                  ))}
                </section>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
