import {
  BarChart3,
  Database,
  Home,
  Lightbulb,
  Settings,
  Users,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const navigation = [
  {
    label: "Dashboard",
    to: "/dashboard",
    icon: Home,
  },
  {
    label: "Datasets",
    to: "/datasets",
    icon: Database,
  },
  {
    label: "Forecasts",
    to: "/forecasts",
    icon: BarChart3,
  },
  {
    label: "Recommendations",
    to: "/recommendations",
    icon: Lightbulb,
  },
  {
    label: "Team",
    to: "/team",
    icon: Users,
  },
  {
    label: "Settings",
    to: "/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-white/10 bg-[#0b1017] text-white">
      {/* BRAND */}
      <div className="border-b border-white/10 p-6">
        <NavLink to="/dashboard" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/20">
            <Lightbulb className="h-5 w-5 text-blue-300" />
          </div>

          <div>
            <p className="text-lg font-bold tracking-tight">MUGONEXT</p>

            <p className="text-[9px] uppercase tracking-[0.2em] text-slate-500">
              Intelligent Business AI
            </p>
          </div>
        </NavLink>
      </div>

      {/* NAVIGATION */}
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition",
                  isActive
                    ? "bg-blue-500/10 text-blue-300 ring-1 ring-blue-400/10"
                    : "text-slate-400 hover:bg-white/[0.04] hover:text-white",
                ].join(" ")
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* FOOTER */}
      <div className="border-t border-white/10 p-4">
        <div className="rounded-xl bg-white/[0.03] px-4 py-3">
          <p className="text-xs font-medium text-slate-400">AI Engine</p>

          <div className="mt-1 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />

            <span className="text-xs text-emerald-300">Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
