"use client";

import { FormEvent, useState } from "react";

import { ApiError } from "@/services/relationshipApi";
import { LoginPayload } from "@/types/relationship";

interface InstagramLoginCardProps {
  isLoggingIn: boolean;
  onLogin: (payload: LoginPayload) => Promise<void>;
}

export function InstagramLoginCard({
  isLoggingIn,
  onLogin,
}: InstagramLoginCardProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [requires2fa, setRequires2fa] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    try {
      await onLogin({
        username,
        password,
        verification_code: requires2fa ? verificationCode : undefined,
      });
    } catch (err) {
      if (err instanceof ApiError && err.requires2fa) {
        setRequires2fa(true);
      }
      setErrorMessage(
        err instanceof Error ? err.message : "Erro ao autenticar no Instagram."
      );
    }
  };

  return (
    <section
      aria-label="Autenticacao no Instagram"
      className="mx-auto w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h2 className="text-lg font-bold text-slate-900">
        Conectar conta do Instagram
      </h2>
      <p className="mt-1 text-xs text-slate-600">
        A senha e usada apenas no login para gerar a sessao local (
        <code>session.json</code>) e nunca e armazenada em banco ou logs.
      </p>

      {errorMessage && (
        <div
          role="alert"
          className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-xs font-medium text-rose-800"
        >
          {errorMessage}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3.5">
        <div>
          <label
            htmlFor="ig-username"
            className="block text-xs font-semibold text-slate-700"
          >
            Usuario (@username)
          </label>
          <input
            id="ig-username"
            type="text"
            required
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="seu.usuario"
            className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
          />
        </div>

        <div>
          <label
            htmlFor="ig-password"
            className="block text-xs font-semibold text-slate-700"
          >
            Senha
          </label>
          <input
            id="ig-password"
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-200"
          />
        </div>

        {requires2fa && (
          <div>
            <label
              htmlFor="ig-2fa"
              className="block text-xs font-semibold text-slate-700"
            >
              Codigo de verificacao (2FA)
            </label>
            <input
              id="ig-2fa"
              type="text"
              required
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              placeholder="123456"
              className="mt-1 w-full rounded-xl border border-amber-300 bg-amber-50 px-3.5 py-2 text-sm text-slate-900 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
            />
          </div>
        )}

        <button
          type="submit"
          disabled={isLoggingIn}
          className="mt-2 inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoggingIn
            ? "Conectando e sincronizando..."
            : requires2fa
              ? "Confirmar codigo 2FA"
              : "Conectar e Sincronizar"}
        </button>
      </form>
    </section>
  );
}
