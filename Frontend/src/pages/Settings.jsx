import {
  Building2,
  Settings as SettingsIcon,
  ShieldCheck,
  User,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import Sidebar from "../components/Sidebar";

export default function Settings() {
  const { company } = useAuth();

  return (
    <div className="min-h-screen bg-[#0b0f14] text-white">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content */}
        <main className="min-w-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-5xl px-6 py-10 lg:px-8">
            {/* Page Header */}
            <div className="mb-10">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-500/10 ring-1 ring-white/10">
                  <SettingsIcon className="h-5 w-5 text-slate-300" />
                </div>

                <div>
                  <h1 className="text-3xl font-bold tracking-tight">
                    Settings
                  </h1>

                  <p className="mt-1 text-sm text-slate-500">
                    Manage your MUGONEXT workspace.
                  </p>
                </div>
              </div>
            </div>

            {/* Settings Sections */}
            <div className="space-y-6">
              {/* COMPANY */}
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                <div className="flex items-center gap-3">
                  <Building2 className="h-5 w-5 text-blue-300" />

                  <div>
                    <h2 className="font-semibold">Company</h2>

                    <p className="text-xs text-slate-600">
                      Your MUGONEXT workspace
                    </p>
                  </div>
                </div>

                <div className="mt-6 rounded-xl border border-white/10 bg-[#0a0f15] p-5">
                  <p className="text-xs uppercase tracking-wider text-slate-600">
                    Company name
                  </p>

                  <p className="mt-2 text-sm font-medium text-slate-200">
                    {company?.name || "MUGONEXT Company"}
                  </p>
                </div>
              </div>

              {/* ACCOUNT */}
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                <div className="flex items-center gap-3">
                  <User className="h-5 w-5 text-violet-300" />

                  <div>
                    <h2 className="font-semibold">Account</h2>

                    <p className="text-xs text-slate-600">
                      Account and access information
                    </p>
                  </div>
                </div>

                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  {/* Account Status */}
                  <div className="rounded-xl border border-white/10 bg-[#0a0f15] p-5">
                    <p className="text-xs uppercase tracking-wider text-slate-600">
                      Status
                    </p>

                    <div className="mt-2 flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-emerald-400" />

                      <span className="text-sm text-slate-300">Active</span>
                    </div>
                  </div>

                  {/* Security */}
                  <div className="rounded-xl border border-white/10 bg-[#0a0f15] p-5">
                    <p className="text-xs uppercase tracking-wider text-slate-600">
                      Security
                    </p>

                    <div className="mt-2 flex items-center gap-2">
                      <ShieldCheck className="h-4 w-4 text-emerald-300" />

                      <span className="text-sm text-slate-300">
                        JWT Protected
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* SYSTEM */}
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                <div className="flex items-center gap-3">
                  <SettingsIcon className="h-5 w-5 text-slate-300" />

                  <div>
                    <h2 className="font-semibold">MUGONEXT System</h2>

                    <p className="text-xs text-slate-600">Platform status</p>
                  </div>
                </div>

                <div className="mt-6 rounded-xl border border-white/10 bg-[#0a0f15] p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-200">
                        AI Decision Engine
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Forecasting and business intelligence services
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-emerald-400" />

                      <span className="text-xs font-medium text-emerald-300">
                        Online
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
