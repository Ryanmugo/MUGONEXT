import {
  ArrowRight,
  Brain,
  CheckCircle2,
  LockKeyhole,
  Mail,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await login(email.trim(), password);

      // After successful login, go to the requested page
      // or default to the Dashboard.
      const destination = location.state?.from?.pathname || "/dashboard";

      navigate(destination, { replace: true });
    } catch (err) {
      setError(err?.message || "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#080c12] text-white">
      <div className="grid min-h-screen lg:grid-cols-2">
        {/* LEFT PANEL */}
        <section className="relative hidden overflow-hidden border-r border-white/10 bg-[#0b1017] lg:flex lg:flex-col lg:justify-between">
          <div className="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
          <div className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-violet-500/10 blur-3xl" />

          <div className="relative z-10 p-10">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/20">
                <Sparkles className="h-5 w-5 text-blue-300" />
              </div>

              <div>
                <p className="text-lg font-bold tracking-tight">MUGONEXT</p>

                <p className="text-[10px] uppercase tracking-[0.22em] text-slate-500">
                  Business Intelligence
                </p>
              </div>
            </div>
          </div>

          <div className="relative z-10 max-w-xl p-10 pb-16">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-400/15 bg-blue-400/5 px-3 py-1.5 text-xs font-semibold text-blue-300">
              <Brain className="h-3.5 w-3.5" />
              AI-powered decision intelligence
            </div>

            <h1 className="text-5xl font-bold leading-[1.05] tracking-tight">
              Turn business data into your next best decision.
            </h1>

            <p className="mt-6 max-w-lg text-base leading-7 text-slate-500">
              MUGONEXT transforms business data into forecasts, insights, and
              actionable recommendations.
            </p>

            <div className="mt-8 grid gap-3">
              {[
                "Forecast future business performance",
                "Understand what is driving the numbers",
                "Get actionable recommendations",
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-3 text-sm text-slate-300"
                >
                  <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="relative z-10 border-t border-white/10 p-10">
            <p className="text-xs text-slate-600">
              MUGONEXT • AI Business Intelligence Platform
            </p>
          </div>
        </section>

        {/* RIGHT PANEL */}
        <section className="flex items-center justify-center px-5 py-10 sm:px-8">
          <div className="w-full max-w-md">
            {/* MOBILE BRANDING */}
            <div className="mb-8 lg:hidden">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/20">
                  <Sparkles className="h-5 w-5 text-blue-300" />
                </div>

                <div>
                  <p className="text-lg font-bold">MUGONEXT</p>

                  <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                    Business Intelligence
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 shadow-2xl shadow-black/20 sm:p-8">
              <div className="mb-8">
                <p className="text-sm font-medium text-blue-300">
                  Welcome back
                </p>

                <h2 className="mt-2 text-3xl font-bold tracking-tight">
                  Sign in to MUGONEXT
                </h2>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Access your forecasts, insights, and recommendations.
                </p>
              </div>

              {error && (
                <div className="mb-5 rounded-xl border border-rose-400/15 bg-rose-400/5 px-4 py-3 text-sm text-rose-300">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* EMAIL */}
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

                {/* PASSWORD */}
                <div>
                  <label
                    htmlFor="password"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Password
                  </label>

                  <div className="relative">
                    <LockKeyhole className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />

                    <input
                      id="password"
                      type="password"
                      autoComplete="current-password"
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                      required
                      className="w-full rounded-xl border border-white/10 bg-[#0a0f15] px-11 py-3.5 text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                      placeholder="••••••••"
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Link
                    to="/forgot-password"
                    className="text-xs font-medium text-blue-300 transition hover:text-blue-200"
                  >
                    Forgot password?
                  </Link>
                </div>

                {/* SUBMIT */}
                <button
                  type="submit"
                  disabled={submitting}
                  className="group flex w-full items-center justify-center gap-2 rounded-xl bg-blue-500 px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting ? "Signing in..." : "Sign in"}

                  {!submitting && (
                    <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                  )}
                </button>
              </form>

              <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-600">
                <LockKeyhole className="h-3.5 w-3.5" />
                Secured by MUGONEXT authentication
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
