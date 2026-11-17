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
        className={`flex items-center justify-center gap-1.5 rounded-xl border text-xs font-semibold transition ${
          wide ? "px-3.5 py-2" : "h-9 min-w-[2.5rem] px-2"
        } ${
          isActive
            ? "border-transparent bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500 text-white shadow-md shadow-rose-500/20"
            : isEmpty
              ? "border-slate-100 bg-slate-50/80 text-slate-300 hover:border-slate-200 hover:text-slate-500"
              : "border-slate-200 bg-white text-slate-700 hover:border-fuchsia-300 hover:bg-fuchsia-50/60 hover:text-fuchsia-800"
        }`}
      >
        <span>{label}</span>
        <span
          className={`rounded-full px-1.5 py-0.5 text-[10px] font-bold ${
            isActive
              ? "bg-white/25 text-white"
              : isEmpty
                ? "text-slate-300"
                : "bg-fuchsia-50 text-fuchsia-700"
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
      className="rounded-2xl border border-rose-100/80 bg-white/90 p-4 shadow-sm backdrop-blur-sm"
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs font-bold uppercase tracking-wider text-fuchsia-700/80">
          Filtrar por inicial do nome (A–Z, 0–9, Caracteres Especiais)
        </span>
        {selectedBucket !== "ALL" && (
          <button
            type="button"
            onClick={() => onSelectBucket("ALL")}
            className="text-xs font-semibold text-rose-600 transition hover:text-rose-700 hover:underline"
          >
            Ver todos ({totalInList})
          </button>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5">
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
          "Caracteres Especiais",
          bucketCounts[SPECIAL_BUCKET] ?? 0,
          true
        )}
      </div>
    </section>
  );
}
