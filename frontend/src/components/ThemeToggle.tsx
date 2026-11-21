"use client";

import { useSyncExternalStore } from "react";

function subscribeTheme(callback: () => void): () => void {
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  const handleSystemChange = (event: MediaQueryListEvent) => {
    const saved = localStorage.getItem("theme");
    if (saved !== "light" && saved !== "dark") {
      document.documentElement.classList.toggle("dark", event.matches);
    }
    callback();
  };

  mediaQuery.addEventListener("change", handleSystemChange);
  window.addEventListener("themechange", callback);
  return () => {
    mediaQuery.removeEventListener("change", handleSystemChange);
    window.removeEventListener("themechange", callback);
  };
}

function getThemeSnapshot(): boolean {
  return document.documentElement.classList.contains("dark");
}

function getServerThemeSnapshot(): boolean {
  return false;
}

export function ThemeToggle() {
  const isDark = useSyncExternalStore(
    subscribeTheme,
    getThemeSnapshot,
    getServerThemeSnapshot
  );

  const toggleTheme = () => {
    const nextDark = !isDark;
    document.documentElement.classList.toggle("dark", nextDark);
    localStorage.setItem("theme", nextDark ? "dark" : "light");
    window.dispatchEvent(new Event("themechange"));
  };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? "Ativar modo claro" : "Ativar modo escuro"}
      title={isDark ? "Alternar para modo claro" : "Alternar para modo escuro"}
      className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-base font-semibold text-slate-700 shadow-sm transition hover:border-fuchsia-300 hover:bg-fuchsia-50 hover:text-fuchsia-800 dark:border-slate-700 dark:bg-slate-800/90 dark:text-slate-100 dark:hover:border-fuchsia-500/60 dark:hover:bg-slate-800"
    >
      {isDark ? (
        <svg
          className="h-5 w-5 text-amber-400"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2" />
          <path d="M12 20v2" />
          <path d="m4.93 4.93 1.41 1.41" />
          <path d="m17.66 17.66 1.41 1.41" />
          <path d="M2 12h2" />
          <path d="M20 12h2" />
          <path d="m6.34 17.66-1.41 1.41" />
          <path d="m19.07 4.93-1.41 1.41" />
        </svg>
      ) : (
        <svg
          className="h-5 w-5 text-indigo-600 dark:text-indigo-400"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
        </svg>
      )}
      <span className="hidden sm:inline">{isDark ? "Claro" : "Escuro"}</span>
    </button>
  );
}
