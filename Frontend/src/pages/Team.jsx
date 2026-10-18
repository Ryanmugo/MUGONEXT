import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

import {
  Brain,
  LayoutDashboard,
  FileSpreadsheet,
  BarChart3,
  Lightbulb,
  Users,
  Settings,
  ShieldCheck,
  LogOut,
  X,
  Menu,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

function SidebarLink({ to, icon: Icon, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        [
          "flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition",
          isActive
            ? "bg-blue-500/10 text-blue-400"
            : "text-slate-400 hover:bg-white/5 hover:text-white",
        ].join(" ")
      }
    >
      {" "}
      <Icon className="h-4 w-4 shrink-0" />
      {children}{" "}
    </NavLink>
  );
}

export default function Team() {
  const navigate = useNavigate();
  const { company, logout } = useAuth();

  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false);

  const companyName =
    company?.name ||
    company?.company_name ||
    company?.business_name ||
    "MUGONEXT Company";

  function closeMobileSidebar() {
    setMobileSidebarOpen(false);
  }

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-[#0b0f14] text-slate-200">
      {/* MOBILE OVERLAY */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={closeMobileSidebar}
        />
      )}
      ```
      {/* SIDEBAR */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 transform border-r border-white/10 bg-[#0d1219] transition-transform duration-200 lg:translate-x-0 ${
          mobileSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* BRAND */}
        <div className="flex h-20 items-center justify-between border-b border-white/10 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
              <Brain className="h-5 w-5" />
            </div>

            <div>
              <div className="text-lg font-semibold tracking-tight text-white">
                MUGONEXT
              </div>

              <div className="text-[11px] text-slate-500">
                Intelligent Business AI
              </div>
            </div>
          </div>

          <button
            type="button"
            aria-label="Close navigation"
            className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-white lg:hidden"
            onClick={closeMobileSidebar}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* NAVIGATION */}
        <div className="px-4 py-5">
          <p className="px-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-600">
            Workspace
          </p>

          <nav className="mt-3 space-y-1">
            <SidebarLink to="/dashboard" icon={LayoutDashboard}>
              Dashboard
            </SidebarLink>

            <SidebarLink to="/datasets" icon={FileSpreadsheet}>
              Datasets
            </SidebarLink>

            <SidebarLink to="/forecasts" icon={BarChart3}>
              Forecasts
            </SidebarLink>

            <SidebarLink to="/recommendations" icon={Lightbulb}>
              Recommendations
            </SidebarLink>
          </nav>

          <p className="mt-8 px-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-600">
            Management
          </p>

          <nav className="mt-3 space-y-1">
            <SidebarLink to="/team" icon={Users}>
              Team
            </SidebarLink>

            <SidebarLink to="/settings" icon={Settings}>
              Settings
            </SidebarLink>
          </nav>
        </div>

        {/* USER / COMPANY */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-white/10 p-4">
          <div className="mb-3 rounded-xl border border-white/10 bg-white/[0.02] p-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-500/10 text-blue-400">
                <ShieldCheck className="h-4 w-4" />
              </div>

              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-white">
                  {companyName}
                </p>

                <p className="text-xs text-emerald-500">Connected</p>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-400 transition hover:bg-rose-500/10 hover:text-rose-400"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>
      {/* MAIN */}
      <main className="lg:pl-72">
        {/* HEADER */}
        <header className="sticky top-0 z-30 border-b border-white/10 bg-[#0b0f14]/90 backdrop-blur-xl">
          <div className="flex h-20 items-center justify-between px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Open navigation"
                className="rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white lg:hidden"
                onClick={() => setMobileSidebarOpen(true)}
              >
                <Menu className="h-5 w-5" />
              </button>

              <div>
                <p className="text-sm text-slate-500">Management</p>

                <h1 className="text-xl font-semibold text-white">Team</h1>
              </div>
            </div>
          </div>
        </header>

        {/* TEAM CONTENT */}
        <div className="space-y-6 px-4 py-6 sm:px-6 lg:px-8">
          <section>
            {/* PAGE INTRO */}
            <div className="mb-10">
              <p className="text-sm text-blue-400">MUGONEXT</p>

              <h2 className="mt-1 text-3xl font-semibold text-white">
                The People & Intelligence Behind MUGONEXT
              </h2>

              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-500">
                MUGONEXT is founded on a simple vision: make business
                intelligence practical, accessible and actionable, so businesses
                can make better decisions before problems become losses.
              </p>
            </div>

            {/* TEAM CARDS */}
            <div className="grid gap-6 md:grid-cols-3">
              {/* FOUNDER */}
              <div className="rounded-2xl border border-blue-500/20 bg-[#0d1219] p-6 shadow-lg shadow-blue-500/5">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
                  <Brain className="h-6 w-6" />
                </div>

                <h3 className="mt-5 text-xl font-semibold text-white">
                  Ryan Mugo Gathari
                </h3>

                <p className="mt-1 text-sm font-medium text-blue-400">
                  Founder & CEO
                </p>

                <p className="mt-4 text-sm leading-6 text-slate-400">
                  Ryan Mugo Gathari is the founder of MUGONEXT, building an
                  AI-powered business intelligence platform designed to help
                  businesses move from guesswork to informed decision-making.
                </p>

                <p className="mt-4 text-sm leading-6 text-slate-400">
                  His vision is to make advanced forecasting and business
                  intelligence accessible to businesses that traditionally have
                  limited access to sophisticated analytics.
                </p>

                <div className="mt-5 rounded-xl border border-blue-500/10 bg-blue-500/[0.04] p-4">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-400">
                    Founder Vision
                  </p>

                  <p className="mt-2 text-sm font-medium leading-6 text-slate-300">
                    “Turn data into decisions before problems become losses.”
                  </p>
                </div>
              </div>

              {/* AI ENGINE */}
              <div className="rounded-2xl border border-violet-500/20 bg-[#0d1219] p-6 shadow-lg shadow-violet-500/5">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-500/10 text-violet-400">
                  <Brain className="h-6 w-6" />
                </div>

                <h3 className="mt-5 text-xl font-semibold text-white">
                  MUGONEXT Intelligence
                </h3>

                <p className="mt-1 text-sm font-medium text-violet-400">
                  AI Decision Engine
                </p>

                <p className="mt-4 text-sm leading-6 text-slate-400">
                  The intelligence layer of MUGONEXT analyzes business data,
                  identifies patterns and transforms forecasts into practical
                  business recommendations.
                </p>

                <div className="mt-5 rounded-xl border border-violet-500/10 bg-violet-500/[0.04] p-4">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-violet-400">
                    Purpose
                  </p>

                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    Helping businesses understand what their data is saying and
                    what they can do next.
                  </p>
                </div>
              </div>

              {/* TEAM & PARTNERS */}
              <div className="rounded-2xl border border-emerald-500/20 bg-[#0d1219] p-6 shadow-lg shadow-emerald-500/5">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400">
                  <Users className="h-6 w-6" />
                </div>

                <h3 className="mt-5 text-xl font-semibold text-white">
                  Team & Partners
                </h3>

                <p className="mt-1 text-sm font-medium text-emerald-400">
                  Building MUGONEXT
                </p>

                <p className="mt-4 text-sm leading-6 text-slate-400">
                  MUGONEXT is designed to grow with expertise across
                  supply-chain management, business development, finance,
                  technology and business intelligence.
                </p>

                <div className="mt-5 rounded-xl border border-emerald-500/10 bg-emerald-500/[0.04] p-4">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-emerald-400">
                    Building Together
                  </p>

                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    Combining technology and business expertise to solve real
                    operational problems.
                  </p>
                </div>
              </div>
            </div>

            {/* FOUNDER STATEMENT */}
            <div className="mt-8 rounded-2xl border border-white/10 bg-[#0d1219] p-6">
              <div className="flex flex-col gap-5 md:flex-row md:items-start">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
                  <Brain className="h-6 w-6" />
                </div>

                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-400">
                    Why MUGONEXT Exists
                  </p>

                  <h3 className="mt-2 text-xl font-semibold text-white">
                    From Data to Decisions
                  </h3>

                  <p className="mt-3 max-w-4xl text-sm leading-7 text-slate-400">
                    Businesses generate valuable data every day, but having data
                    is not the same as knowing what to do with it. MUGONEXT is
                    being built to bridge that gap by combining forecasting,
                    business intelligence and AI-driven reasoning into one
                    decision-support platform.
                  </p>

                  <p className="mt-4 max-w-4xl text-sm leading-7 text-slate-400">
                    The long-term vision is to give businesses the ability to
                    look ahead, identify potential risks and opportunities, and
                    make informed decisions before those situations become
                    costly problems.
                  </p>
                </div>
              </div>
            </div>

            {/* ACCESS */}
            <div className="mt-8 rounded-2xl border border-blue-500/10 bg-blue-500/[0.04] p-6">
              <div className="flex items-start gap-4">
                <ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-blue-400" />

                <div>
                  <h3 className="font-semibold text-white">Team Access</h3>

                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    Team members can eventually be assigned roles and
                    permissions based on their responsibilities within the
                    business.
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
