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
    activeClass: "bg-indigo-600 text-white shadow-sm shadow-indigo-500/25",
    badgeClass: "bg-white/25 text-white",
  },
  {
    id: "followers",
    label: "Seguidores",
    activeClass: "bg-emerald-600 text-white shadow-sm shadow-emerald-500/25",
    badgeClass: "bg-white/25 text-white",
  },
  {
    id: "non_followers",
    label: "Não me seguem de volta",
    activeClass:
      "bg-gradient-to-r from-rose-600 to-pink-600 text-white shadow-sm shadow-rose-500/25",
    badgeClass: "bg-white/25 text-white",
  },
  {
    id: "not_following_back",
    label: "Não sigo de volta",
    activeClass:
      "bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm shadow-amber-500/25",
    badgeClass: "bg-white/25 text-white",
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
    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="inline-flex flex-wrap gap-2 rounded-2xl border border-slate-200/90 bg-white/90 p-2 shadow-sm backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/90">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`inline-flex items-center rounded-xl px-5 py-3 text-base font-semibold transition ${
                isActive
                  ? tab.activeClass
                  : "text-slate-700 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
              }`}
            >
              {tab.label}
              {isActive && (
                <span
                  className={`ml-2.5 rounded-full px-2.5 py-0.5 text-sm font-bold ${tab.badgeClass}`}
                >
                  {totalInList}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="relative w-full lg:w-96">
        <svg
          className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400 dark:text-slate-500"
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
          placeholder="Buscar por nome ou @usuario..."
          aria-label="Buscar por nome ou @usuario"
          className="w-full rounded-2xl border border-slate-200 bg-white py-3.5 pl-12 pr-4 text-base text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-fuchsia-400 focus:ring-2 focus:ring-fuchsia-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-fuchsia-500"
        />
      </div>
    </div>
  );
}
