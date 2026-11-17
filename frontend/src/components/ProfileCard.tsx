"use client";

import { Profile } from "@/types/relationship";

interface ProfileCardProps {
  profile: Profile;
  isUnfollowing: boolean;
  onUnfollow: (pk: string) => void;
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
  isUnfollowing,
  onUnfollow,
}: ProfileCardProps) {
  const displayName = profile.full_name.trim() || "(Sem nome de exibição)";

  return (
    <article className="flex items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-slate-300">
      <div className="flex min-w-0 items-center gap-3.5">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-fuchsia-500 via-rose-500 to-amber-400 text-sm font-bold text-white">
          {profile.profile_pic_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={profile.profile_pic_url}
              alt={displayName}
              className="h-full w-full object-cover"
            />
          ) : (
            getInitials(profile.full_name, profile.username)
          )}
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <h3 className="truncate text-sm font-semibold text-slate-900">
              {displayName}
            </h3>
            {profile.is_verified && (
              <span
                title="Conta verificada"
                className="inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-sky-500 text-[10px] font-bold text-white"
              >
                ✓
              </span>
            )}
          </div>
          <p className="truncate text-xs text-slate-500">@{profile.username}</p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600">
              Grupo: {profile.bucket === "SPECIAL" ? "Especiais" : profile.bucket}
            </span>
            {profile.is_follower ? (
              <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-700">
                Segue você
              </span>
            ) : (
              <span className="rounded bg-rose-50 px-1.5 py-0.5 text-[10px] font-medium text-rose-700">
                Não segue você
              </span>
            )}
          </div>
        </div>
      </div>

      {profile.is_following && (
        <button
          type="button"
          onClick={() => onUnfollow(profile.pk)}
          disabled={isUnfollowing}
          className="shrink-0 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2 text-xs font-semibold text-rose-700 transition hover:bg-rose-600 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isUnfollowing ? "Enviando..." : "Unfollow"}
        </button>
      )}
    </article>
  );
}
