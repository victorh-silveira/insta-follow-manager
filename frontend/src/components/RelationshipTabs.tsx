"use client";

import { RelationshipListType } from "@/types/relationship";

interface RelationshipTabsProps {
  activeTab: RelationshipListType;
  searchQuery: string;
  totalInList: number;
  onTabChange: (tab: RelationshipListType) => void;
  onSearchChange: (value: string) => void;
}

const TABS: { id: RelationshipListType; label: string }[] = [
  { id: "following", label: "Seguindo" },
  { id: "followers", label: "Seguidores" },
  { id: "non_followers", label: "Não me seguem de volta" },
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
      <div className="inline-flex flex-wrap gap-1.5 rounded-xl bg-slate-100 p-1">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                isActive
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {tab.label}
              {isActive && (
                <span className="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">
                  {totalInList}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="relative w-full sm:w-72">
        <input
          type="search"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Buscar por nome ou @user..."
          aria-label="Buscar perfil"
          className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 placeholder-slate-400 shadow-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
        />
      </div>
    </div>
  );
}
