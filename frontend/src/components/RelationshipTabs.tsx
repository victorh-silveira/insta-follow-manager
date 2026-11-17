"use client";

import { RelationshipListType } from "@/types/relationship";

interface RelationshipTabsProps {
  activeTab: RelationshipListType;
  searchQuery: string;
  totalInList: number;
  onTabChange: (tab: RelationshipListType) => void;
  onSearchChange: (value: string) => void;
}

const TABS: {
  id: RelationshipListType;
  label: string;
  activeClass: string;
  badgeClass: string;
}[] = [
  {
    id: "following",
    label: "Seguindo",
    activeClass:
      "bg-indigo-600 text-white shadow-sm shadow-indigo-500/25",
    badgeClass: "bg-white/20 text-white",
  },
  {
    id: "followers",
    label: "Seguidores",
    activeClass:
      "bg-emerald-600 text-white shadow-sm shadow-emerald-500/25",
    badgeClass: "bg-white/20 text-white",
  },
  {
    id: "non_followers",
    label: "Não me seguem de volta",
    activeClass:
      "bg-gradient-to-r from-rose-600 to-pink-600 text-white shadow-sm shadow-rose-500/25",
    badgeClass: "bg-white/20 text-white",
  },
];

export function RelationshipTabs({
  activeTab,
  searchQuery,
  totalInList,
  onTabChange,
  onSearchChange,
}: RelationshipTabsProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="inline-flex flex-wrap gap-1.5 rounded-2xl border border-slate-200/80 bg-white/80 p-1.5 shadow-sm backdrop-blur-sm">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`inline-flex items-center rounded-xl px-4 py-2 text-sm font-semibold transition ${
                isActive
                  ? tab.activeClass
                  : "text-slate-600 hover:bg-slate-100/80 hover:text-slate-900"
              }`}
            >
              {tab.label}
              {isActive && (
                <span
                  className={`ml-2 rounded-full px-2 py-0.5 text-xs font-bold ${tab.badgeClass}`}
                >
                  {totalInList}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="relative w-full sm:w-80">
        <svg
          className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="search"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Buscar por nome ou @user..."
          aria-label="Buscar perfil"
          className="w-full rounded-xl border border-slate-200 bg-white/90 py-2.5 pl-10 pr-9 text-sm text-slate-900 placeholder-slate-400 shadow-sm outline-none transition focus:border-fuchsia-400 focus:bg-white focus:ring-2 focus:ring-fuchsia-100"
        />
        {searchQuery && (
          <button
            type="button"
            onClick={() => onSearchChange("")}
            aria-label="Limpar busca"
            className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
          >
            <svg
              className="h-3.5 w-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              aria-hidden="true"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
