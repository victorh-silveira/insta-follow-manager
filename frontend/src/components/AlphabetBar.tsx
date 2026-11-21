"use client";

import {
  DIGITS_BUCKET,
  LETTER_BUCKETS,
  SPECIAL_BUCKET,
} from "@/types/relationship";

interface AlphabetBarProps {
  selectedBucket: string;
  bucketCounts: Record<string, number>;
  totalInList: number;
  onSelectBucket: (bucket: string) => void;
}

export function AlphabetBar({
  selectedBucket,
  bucketCounts,
  totalInList,
  onSelectBucket,
}: AlphabetBarProps) {
  const renderButton = (
    key: string,
    label: string,
    count: number,
    wide = false
  ) => {
    const isActive = selectedBucket === key;
    const isEmpty = count === 0 && key !== "ALL";

    return (
      <button
        key={key}
        type="button"
        onClick={() => onSelectBucket(key)}
        className={`flex items-center justify-center gap-2 rounded-xl border text-sm font-semibold transition ${
          wide ? "px-4 py-2.5" : "h-11 min-w-[3.25rem] px-3"
        } ${
          isActive
            ? "border-transparent bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500 text-white shadow-md shadow-rose-500/25"
            : isEmpty
              ? "border-slate-200/70 bg-slate-50 text-slate-400 hover:border-slate-300 hover:text-slate-600 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-600 dark:hover:border-slate-700 dark:hover:text-slate-400"
              : "border-slate-200 bg-white text-slate-800 hover:border-fuchsia-300 hover:bg-fuchsia-50/70 hover:text-fuchsia-800 dark:border-slate-700 dark:bg-slate-800/80 dark:text-slate-200 dark:hover:border-fuchsia-500/70 dark:hover:bg-slate-800 dark:hover:text-fuchsia-300"
        }`}
      >
        <span>{label}</span>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-bold ${
            isActive
              ? "bg-white/25 text-white"
              : isEmpty
                ? "text-slate-400 dark:text-slate-600"
                : "bg-fuchsia-50 text-fuchsia-700 dark:bg-fuchsia-950 dark:text-fuchsia-300"
          }`}
        >
          {count}
        </span>
      </button>
    );
  };

  return (
    <section
      aria-label="Filtro alfabético por nome de exibição"
      className="rounded-3xl border border-rose-200/70 bg-white/95 p-5 shadow-sm backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/90 sm:p-6"
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm font-bold uppercase tracking-wider text-fuchsia-700 dark:text-fuchsia-300">
          Filtrar por inicial do nome (A–Z, 0–9, Especiais)
        </span>
        {selectedBucket !== "ALL" && (
          <button
            type="button"
            onClick={() => onSelectBucket("ALL")}
            className="text-sm font-semibold text-rose-600 transition hover:text-rose-700 hover:underline dark:text-rose-400 dark:hover:text-rose-300"
          >
            Ver todos ({totalInList})
          </button>
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {renderButton("ALL", "Todos", totalInList, true)}
        {LETTER_BUCKETS.map((letter) =>
          renderButton(letter, letter, bucketCounts[letter] ?? 0)
        )}
        {renderButton(
          DIGITS_BUCKET,
          "0–9",
          bucketCounts[DIGITS_BUCKET] ?? 0,
          true
        )}
        {renderButton(
          SPECIAL_BUCKET,
          "Especiais",
          bucketCounts[SPECIAL_BUCKET] ?? 0,
          true
        )}
      </div>
    </section>
  );
}
