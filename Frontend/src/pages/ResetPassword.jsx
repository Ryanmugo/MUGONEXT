import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  LockKeyhole,
  Sparkles,
} from "lucide-react";

import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { resetPassword } from "../services/api";

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!token) {
      setError("This password reset link is missing its token.");
      return;
    }

    if (password.length < 8) {
      setError("Your new password must be at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    setSubmitting(true);

    try {
      const response = await resetPassword(token, password);

      setSuccess(response.message);

      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1800);
    } catch (err) {
      setError(err?.message || "Unable to reset your password.");
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
            {success ? (
              <div className="text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-400/10">
                  <CheckCircle2 className="h-7 w-7 text-emerald-300" />
                </div>

                <h1 className="mt-6 text-2xl font-bold">Password changed</h1>

                <p className="mt-3 text-sm leading-6 text-slate-500">
                  {success}
                </p>

                <p className="mt-5 text-xs text-slate-600">
                  Returning you to sign in...
                </p>
              </div>
            ) : (
              <>
                <div className="mb-8">
                  <p className="text-sm font-medium text-blue-300">
                    Account recovery
                  </p>

                  <h1 className="mt-2 text-3xl font-bold tracking-tight">
                    Create a new password
                  </h1>

                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    Choose a new password for your MUGONEXT account.
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
                      htmlFor="password"
                      className="mb-2 block text-sm font-medium text-slate-300"
                    >
                      New password
                    </label>

                    <div className="relative">
                      <LockKeyhole className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                      <input
                        id="password"
                        type="password"
                        autoComplete="new-password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        required
                        minLength={8}
                        className="w-full rounded-xl border border-white/10 bg-[#0a0f15] px-11 py-3.5 text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                        placeholder="At least 8 characters"
                      />
                    </div>
                  </div>

                  <div>
                    <label
                      htmlFor="confirmPassword"
                      className="mb-2 block text-sm font-medium text-slate-300"
                    >
                      Confirm new password
                    </label>

                    <div className="relative">
                      <LockKeyhole className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                      <input
                        id="confirmPassword"
                        type="password"
                        autoComplete="new-password"
                        value={confirmPassword}
                        onChange={(event) =>
                          setConfirmPassword(event.target.value)
                        }
                        required
                        minLength={8}
                        className="w-full rounded-xl border border-white/10 bg-[#0a0f15] px-11 py-3.5 text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                        placeholder="Repeat your new password"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={submitting}
                    className="group flex w-full items-center justify-center gap-2 rounded-xl bg-blue-500 px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {submitting ? "Updating password..." : "Reset password"}

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
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
