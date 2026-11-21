"use client";

import { useState } from "react";

import { Profile, RelationshipListType } from "@/types/relationship";

interface ProfileCardProps {
  profile: Profile;
  activeTab: RelationshipListType;
  isProcessing: boolean;
  onUnfollow: (pk: string) => void;
  onRemoveFollower: (pk: string) => void;
}

function getInitials(fullName: string, username: string): string {
  const source = (fullName || username || "?").trim();
  const parts = source.split(/\s+/);
  if (parts.length >= 2) {
    return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
  }
  return source.slice(0, 2).toUpperCase();
}

export function ProfileCard({
  profile,
  activeTab,
  isProcessing,
  onUnfollow,
  onRemoveFollower,
}: ProfileCardProps) {
  const [confirming, setConfirming] = useState(false);
  const [imageError, setImageError] = useState(false);

  const displayName = profile.full_name.trim() || "(Sem nome de exibição)";
  const showAvatarImage = Boolean(profile.profile_pic_url) && !imageError;

  const isFollowerMode =
    activeTab === "followers" || activeTab === "not_following_back";
  const canAct = isFollowerMode ? profile.is_follower : profile.is_following;
  const actionLabel = isFollowerMode ? "Remover seguidor" : "Deixar de seguir";

  const handleConfirmAction = () => {
    setConfirming(false);
    if (isFollowerMode) {
      onRemoveFollower(profile.pk);
    } else {
      onUnfollow(profile.pk);
    }
  };

  return (
    <article className="group flex flex-col justify-between gap-4 rounded-3xl border border-slate-200/90 bg-white/95 p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-fuchsia-300 hover:shadow-md hover:shadow-fuchsia-500/10 dark:border-slate-800 dark:bg-slate-900/90 dark:hover:border-fuchsia-500/60 sm:flex-row sm:items-center">
      <div className="flex min-w-0 items-center gap-4">
        <div
          className={`shrink-0 rounded-full p-0.5 ${
            profile.is_follower
              ? "bg-gradient-to-tr from-emerald-400 via-teal-400 to-sky-400"
              : "bg-gradient-to-tr from-fuchsia-500 via-rose-500 to-amber-400"
          }`}
        >
          <div className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full border-2 border-white bg-gradient-to-br from-fuchsia-500 via-rose-500 to-amber-400 text-base font-bold text-white dark:border-slate-900">
            {showAvatarImage ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={profile.profile_pic_url ?? undefined}
                alt={displayName}
                onError={() => setImageError(true)}
                className="h-full w-full object-cover"
              />
            ) : (
              getInitials(profile.full_name, profile.username)
            )}
          </div>
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="truncate text-base font-bold text-slate-900 dark:text-white">
              {displayName}
            </h3>
            {profile.is_verified && (
              <span
                title="Conta verificada"
                className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-500 text-xs font-bold text-white shadow-sm shadow-sky-500/30"
              >
                ✓
              </span>
            )}
          </div>

          <a
            href={`https://www.instagram.com/${encodeURIComponent(profile.username)}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 truncate text-sm font-medium text-slate-500 transition hover:text-fuchsia-600 dark:text-slate-400 dark:hover:text-fuchsia-400"
          >
            @{profile.username}
          </a>

          <div className="mt-2 flex flex-wrap gap-2">
            {profile.is_following && profile.is_follower ? (
              <span className="rounded-full bg-emerald-50 px-3 py-0.5 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-200 dark:bg-emerald-950/70 dark:text-emerald-300 dark:ring-emerald-800">
                Mútuo
              </span>
            ) : profile.is_follower ? (
              <span className="rounded-full bg-emerald-50 px-3 py-0.5 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-200 dark:bg-emerald-950/70 dark:text-emerald-300 dark:ring-emerald-800">
                Segue você
              </span>
            ) : (
              <span className="rounded-full bg-rose-50 px-3 py-0.5 text-xs font-semibold text-rose-700 ring-1 ring-rose-200 dark:bg-rose-950/70 dark:text-rose-300 dark:ring-rose-800">
                Não te segue
              </span>
            )}
          </div>
        </div>
      </div>

      {canAct && (
        <div className="flex shrink-0 items-center justify-end gap-2">
          {confirming ? (
            <>
              <button
                type="button"
                disabled={isProcessing}
                onClick={handleConfirmAction}
                className="rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-rose-700 disabled:opacity-50"
              >
                {isProcessing ? "Processando..." : "Confirmar"}
              </button>
              <button
                type="button"
                disabled={isProcessing}
                onClick={() => setConfirming(false)}
                className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              >
                Cancelar
              </button>
            </>
          ) : (
            <button
              type="button"
              disabled={isProcessing}
              onClick={() => setConfirming(true)}
              className="rounded-xl border border-rose-200 bg-rose-50/70 px-4 py-2.5 text-sm font-semibold text-rose-700 transition hover:border-rose-300 hover:bg-rose-100 disabled:opacity-50 dark:border-rose-900 dark:bg-rose-950/60 dark:text-rose-300 dark:hover:border-rose-700 dark:hover:bg-rose-950"
            >
              {actionLabel}
            </button>
          )}
        </div>
      )}
    </article>
  );
}
