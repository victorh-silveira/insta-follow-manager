"use client";

import { FormEvent, useState } from "react";

import { ApiError } from "@/services/relationshipApi";
import { LoginPayload } from "@/types/relationship";

interface InstagramLoginCardProps {
  isLoggingIn: boolean;
  onLogin: (payload: LoginPayload) => Promise<void>;
}

type AuthMode = "credentials" | "session_id";

export function InstagramLoginCard({
  isLoggingIn,
  onLogin,
}: InstagramLoginCardProps) {
  const [authMode, setAuthMode] = useState<AuthMode>("credentials");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [challengeCode, setChallengeCode] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [requires2fa, setRequires2fa] = useState(false);
  const [requiresChallenge, setRequiresChallenge] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    try {
      if (authMode === "session_id") {
        await onLogin({
          session_id: sessionId,
        });
        return;
      }

      await onLogin({
        username,
        password,
        verification_code: requires2fa ? verificationCode : undefined,
        challenge_code: requiresChallenge ? challengeCode : undefined,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.requires2fa) setRequires2fa(true);
        if (err.requiresChallenge) setRequiresChallenge(true);
      }
      setErrorMessage(
        err instanceof Error ? err.message : "Erro ao autenticar no Instagram."
      );
    }
  };

  return (
    <section
      aria-label="Autenticacao no Instagram"
      className="relative mx-auto w-full max-w-md overflow-hidden rounded-3xl border border-rose-100/80 bg-white/95 p-6 shadow-xl shadow-rose-500/10 backdrop-blur-md sm:p-8"
    >
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500"
      />

      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-fuchsia-100 to-rose-100 text-fuchsia-600">
          <svg
            className="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900">
            Conectar conta do Instagram
          </h2>
          <p className="text-xs text-slate-500">
            Sessão local segura para sincronizar seguidores
          </p>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-1.5 rounded-xl bg-slate-100 p-1">
        <button
          type="button"
          onClick={() => {
            setAuthMode("credentials");
            setErrorMessage(null);
          }}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
            authMode === "credentials"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Usuário e senha
        </button>
        <button
          type="button"
          onClick={() => {
            setAuthMode("session_id");
            setErrorMessage(null);
          }}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
            authMode === "session_id"
              ? "bg-white text-fuchsia-700 shadow-sm"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          Session ID (Cookie)
        </button>
      </div>

      <p className="mt-3 rounded-xl border border-indigo-100 bg-indigo-50/60 px-3.5 py-2.5 text-xs leading-relaxed text-indigo-900">
        {authMode === "session_id" ? (
          <>
            No navegador logado no Instagram, abra o DevTools (<code className="font-semibold text-indigo-700">F12</code> → Application → Cookies) e copie o valor de{" "}
            <code className="font-semibold text-indigo-700">sessionid</code>. Evita bloqueios de Bloks/Checkpoint.
          </>
        ) : (
          <>
            A senha é usada apenas no login para gerar a sessão local (
            <code className="font-semibold text-indigo-700">session.json</code>) e
            nunca é armazenada em banco ou logs.
          </>
        )}
      </p>

      {errorMessage && (
        <div
          role="alert"
          className="mt-4 flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-xs font-medium text-rose-800"
        >
          <svg
            className="mt-0.5 h-4 w-4 shrink-0 text-rose-600"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-4">
        {authMode === "session_id" ? (
          <div>
            <label
              htmlFor="ig-session-id"
              className="block text-xs font-semibold text-slate-700"
            >
              Cookie sessionid
            </label>
            <input
              id="ig-session-id"
              type="password"
              required
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              placeholder="Cole aqui o cookie sessionid"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2.5 text-sm font-mono text-slate-900 outline-none transition focus:border-fuchsia-400 focus:bg-white focus:ring-2 focus:ring-fuchsia-100"
            />
          </div>
        ) : (
          <>
            <div>
              <label
                htmlFor="ig-username"
                className="block text-xs font-semibold text-slate-700"
              >
                Usuário (@username)
              </label>
              <input
                id="ig-username"
                type="text"
                required
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="seu.usuario"
                className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-fuchsia-400 focus:bg-white focus:ring-2 focus:ring-fuchsia-100"
              />
            </div>

            <div>
              <label
                htmlFor="ig-password"
                className="block text-xs font-semibold text-slate-700"
              >
                Senha
              </label>
              <div className="relative mt-1.5">
                <input
                  id="ig-password"
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50/60 py-2.5 pl-3.5 pr-11 text-sm text-slate-900 outline-none transition focus:border-fuchsia-400 focus:bg-white focus:ring-2 focus:ring-fuchsia-100"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                  className="absolute inset-y-0 right-0 flex items-center px-3 text-slate-400 transition hover:text-fuchsia-600"
                >
                  {showPassword ? (
                    <svg
                      className="h-4 w-4"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      aria-hidden="true"
                    >
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg
                      className="h-4 w-4"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      aria-hidden="true"
                    >
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {requires2fa && (
              <div className="rounded-2xl border border-amber-200 bg-amber-50/70 p-3.5">
                <label
                  htmlFor="ig-2fa"
                  className="block text-xs font-semibold text-amber-900"
                >
                  Código de verificação (2FA)
                </label>
                <input
                  id="ig-2fa"
                  type="text"
                  required
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="123456"
                  className="mt-1.5 w-full rounded-xl border border-amber-300 bg-white px-3.5 py-2 text-sm font-mono tracking-widest text-slate-900 outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-200"
                />
              </div>
            )}

            {requiresChallenge && (
              <div className="rounded-2xl border border-fuchsia-200 bg-fuchsia-50/70 p-3.5">
                <label
                  htmlFor="ig-challenge"
                  className="block text-xs font-semibold text-fuchsia-900"
                >
                  Código do Challenge (E-mail ou SMS)
                </label>
                <input
                  id="ig-challenge"
                  type="text"
                  required
                  value={challengeCode}
                  onChange={(e) => setChallengeCode(e.target.value)}
                  placeholder="123456"
                  className="mt-1.5 w-full rounded-xl border border-fuchsia-300 bg-white px-3.5 py-2 text-sm font-mono tracking-widest text-slate-900 outline-none focus:border-fuchsia-500 focus:ring-2 focus:ring-fuchsia-200"
                />
              </div>
            )}
          </>
        )}

        <button
          type="submit"
          disabled={isLoggingIn}
          className="mt-1 inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-fuchsia-600 via-rose-500 to-amber-500 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-rose-500/25 transition hover:brightness-105 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoggingIn
            ? "Conectando e sincronizando..."
            : authMode === "session_id"
              ? "Conectar com Session ID"
              : requiresChallenge
                ? "Confirmar código do Challenge"
                : requires2fa
                  ? "Confirmar código 2FA"
                  : "Conectar e Sincronizar"}
        </button>
      </form>
    </section>
  );
}
