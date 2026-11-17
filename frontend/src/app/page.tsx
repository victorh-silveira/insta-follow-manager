"use client";

import { useCallback, useEffect, useState } from "react";

import { AlphabetBar } from "@/components/AlphabetBar";
import { InstagramLoginCard } from "@/components/InstagramLoginCard";
import { ProfileCard } from "@/components/ProfileCard";
import { RelationshipTabs } from "@/components/RelationshipTabs";
import { SyncHeader } from "@/components/SyncHeader";
import { relationshipApi } from "@/services/relationshipApi";
import {
  AuthStatus,
  LoginPayload,
  Profile,
  RelationshipListType,
  SyncResponse,
} from "@/types/relationship";

export default function HomePage() {
  const [gatewayMode, setGatewayMode] = useState<string>("instagrapi");
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState<boolean>(true);
  const [isLoggingIn, setIsLoggingIn] = useState<boolean>(false);

  const [activeTab, setActiveTab] = useState<RelationshipListType>("following");
  const [selectedBucket, setSelectedBucket] = useState<string>("A");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [bucketCounts, setBucketCounts] = useState<Record<string, number>>({});
  const [totalInList, setTotalInList] = useState<number>(0);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [unfollowingPk, setUnfollowingPk] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<SyncResponse | null>(null);
  const [feedback, setFeedback] = useState<{
    type: "error" | "success";
    message: string;
  } | null>(null);

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
      await loadProfiles();
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
    setLastSync(null);
    setFeedback({
      type: "success",
      message: "Sessao do Instagram encerrada.",
    });
  };

  const handleUnfollow = async (pk: string) => {
    setUnfollowingPk(pk);
    setFeedback(null);
    try {
      const result = await relationshipApi.unfollow(pk);
      setFeedback({
        type: "success",
        message: `Unfollow enviado para ${result.full_name || result.username} (@${result.username}).`,
      });
      await loadProfiles();
    } catch (err) {
      setFeedback({
        type: "error",
        message:
          err instanceof Error ? err.message : "Falha ao executar unfollow.",
      });
    } finally {
      setUnfollowingPk(null);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
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
            className={`rounded-xl border px-4 py-3 text-sm font-medium ${
              feedback.type === "error"
                ? "border-rose-200 bg-rose-50 text-rose-800"
                : "border-emerald-200 bg-emerald-50 text-emerald-800"
            }`}
          >
            {feedback.message}
          </div>
        )}

        {isCheckingAuth ? (
          <div className="h-48 animate-pulse rounded-2xl border border-slate-200 bg-white" />
        ) : !authStatus?.authenticated ? (
          <InstagramLoginCard
            isLoggingIn={isLoggingIn}
            onLogin={handleLogin}
          />
        ) : (
          <>
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
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 6 }).map((_, idx) => (
                  <div
                    key={idx}
                    className="h-24 animate-pulse rounded-2xl border border-slate-200 bg-white"
                  />
                ))}
              </div>
            ) : profiles.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center">
                <p className="text-sm font-medium text-slate-700">
                  {totalInList === 0
                    ? "Nenhum perfil em cache nesta lista. Clique em \"Sincronizar Instagram\" para carregar."
                    : "Nenhum perfil encontrado para este filtro alfabético."}
                </p>
              </div>
            ) : (
              <section
                aria-label="Lista de perfis"
                className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
              >
                {profiles.map((profile) => (
                  <ProfileCard
                    key={profile.pk}
                    profile={profile}
                    isUnfollowing={unfollowingPk === profile.pk}
                    onUnfollow={handleUnfollow}
                  />
                ))}
              </section>
            )}
          </>
        )}
      </div>
    </main>
  );
}
