import {
  Activity,
  AlertCircle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Brain,
  CheckCircle2,
  Database,
  FileSpreadsheet,
  LayoutDashboard,
  Lightbulb,
  LogOut,
  Menu,
  RefreshCw,
  Settings,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Upload,
  Users,
  X,
} from "lucide-react";

import { useCallback, useEffect, useMemo, useState } from "react";
import { NavLink } from "react-router-dom";

import {
  getCompany,
  getUploads,
  getForecasts,
  getRecommendations,
  markRecommendationActioned,
} from "./services/api";

import { useAuth } from "./context/AuthContext";

/* =========================================================
   FORMATTERS
========================================================= */

function formatNumber(value, decimals = 2) {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatCompact(value) {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  const number = Number(value);

  if (Math.abs(number) >= 1_000_000) {
    return `${(number / 1_000_000).toFixed(1)}M`;
  }

  if (Math.abs(number) >= 1_000) {
    return `${(number / 1_000).toFixed(1)}K`;
  }

  return number.toLocaleString(undefined, {
    maximumFractionDigits: 0,
  });
}

function formatPercent(value, decimals = 1) {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${Number(value).toFixed(decimals)}%`;
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

/* =========================================================
   DATA HELPERS
========================================================= */

function getLatest(records = []) {
  if (!Array.isArray(records) || !records.length) {
    return null;
  }

  return [...records].sort((a, b) => {
    const aId = Number(a?.id ?? 0);
    const bId = Number(b?.id ?? 0);

    if (aId !== bId) {
      return bId - aId;
    }

    const aDate = new Date(
      a?.created_at || a?.createdAt || a?.uploaded_at || a?.uploadedAt || 0,
    ).getTime();

    const bDate = new Date(
      b?.created_at || b?.createdAt || b?.uploaded_at || b?.uploadedAt || 0,
    ).getTime();

    return bDate - aDate;
  })[0];
}

function getPredictionValues(forecast) {
  const predictions = forecast?.predictions;

  if (!predictions) {
    return [];
  }

  if (Array.isArray(predictions)) {
    return predictions
      .map((item) => {
        if (typeof item === "number") {
          return item;
        }

        if (typeof item === "object" && item !== null) {
          return Number(
            item.value ??
              item.prediction ??
              item.predicted_value ??
              item.yhat ??
              item.forecast ??
              0,
          );
        }

        return Number(item);
      })
      .filter((value) => Number.isFinite(value));
  }

  if (typeof predictions === "object") {
    return Object.values(predictions)
      .map((item) => {
        if (typeof item === "number") {
          return item;
        }

        if (typeof item === "object" && item !== null) {
          return Number(
            item.value ??
              item.prediction ??
              item.predicted_value ??
              item.yhat ??
              item.forecast ??
              0,
          );
        }

        return Number(item);
      })
      .filter((value) => Number.isFinite(value));
  }

  return [];
}

function getRecommendationItems(response) {
  if (Array.isArray(response)) {
    return response;
  }

  return response?.items || [];
}

function metricIsGood(metric) {
  if (
    metric === null ||
    metric === undefined ||
    metric === "" ||
    Number.isNaN(Number(metric))
  ) {
    return null;
  }

  const numeric = Number(metric);

  if (!Number.isFinite(numeric)) {
    return null;
  }

  return numeric;
}

/* =========================================================
   KPI CARD
========================================================= */

function KpiCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconClass = "bg-blue-500/10 text-blue-400",
  trend,
  trendPositive = true,
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0d1219] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.18)] transition duration-200 hover:border-white/15 hover:bg-[#0f151d]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-400">{title}</p>

          <h3 className="mt-3 text-2xl font-semibold tracking-tight text-white">
            {value}
          </h3>

          {subtitle && (
            <p className="mt-1 truncate text-xs text-slate-500">{subtitle}</p>
          )}
        </div>

        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconClass}`}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>

      {trend !== undefined && trend !== null && (
        <div className="mt-5 flex items-center gap-2 text-xs">
          {trendPositive ? (
            <ArrowUpRight className="h-3.5 w-3.5 text-emerald-400" />
          ) : (
            <ArrowDownRight className="h-3.5 w-3.5 text-rose-400" />
          )}

          <span
            className={trendPositive ? "text-emerald-400" : "text-rose-400"}
          >
            {trend}
          </span>

          <span className="text-slate-600">forecast horizon</span>
        </div>
      )}
    </div>
  );
}

/* =========================================================
   SKELETON
========================================================= */

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-2xl border border-white/10 bg-[#0d1219] p-5">
      <div className="h-4 w-24 rounded bg-white/5" />
      <div className="mt-4 h-8 w-32 rounded bg-white/5" />
      <div className="mt-3 h-3 w-20 rounded bg-white/5" />
    </div>
  );
}

/* =========================================================
   SIDEBAR LINK
========================================================= */

function SidebarLink({ to, icon: Icon, children, end = false }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        [
          "flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition",
          isActive
            ? "bg-blue-500/10 text-blue-400"
            : "text-slate-400 hover:bg-white/5 hover:text-white",
        ].join(" ")
      }
    >
      <Icon className="h-4 w-4 shrink-0" />
      {children}
    </NavLink>
  );
}

/* =========================================================
   DASHBOARD
========================================================= */

export default function Dashboard() {
  const { company: authCompany, logout } = useAuth();

  const [company, setCompany] = useState(authCompany);
  const [uploads, setUploads] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  /* =========================================================
     LOAD DASHBOARD
  ========================================================= */

  const loadDashboard = useCallback(
    async ({ silent = false } = {}) => {
      try {
        if (silent) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        setError("");

        const [
          companyResponse,
          uploadsResponse,
          forecastsResponse,
          recommendationsResponse,
        ] = await Promise.all([
          getCompany(),
          getUploads(),
          getForecasts(),
          getRecommendations(),
        ]);

        setCompany(
          companyResponse?.[0] || companyResponse || authCompany || null,
        );

        const uploadItems = Array.isArray(uploadsResponse)
          ? uploadsResponse
          : uploadsResponse?.items || [];

        setUploads(uploadItems);

        const forecastItems = Array.isArray(forecastsResponse)
          ? forecastsResponse
          : forecastsResponse?.items || [];

        setForecasts(forecastItems);

        const recommendationItems = getRecommendationItems(
          recommendationsResponse,
        );

        setRecommendations(recommendationItems);

        console.log("========== MUGONEXT DASHBOARD ==========");

        console.log("Forecasts:", forecastItems);

        console.log("Recommendations:", recommendationItems);

        console.log(
          "Recommendation statuses:",
          recommendationItems.map((item) => ({
            id: item?.id,
            title: item?.title,
            status: item?.status,
            forecast_id: item?.forecast_id,
          })),
        );

        console.log("========================================");
      } catch (err) {
        console.error("Dashboard loading error:", err);

        setError(
          err?.message ||
            "Unable to load dashboard data from the MUGONEXT backend.",
        );
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [authCompany],
  );

  /* =========================================================
     INITIAL LOAD + AUTO REFRESH
  ========================================================= */

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(() => {
      loadDashboard({ silent: true });
    }, 60_000);

    return () => clearInterval(interval);
  }, [loadDashboard]);

  /* =========================================================
     DERIVED DATA
  ========================================================= */

  const latestForecast = useMemo(() => getLatest(forecasts), [forecasts]);

  const latestUpload = useMemo(() => getLatest(uploads), [uploads]);

  const forecastValues = useMemo(
    () => getPredictionValues(latestForecast),
    [latestForecast],
  );

  /* =========================================================
     ACTIVE RECOMMENDATIONS
     
     Used for the KPI and active count.
     
     Actioned recommendations are NOT counted here.
  ========================================================= */

  const activeRecommendations = useMemo(() => {
    return recommendations.filter((item) => {
      const status = String(item?.status || "active").toLowerCase();

      return !["actioned", "archived", "completed", "dismissed"].includes(
        status,
      );
    });
  }, [recommendations]);

  /* =========================================================
     RECENT RECOMMENDATIONS
     
     IMPORTANT:
     This contains BOTH active and actioned recommendations.
     
     This prevents the dashboard section from becoming empty
     after the user marks all recommendations as actioned.
  ========================================================= */

  const recentRecommendations = useMemo(() => {
    return [...recommendations]
      .sort((a, b) => {
        const aId = Number(a?.id ?? 0);
        const bId = Number(b?.id ?? 0);

        if (aId !== bId) {
          return bId - aId;
        }

        const dateA = new Date(
          a?.created_at || a?.createdAt || a?.updated_at || a?.updatedAt || 0,
        ).getTime();

        const dateB = new Date(
          b?.created_at || b?.createdAt || b?.updated_at || b?.updatedAt || 0,
        ).getTime();

        return dateB - dateA;
      })
      .slice(0, 5);
  }, [recommendations]);

  /* =========================================================
     MATCH AI EXPLANATION TO SAME FORECAST
  ========================================================= */

  const latestForecastRecommendation = useMemo(() => {
    if (!latestForecast?.id || !recommendations.length) {
      return null;
    }

    return (
      recommendations.find(
        (recommendation) =>
          Number(recommendation?.forecast_id) === Number(latestForecast.id),
      ) || null
    );
  }, [latestForecast, recommendations]);

  /* =========================================================
     COMPANY
  ========================================================= */

  const companyName =
    company?.name ||
    company?.company_name ||
    company?.business_name ||
    "MUGONEXT Company";

  /* =========================================================
     FORECAST METRICS
  ========================================================= */

  const forecastModel =
    latestForecast?.forecast_model || latestForecast?.model || "Auto";

  const confidence = metricIsGood(
    latestForecast?.confidence_score ??
      latestForecast?.confidence ??
      latestForecast?.forecast_confidence,
  );

  const mape = metricIsGood(latestForecast?.mape);

  const rmse = metricIsGood(latestForecast?.rmse);

  const mae = metricIsGood(latestForecast?.mae);

  const rSquared = metricIsGood(
    latestForecast?.r_squared ??
      latestForecast?.r2 ??
      latestForecast?.r_squared_score,
  );

  const accuracy = metricIsGood(
    latestForecast?.accuracy_score ?? (mape !== null ? 100 - mape : null),
  );

  const dataQuality = metricIsGood(
    latestUpload?.quality_score ??
      latestUpload?.data_quality_score ??
      latestUpload?.quality ??
      latestUpload?.validation_score,
  );

  /* =========================================================
     FORECAST GROWTH
  ========================================================= */

  const firstPrediction = forecastValues.length > 0 ? forecastValues[0] : null;

  const lastPrediction =
    forecastValues.length > 0
      ? forecastValues[forecastValues.length - 1]
      : null;

  const forecastGrowth =
    firstPrediction !== null &&
    firstPrediction !== undefined &&
    lastPrediction !== null &&
    lastPrediction !== undefined &&
    firstPrediction !== 0
      ? ((lastPrediction - firstPrediction) / firstPrediction) * 100
      : null;

  /* =========================================================
     CHART
  ========================================================= */

  const chartPoints = useMemo(() => {
    if (!forecastValues.length) {
      return [];
    }

    const width = 800;
    const height = 300;
    const paddingX = 25;
    const paddingY = 25;

    const min = Math.min(...forecastValues);
    const max = Math.max(...forecastValues);
    const range = max - min || 1;

    return forecastValues.map((value, index) => {
      const x =
        forecastValues.length === 1
          ? width / 2
          : paddingX +
            (index / (forecastValues.length - 1)) * (width - paddingX * 2);

      const y =
        height - paddingY - ((value - min) / range) * (height - paddingY * 2);

      return {
        x,
        y,
        value,
        index,
      };
    });
  }, [forecastValues]);

  const chartPolyline = chartPoints
    .map((point) => `${point.x},${point.y}`)
    .join(" ");

  const chartAreaPath =
    chartPoints.length > 0
      ? [
          `M ${chartPoints[0].x} ${chartPoints[0].y}`,

          ...chartPoints.slice(1).map((point) => `L ${point.x} ${point.y}`),

          `L ${chartPoints[chartPoints.length - 1].x} 285`,

          `L ${chartPoints[0].x} 285`,

          "Z",
        ].join(" ")
      : "";

  /* =========================================================
     RECOMMENDATION ACTION
  ========================================================= */

  async function handleActionRecommendation(recommendationId) {
    if (!recommendationId) {
      return;
    }

    try {
      setError("");

      await markRecommendationActioned({
        recommendationId,
        actionTaken: true,
      });

      /*
       * Reload the dashboard so:
       *
       * Active count decreases
       * Actioned count/status updates
       * Recent recommendation remains visible
       */

      await loadDashboard({
        silent: true,
      });
    } catch (err) {
      console.error("Recommendation action failed:", err);

      setError(err?.message || "Unable to update recommendation.");
    }
  }

  /* =========================================================
     NAVIGATION
  ========================================================= */

  function closeMobileSidebar() {
    setMobileSidebarOpen(false);
  }

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <div className="min-h-screen bg-[#0b0f14] text-slate-200">
      {/* MOBILE OVERLAY */}

      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={closeMobileSidebar}
        />
      )}

      {/* =====================================================
          SIDEBAR
      ===================================================== */}

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
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-400 transition hover:bg-rose-500/10 hover:text-rose-400"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* =====================================================
          MAIN
      ===================================================== */}

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
                <p className="text-sm text-slate-500">Overview</p>

                <h1 className="text-xl font-semibold text-white">
                  Business Intelligence Dashboard
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() =>
                  loadDashboard({
                    silent: true,
                  })
                }
                disabled={refreshing}
                className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCw
                  className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
                />

                <span className="hidden sm:inline">Refresh</span>
              </button>

              <div className="hidden items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-3 py-2 sm:flex">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />

                <span className="text-xs font-medium text-emerald-400">
                  AI Engine Online
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* ===================================================
            CONTENT
        =================================================== */}

        <div className="space-y-6 px-4 py-6 sm:px-6 lg:px-8">
          {/* ERROR */}

          {error && (
            <div className="flex items-start gap-3 rounded-2xl border border-rose-500/20 bg-rose-500/5 p-4">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-rose-400" />

              <div className="min-w-0">
                <p className="text-sm font-medium text-rose-300">
                  Dashboard data error
                </p>

                <p className="mt-1 text-sm text-rose-300/70">{error}</p>
              </div>
            </div>
          )}

          {/* WELCOME */}

          <section>
            <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
              <div>
                <p className="text-sm text-slate-500">Welcome back</p>

                <h2 className="mt-1 text-2xl font-semibold text-white">
                  {companyName}
                </h2>
              </div>

              <div className="text-xs text-slate-500">
                Latest forecast{" "}
                {latestForecast?.created_at || latestForecast?.createdAt
                  ? formatDate(
                      latestForecast.created_at || latestForecast.createdAt,
                    )
                  : "—"}
              </div>
            </div>

            {/* KPI GRID */}

            {loading ? (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <KpiCard
                  title="Forecasted Value"
                  value={
                    lastPrediction !== null
                      ? formatCompact(lastPrediction)
                      : "—"
                  }
                  subtitle={
                    latestForecast
                      ? `${
                          forecastValues.length ||
                          latestForecast.forecast_periods ||
                          0
                        } forecast periods`
                      : "No forecast yet"
                  }
                  icon={TrendingUp}
                  trend={
                    forecastGrowth !== null
                      ? `${
                          forecastGrowth >= 0 ? "+" : ""
                        }${forecastGrowth.toFixed(2)}%`
                      : null
                  }
                  trendPositive={forecastGrowth === null || forecastGrowth >= 0}
                />

                <KpiCard
                  title="Forecast Confidence"
                  value={
                    confidence !== null ? formatPercent(confidence, 1) : "—"
                  }
                  subtitle={
                    latestForecast ? String(forecastModel) : "No forecast yet"
                  }
                  icon={Target}
                  iconClass="bg-violet-500/10 text-violet-400"
                />

                <KpiCard
                  title="Active Recommendations"
                  value={activeRecommendations.length}
                  subtitle="AI-generated business insights"
                  icon={Lightbulb}
                  iconClass="bg-amber-500/10 text-amber-400"
                />

                <KpiCard
                  title="Data Quality"
                  value={
                    dataQuality !== null ? formatPercent(dataQuality, 0) : "—"
                  }
                  subtitle={
                    latestUpload
                      ? latestUpload.dataset_name ||
                        latestUpload.filename ||
                        "Latest dataset"
                      : "No dataset uploaded"
                  }
                  icon={Database}
                  iconClass="bg-emerald-500/10 text-emerald-400"
                />
              </div>
            )}
          </section>

          {/* =================================================
              FORECAST + AI INTELLIGENCE
          ================================================= */}

          <section className="grid gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,0.85fr)]">
            {/* FORECAST CARD */}

            <div className="rounded-2xl border border-white/10 bg-[#0d1219] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.18)] sm:p-6">
              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-blue-400" />

                    <p className="text-sm font-medium text-slate-400">
                      Forecast Trend
                    </p>
                  </div>

                  <div className="mt-2 flex items-baseline gap-3">
                    <h3 className="text-2xl font-semibold text-white">
                      {lastPrediction !== null
                        ? formatCompact(lastPrediction)
                        : "No forecast"}
                    </h3>

                    {forecastGrowth !== null && (
                      <span
                        className={`flex items-center gap-1 text-xs font-medium ${
                          forecastGrowth >= 0
                            ? "text-emerald-400"
                            : "text-rose-400"
                        }`}
                      >
                        {forecastGrowth >= 0 ? (
                          <ArrowUpRight className="h-3.5 w-3.5" />
                        ) : (
                          <ArrowDownRight className="h-3.5 w-3.5" />
                        )}
                        {forecastGrowth >= 0 ? "+" : ""}
                        {forecastGrowth.toFixed(2)}%
                      </span>
                    )}
                  </div>

                  <p className="mt-1 text-xs text-slate-500">
                    Projected business performance
                  </p>
                </div>

                <div className="flex items-center gap-2 rounded-xl bg-blue-500/5 px-3 py-2 text-xs text-blue-300">
                  <Sparkles className="h-3.5 w-3.5" />

                  {forecastModel}
                </div>
              </div>

              {/* CHART */}

              <div className="mt-6 overflow-hidden rounded-xl border border-white/5 bg-[#0a0f15]">
                {chartPoints.length ? (
                  <div className="h-[330px] w-full">
                    <svg
                      viewBox="0 0 800 300"
                      className="h-full w-full"
                      preserveAspectRatio="none"
                    >
                      <defs>
                        <linearGradient
                          id="forecastFill"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#3b82f6"
                            stopOpacity="0.25"
                          />

                          <stop
                            offset="100%"
                            stopColor="#3b82f6"
                            stopOpacity="0"
                          />
                        </linearGradient>
                      </defs>

                      {[70, 140, 210, 280].map((y) => (
                        <line
                          key={y}
                          x1="20"
                          y1={y}
                          x2="780"
                          y2={y}
                          stroke="rgba(255,255,255,0.06)"
                          strokeWidth="1"
                        />
                      ))}

                      {chartAreaPath && (
                        <path d={chartAreaPath} fill="url(#forecastFill)" />
                      )}

                      {chartPolyline && (
                        <polyline
                          points={chartPolyline}
                          fill="none"
                          stroke="#60a5fa"
                          strokeWidth="4"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      )}

                      {chartPoints.map((point) => (
                        <circle
                          key={point.index}
                          cx={point.x}
                          cy={point.y}
                          r="4"
                          fill="#0b0f14"
                          stroke="#60a5fa"
                          strokeWidth="2"
                        />
                      ))}
                    </svg>
                  </div>
                ) : (
                  <div className="flex h-[330px] flex-col items-center justify-center px-6 text-center">
                    <BarChart3 className="h-10 w-10 text-slate-700" />

                    <p className="mt-4 text-sm font-medium text-slate-400">
                      No forecast data available
                    </p>

                    <p className="mt-1 max-w-sm text-xs leading-5 text-slate-600">
                      Upload a dataset and create a forecast to see your
                      projected business performance here.
                    </p>
                  </div>
                )}
              </div>

              {/* METRICS */}

              <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-xl border border-white/5 bg-white/[0.02] p-3">
                  <p className="text-[11px] text-slate-600">MAE</p>

                  <p className="mt-1 text-sm font-semibold text-white">
                    {formatNumber(mae)}
                  </p>
                </div>

                <div className="rounded-xl border border-white/5 bg-white/[0.02] p-3">
                  <p className="text-[11px] text-slate-600">RMSE</p>

                  <p className="mt-1 text-sm font-semibold text-white">
                    {formatNumber(rmse)}
                  </p>
                </div>

                <div className="rounded-xl border border-white/5 bg-white/[0.02] p-3">
                  <p className="text-[11px] text-slate-600">MAPE</p>

                  <p className="mt-1 text-sm font-semibold text-white">
                    {formatPercent(mape, 2)}
                  </p>
                </div>

                <div className="rounded-xl border border-white/5 bg-white/[0.02] p-3">
                  <p className="text-[11px] text-slate-600">R²</p>

                  <p className="mt-1 text-sm font-semibold text-white">
                    {rSquared !== null ? rSquared.toFixed(4) : "—"}
                  </p>
                </div>
              </div>
            </div>

            {/* AI INTELLIGENCE */}

            <div className="rounded-2xl border border-violet-500/15 bg-gradient-to-br from-violet-500/[0.08] to-[#0d1219] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.18)] sm:p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/10">
                    <Brain className="h-4 w-4 text-violet-400" />
                  </div>

                  <div>
                    <p className="text-sm font-medium text-white">
                      AI Intelligence
                    </p>

                    <p className="text-[11px] text-slate-500">
                      MUGONEXT analysis
                    </p>
                  </div>
                </div>

                <Sparkles className="h-4 w-4 text-violet-400" />
              </div>

              <div className="mt-6">
                {latestForecast ? (
                  <>
                    <div className="rounded-xl border border-white/10 bg-black/10 p-4">
                      <p className="text-sm leading-6 text-slate-300">
                        {latestForecastRecommendation?.ai_explanation ||
                          latestForecastRecommendation?.reasoning ||
                          latestForecastRecommendation?.recommendation ||
                          (forecastGrowth !== null
                            ? `The latest forecast projects ${
                                forecastGrowth >= 0
                                  ? "continued growth"
                                  : "a decline"
                              } of approximately ${Math.abs(
                                forecastGrowth,
                              ).toFixed(2)}% across the forecast horizon.`
                            : "Your latest forecasting model has been processed successfully.")}
                      </p>
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-3">
                      <div className="rounded-xl border border-white/10 bg-black/10 p-3">
                        <p className="text-[11px] text-slate-600">Accuracy</p>

                        <p className="mt-1 text-lg font-semibold text-white">
                          {accuracy !== null ? formatPercent(accuracy, 2) : "—"}
                        </p>
                      </div>

                      <div className="rounded-xl border border-white/10 bg-black/10 p-3">
                        <p className="text-[11px] text-slate-600">Confidence</p>

                        <p className="mt-1 text-lg font-semibold text-white">
                          {confidence !== null
                            ? formatPercent(confidence, 1)
                            : "—"}
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center gap-2 text-xs text-emerald-400">
                      <CheckCircle2 className="h-4 w-4" />
                      Forecast successfully processed
                    </div>
                  </>
                ) : (
                  <div className="rounded-xl border border-white/10 bg-black/10 p-5 text-center">
                    <Activity className="mx-auto h-8 w-8 text-slate-700" />

                    <p className="mt-3 text-sm text-slate-400">
                      AI insights will appear here once a forecast exists.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* =================================================
              RECOMMENDATIONS + DATA
          ================================================= */}

          <section className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.8fr)]">
            {/* =================================================
                RECOMMENDATIONS
            ================================================= */}

            <div className="rounded-2xl border border-white/10 bg-[#0d1219] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.18)] sm:p-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-400">
                    AI Recommendations
                  </p>

                  <p className="mt-1 text-xs text-slate-600">
                    Actions generated from your business forecasts
                  </p>
                </div>

                <div className="rounded-lg bg-amber-500/10 px-2.5 py-1.5 text-xs font-medium text-amber-400">
                  {activeRecommendations.length} active
                </div>
              </div>

              {/* =================================================
                  IMPORTANT:
                  SHOW RECENT RECOMMENDATIONS, NOT ONLY ACTIVE
              ================================================= */}

              <div className="mt-5 space-y-3">
                {loading ? (
                  <>
                    <div className="h-24 animate-pulse rounded-xl bg-white/[0.03]" />

                    <div className="h-24 animate-pulse rounded-xl bg-white/[0.03]" />

                    <div className="h-24 animate-pulse rounded-xl bg-white/[0.03]" />
                  </>
                ) : recentRecommendations.length ? (
                  recentRecommendations.map((recommendation, index) => {
                    const status = String(
                      recommendation?.status || "active",
                    ).toLowerCase();

                    const isActioned = ["actioned", "completed"].includes(
                      status,
                    );

                    const isArchived = status === "archived";

                    const priority = String(
                      recommendation?.priority || "medium",
                    ).toLowerCase();

                    const priorityClass =
                      priority === "high" || priority === "critical"
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/10"
                        : priority === "low"
                          ? "bg-slate-500/10 text-slate-400 border-slate-500/10"
                          : "bg-amber-500/10 text-amber-400 border-amber-500/10";

                    return (
                      <div
                        key={recommendation?.id ?? index}
                        className={`group rounded-xl border p-4 transition ${
                          isActioned
                            ? "border-emerald-500/10 bg-emerald-500/[0.025]"
                            : isArchived
                              ? "border-white/5 bg-white/[0.01] opacity-70"
                              : "border-white/5 bg-white/[0.02] hover:border-white/10 hover:bg-white/[0.035]"
                        }`}
                      >
                        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                          {/* RECOMMENDATION CONTENT */}

                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-2">
                              <span
                                className={`rounded-md border px-2 py-1 text-[10px] font-semibold uppercase tracking-wide ${priorityClass}`}
                              >
                                {priority}
                              </span>

                              {recommendation?.category && (
                                <span className="text-[10px] uppercase tracking-wide text-slate-600">
                                  {String(recommendation.category).replaceAll(
                                    "_",
                                    " ",
                                  )}
                                </span>
                              )}

                              {/* STATUS */}

                              {isActioned ? (
                                <span className="flex items-center gap-1 rounded-md bg-emerald-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-emerald-400">
                                  <CheckCircle2 className="h-3 w-3" />
                                  Actioned
                                </span>
                              ) : isArchived ? (
                                <span className="rounded-md bg-slate-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                                  Archived
                                </span>
                              ) : (
                                <span className="rounded-md bg-blue-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-blue-400">
                                  Active
                                </span>
                              )}
                            </div>

                            <h4 className="mt-2 text-sm font-semibold text-white">
                              {recommendation?.title ||
                                "Business recommendation"}
                            </h4>

                            <p className="mt-1 text-sm leading-6 text-slate-500">
                              {recommendation?.recommendation ||
                                recommendation?.reasoning ||
                                recommendation?.suggested_action ||
                                "MUGONEXT has generated a recommendation from your latest business forecast."}
                            </p>

                            {/* EXPECTED OUTCOME */}

                            {recommendation?.expected_outcome && (
                              <div className="mt-3 rounded-lg border border-white/5 bg-black/10 px-3 py-2">
                                <p className="text-[10px] uppercase tracking-wide text-slate-600">
                                  Expected outcome
                                </p>

                                <p className="mt-1 text-xs leading-5 text-slate-400">
                                  {recommendation.expected_outcome}
                                </p>
                              </div>
                            )}
                          </div>

                          {/* ACTION BUTTON */}

                          <div className="shrink-0">
                            {isActioned ? (
                              <div className="flex items-center gap-1.5 rounded-lg bg-emerald-500/10 px-3 py-2 text-xs font-medium text-emerald-400">
                                <CheckCircle2 className="h-3.5 w-3.5" />
                                Actioned
                              </div>
                            ) : isArchived ? (
                              <div className="rounded-lg bg-slate-500/10 px-3 py-2 text-xs font-medium text-slate-500">
                                Archived
                              </div>
                            ) : (
                              <button
                                type="button"
                                onClick={() =>
                                  handleActionRecommendation(recommendation.id)
                                }
                                className="rounded-lg border border-white/10 px-3 py-2 text-xs font-medium text-slate-300 transition hover:bg-emerald-500/10 hover:text-emerald-400"
                              >
                                Mark done
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="rounded-xl border border-dashed border-white/10 p-8 text-center">
                    <Lightbulb className="mx-auto h-8 w-8 text-slate-700" />

                    <p className="mt-3 text-sm text-slate-400">
                      No AI recommendations yet.
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-600">
                      Create a forecast and MUGONEXT will generate actionable
                      business intelligence here.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* =================================================
                RIGHT COLUMN
            ================================================= */}

            <div className="space-y-6">
              {/* LATEST DATASET */}

              <div className="rounded-2xl border border-white/10 bg-[#0d1219] p-5 shadow-[0_12px_40px_rgba(0,0,0,0.18)]">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10">
                    <Database className="h-4 w-4 text-emerald-400" />
                  </div>

                  <div>
                    <p className="text-sm font-medium text-white">
                      Latest Dataset
                    </p>

                    <p className="text-xs text-slate-600">
                      Current data source
                    </p>
                  </div>
                </div>

                <div className="mt-5 space-y-4">
                  <div>
                    <p className="text-[11px] text-slate-600">Dataset</p>

                    <p className="mt-1 truncate text-sm font-medium text-slate-200">
                      {latestUpload?.dataset_name ||
                        latestUpload?.filename ||
                        "No dataset uploaded"}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-[11px] text-slate-600">Rows</p>

                      <p className="mt-1 text-sm font-semibold text-white">
                        {formatNumber(
                          latestUpload?.row_count ??
                            latestUpload?.rows ??
                            latestUpload?.record_count ??
                            null,
                          0,
                        )}
                      </p>
                    </div>

                    <div>
                      <p className="text-[11px] text-slate-600">Columns</p>

                      <p className="mt-1 text-sm font-semibold text-white">
                        {formatNumber(
                          latestUpload?.column_count ??
                            latestUpload?.columns ??
                            null,
                          0,
                        )}
                      </p>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between">
                      <p className="text-[11px] text-slate-600">Data quality</p>

                      <span className="text-xs font-medium text-emerald-400">
                        {dataQuality !== null
                          ? formatPercent(dataQuality, 0)
                          : "—"}
                      </span>
                    </div>

                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/5">
                      <div
                        className="h-full rounded-full bg-emerald-400 transition-all duration-500"
                        style={{
                          width: `${Math.max(
                            0,
                            Math.min(dataQuality ?? 0, 100),
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* PIPELINE */}

              <div className="rounded-2xl border border-blue-500/10 bg-blue-500/[0.04] p-5">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-500/10">
                    <Upload className="h-4 w-4 text-blue-400" />
                  </div>

                  <div>
                    <p className="text-sm font-medium text-white">
                      MUGONEXT Decision Pipeline
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      Upload → Validate → Forecast → Analyze → Recommend → Act
                    </p>
                  </div>
                </div>

                <div className="mt-5 flex items-center gap-2 text-xs text-blue-300">
                  <CheckCircle2 className="h-4 w-4" />
                  Backend connected successfully
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
