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

  const isFollowerMode = activeTab === "followers";
  const canAct = isFollowerMode ? profile.is_follower : profile.is_following;
  const actionLabel = isFollowerMode ? "Remover seguidor" : "Remover seguindo";

  const handleConfirmAction = () => {
    setConfirming(false);
    if (isFollowerMode) {
      onRemoveFollower(profile.pk);
    } else {
      onUnfollow(profile.pk);
    }
  };

  return (
    <article className="group flex items-center justify-between gap-3 rounded-2xl border border-slate-200/80 bg-white/95 p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-fuchsia-200 hover:shadow-md hover:shadow-fuchsia-500/10">
      <div className="flex min-w-0 items-center gap-3.5">
        <div
          className={`rounded-full p-0.5 ${
            profile.is_follower
              ? "bg-gradient-to-tr from-emerald-400 via-teal-400 to-sky-400"
              : "bg-gradient-to-tr from-fuchsia-500 via-rose-500 to-amber-400"
          }`}
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full border-2 border-white bg-gradient-to-br from-fuchsia-500 via-rose-500 to-amber-400 text-sm font-bold text-white">
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
          <div className="flex items-center gap-1.5">
            <h3 className="truncate text-sm font-bold text-slate-900">
              {displayName}
            </h3>
            {profile.is_verified && (
              <span
                title="Conta verificada"
                className="inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-sky-500 text-[10px] font-bold text-white shadow-sm shadow-sky-500/30"
              >
                ✓
              </span>
            )}
          </div>

          <a
            href={`https://www.instagram.com/${encodeURIComponent(profile.username)}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 truncate text-xs font-medium text-slate-500 transition hover:text-fuchsia-600"
          >
            @{profile.username}
          </a>

          <div className="mt-1.5 flex flex-wrap gap-1.5">
            <span className="rounded-md bg-violet-50 px-2 py-0.5 text-[10px] font-semibold text-violet-700 ring-1 ring-violet-200/70">
              {profile.bucket === "SPECIAL" ? "Especiais" : profile.bucket}
            </span>
            {profile.is_follower ? (
              <span className="rounded-md bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 ring-1 ring-emerald-200/70">
                Segue você
              </span>
            ) : (
              <span className="rounded-md bg-rose-50 px-2 py-0.5 text-[10px] font-semibold text-rose-700 ring-1 ring-rose-200/70">
                Não segue você
              </span>
            )}
          </div>
        </div>
      </div>

      {canAct && (
        <div className="flex shrink-0 items-center gap-1.5">
          {confirming ? (
            <>
              <button
                type="button"
                onClick={handleConfirmAction}
                disabled={isProcessing}
                className={`rounded-xl px-3 py-2 text-xs font-bold text-white shadow-sm transition disabled:cursor-not-allowed disabled:opacity-50 ${
                  isFollowerMode
                    ? "bg-amber-600 shadow-amber-500/25 hover:bg-amber-700"
                    : "bg-rose-600 shadow-rose-500/25 hover:bg-rose-700"
                }`}
              >
                {isProcessing ? "Enviando..." : "Confirmar"}
              </button>
              <button
                type="button"
                onClick={() => setConfirming(false)}
                disabled={isProcessing}
                className="rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50"
              >
                Não
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setConfirming(true)}
              disabled={isProcessing}
              className={`rounded-xl border px-3 py-2 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${
                isFollowerMode
                  ? "border-amber-200 bg-amber-50/80 text-amber-800 hover:border-amber-600 hover:bg-amber-600 hover:text-white"
                  : "border-rose-200 bg-rose-50/80 text-rose-700 hover:border-rose-600 hover:bg-rose-600 hover:text-white"
              }`}
            >
              {isProcessing ? "Enviando..." : actionLabel}
            </button>
          )}
        </div>
      )}
    </article>
  );
}
