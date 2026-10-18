import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Mail,
  Sparkles,
} from "lucide-react";

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { forgotPassword } from "../services/api";

export default function ForgotPassword() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setMessage("");
    setResetToken("");
    setSubmitting(true);

    try {
      const response = await forgotPassword(email.trim());

      setMessage(response.message);

      // Development-only V1 behavior.
      // The backend currently returns the token because
      // no email provider has been connected yet.
      if (response.reset_token) {
        setResetToken(response.reset_token);
      }
    } catch (err) {
      setError(err?.message || "Unable to process password reset.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#080c12] text-white">
      <div className="flex min-h-screen items-center justify-center px-5 py-10">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center justify-center">
            <Link to="/login" className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/20">
                <Sparkles className="h-5 w-5 text-blue-300" />
              </div>

              <div>
                <p className="text-lg font-bold tracking-tight">MUGONEXT</p>

                <p className="text-left text-[10px] uppercase tracking-[0.22em] text-slate-500">
                  Business Intelligence
                </p>
              </div>
            </Link>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 shadow-2xl shadow-black/20 sm:p-8">
            {!message ? (
              <>
                <div className="mb-8">
                  <p className="text-sm font-medium text-blue-300">
                    Account recovery
                  </p>

                  <h1 className="mt-2 text-3xl font-bold tracking-tight">
                    Forgot your password?
                  </h1>

                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    Enter your email and we'll help you reset your MUGONEXT
                    password.
                  </p>
                </div>

                {error && (
                  <div className="mb-5 rounded-xl border border-rose-400/15 bg-rose-400/5 px-4 py-3 text-sm text-rose-300">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                  <div>
                    <label
                      htmlFor="email"
                      className="mb-2 block text-sm font-medium text-slate-300"
                    >
                      Email
                    </label>

                    <div className="relative">
                      <Mail className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                      <input
                        id="email"
                        type="email"
                        autoComplete="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        required
                        className="w-full rounded-xl border border-white/10 bg-[#0a0f15] px-11 py-3.5 text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                        placeholder="you@company.com"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={submitting}
                    className="group flex w-full items-center justify-center gap-2 rounded-xl bg-blue-500 px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {submitting ? "Processing..." : "Request password reset"}

                    {!submitting && (
                      <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                    )}
                  </button>
                </form>

                <Link
                  to="/login"
                  className="mt-6 flex items-center justify-center gap-2 text-sm text-slate-500 transition hover:text-white"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to sign in
                </Link>
              </>
            ) : (
              <div className="text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-400/10">
                  <CheckCircle2 className="h-7 w-7 text-emerald-300" />
                </div>

                <h1 className="mt-6 text-2xl font-bold">
                  Reset request created
                </h1>

                <p className="mt-3 text-sm leading-6 text-slate-500">
                  {message}
                </p>

                {resetToken && (
                  <div className="mt-6 rounded-2xl border border-amber-400/20 bg-amber-400/5 p-4 text-left">
                    <p className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                      Local development reset token
                    </p>

                    <p className="mt-2 break-all text-xs leading-5 text-slate-400">
                      {resetToken}
                    </p>

                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/reset-password?token=${encodeURIComponent(
                            resetToken,
                          )}`,
                        )
                      }
                      className="mt-4 w-full rounded-xl bg-amber-400/10 px-4 py-3 text-sm font-semibold text-amber-200 transition hover:bg-amber-400/20"
                    >
                      Continue to reset password
                    </button>
                  </div>
                )}

                <Link
                  to="/login"
                  className="mt-6 inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-white"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to sign in
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
