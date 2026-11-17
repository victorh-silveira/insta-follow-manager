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
        className={`flex items-center justify-center gap-1.5 rounded-lg border text-xs font-semibold transition ${
          wide ? "px-3 py-2" : "h-9 min-w-[2.4rem] px-2"
        } ${
          isActive
            ? "border-slate-900 bg-slate-900 text-white shadow-sm"
            : isEmpty
              ? "border-slate-100 bg-slate-50 text-slate-300 hover:border-slate-200 hover:text-slate-500"
              : "border-slate-200 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50"
        }`}
      >
        <span>{label}</span>
        <span
          className={`rounded-full px-1.5 py-0.5 text-[10px] ${
            isActive
              ? "bg-white/20 text-white"
              : isEmpty
                ? "text-slate-300"
                : "bg-slate-100 text-slate-500"
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
      className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Filtrar por inicial do nome (A–Z, 0–9, Caracteres Especiais)
        </span>
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
