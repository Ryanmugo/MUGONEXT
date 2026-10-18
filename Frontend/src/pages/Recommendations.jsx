import { useCallback, useEffect, useMemo, useState } from "react";

import {
  Archive,
  CheckCircle2,
  Clock3,
  Lightbulb,
  RefreshCw,
  Sparkles,
  Target,
  TrendingUp,
  AlertTriangle,
  ShieldCheck,
} from "lucide-react";

import {
  getRecommendations,
  markRecommendationActioned,
  archiveRecommendation,
} from "../services/api";
import Sidebar from "../components/Sidebar";

/* =========================================================
   RESPONSE HELPERS
========================================================= */

function getItems(response) {
  if (Array.isArray(response)) {
    return response;
  }

  if (Array.isArray(response?.items)) {
    return response.items;
  }

  if (Array.isArray(response?.data)) {
    return response.data;
  }

  if (Array.isArray(response?.recommendations)) {
    return response.recommendations;
  }

  return [];
}

/* =========================================================
   FORMATTERS
========================================================= */

function formatNumber(value, decimals = 2) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return number.toFixed(decimals);
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString([], {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/* =========================================================
   PRIORITY
========================================================= */

function getPriorityClasses(priority) {
  switch (String(priority || "").toLowerCase()) {
    case "critical":
      return "border-red-400/20 bg-red-500/10 text-red-300";

    case "high":
      return "border-orange-400/20 bg-orange-500/10 text-orange-300";

    case "medium":
      return "border-yellow-400/20 bg-yellow-500/10 text-yellow-300";

    case "low":
      return "border-blue-400/20 bg-blue-500/10 text-blue-300";

    default:
      return "border-white/10 bg-white/5 text-slate-300";
  }
}

function getPriorityIcon(priority) {
  switch (String(priority || "").toLowerCase()) {
    case "critical":
    case "high":
      return AlertTriangle;

    default:
      return ShieldCheck;
  }
}

/* =========================================================
   METRIC CARD
========================================================= */

function MetricCard({ label, value, suffix = "", icon: Icon }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-slate-500">
          {label}
        </p>

        {Icon ? <Icon className="h-4 w-4 text-emerald-300/80" /> : null}
      </div>

      <p className="mt-3 text-2xl font-semibold text-white">
        {value}
        {suffix}
      </p>
    </div>
  );
}

/* =========================================================
   RECOMMENDATION CARD
========================================================= */

function RecommendationCard({
  recommendation,
  onAction,
  onArchive,
  actionLoading,
}) {
  const PriorityIcon = getPriorityIcon(recommendation.priority);

  const confidence =
    recommendation.confidence_score ?? recommendation.confidence ?? null;

  const impact = recommendation.impact_score ?? recommendation.impact ?? null;

  const priorityScore =
    recommendation.priority_score ?? recommendation.priorityScore ?? null;

  const isActioned = Boolean(
    recommendation.action_taken ??
    recommendation.actioned ??
    recommendation.is_actioned,
  );

  const isArchived = Boolean(
    recommendation.archived ??
    recommendation.is_archived ??
    recommendation.archived_at,
  );

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-2xl shadow-black/10">
      {/* Header */}
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-500/10 ring-1 ring-emerald-400/20">
            <Lightbulb className="h-6 w-6 text-emerald-300" />
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xl font-semibold text-white">
                {recommendation.title || "Business recommendation"}
              </h2>

              {recommendation.priority ? (
                <span
                  className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${getPriorityClasses(
                    recommendation.priority,
                  )}`}
                >
                  <PriorityIcon className="h-3.5 w-3.5" />
                  {recommendation.priority}
                </span>
              ) : null}
            </div>

            <p className="mt-1 text-sm capitalize text-slate-500">
              {recommendation.category
                ? String(recommendation.category).replaceAll("_", " ")
                : "Decision intelligence"}
            </p>
          </div>
        </div>

        <div
          className={`inline-flex items-center gap-2 self-start rounded-full border px-3 py-1.5 text-xs ${
            isActioned
              ? "border-emerald-400/20 bg-emerald-500/10 text-emerald-300"
              : isArchived
                ? "border-slate-400/20 bg-slate-500/10 text-slate-400"
                : "border-white/10 bg-white/5 text-slate-400"
          }`}
        >
          <CheckCircle2 className="h-3.5 w-3.5" />

          {isActioned ? "Actioned" : isArchived ? "Archived" : "Pending action"}
        </div>
      </div>

      {/* Main recommendation */}
      <div className="mt-7 rounded-2xl border border-emerald-400/10 bg-emerald-500/[0.04] p-5">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-emerald-300" />

          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-300">
            MUGONEXT decision
          </p>
        </div>

        <p className="mt-3 text-base leading-7 text-slate-200">
          {recommendation.recommendation ||
            recommendation.message ||
            recommendation.description ||
            "No recommendation text available."}
        </p>
      </div>

      {/* Metrics */}
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <MetricCard
          label="Confidence"
          value={formatNumber(confidence)}
          suffix={confidence !== null ? "/100" : ""}
          icon={ShieldCheck}
        />

        <MetricCard
          label="Impact"
          value={formatNumber(impact)}
          suffix={impact !== null ? "/100" : ""}
          icon={Target}
        />

        <MetricCard
          label="Priority score"
          value={formatNumber(priorityScore)}
          suffix={priorityScore !== null ? "/100" : ""}
          icon={TrendingUp}
        />
      </div>

      {/* Reasoning */}
      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-[#0a0f15] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Why MUGONEXT generated this
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-300">
            {recommendation.reasoning ||
              recommendation.ai_explanation ||
              recommendation.explanation ||
              "No reasoning available."}
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#0a0f15] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Suggested action
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-300">
            {recommendation.suggested_action ||
              recommendation.action ||
              "No suggested action available."}
          </p>
        </div>
      </div>

      {/* Expected outcome */}
      {recommendation.expected_outcome ? (
        <div className="mt-5 rounded-2xl border border-white/10 bg-[#0a0f15] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Expected business outcome
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-300">
            {recommendation.expected_outcome}
          </p>
        </div>
      ) : null}

      {/* Forecast source */}
      <div className="mt-6 flex flex-col gap-3 border-t border-white/10 pt-5 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
          <span>
            Forecast{" "}
            <strong className="text-slate-300">
              #{recommendation.forecast_id ?? "—"}
            </strong>
          </span>

          <span>
            Dataset{" "}
            <strong className="text-slate-300">
              #{recommendation.upload_id ?? "—"}
            </strong>
          </span>

          <span>
            Created{" "}
            <strong className="text-slate-300">
              {formatDate(recommendation.created_at)}
            </strong>
          </span>
        </div>

        <span className="inline-flex items-center gap-1.5">
          <Clock3 className="h-3.5 w-3.5" />

          {recommendation.ai_provider === "local"
            ? "MUGONEXT Decision Engine"
            : recommendation.ai_provider || "MUGONEXT AI"}
        </span>
      </div>

      {/* Actions */}
      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        {!isActioned && !isArchived ? (
          <button
            type="button"
            onClick={() => onAction(recommendation.id)}
            disabled={actionLoading}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <CheckCircle2 className="h-4 w-4" />

            {actionLoading ? "Updating..." : "Mark as actioned"}
          </button>
        ) : null}

        {!isArchived ? (
          <button
            type="button"
            onClick={() => onArchive(recommendation.id)}
            disabled={actionLoading}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Archive className="h-4 w-4" />

            {actionLoading ? "Updating..." : "Archive"}
          </button>
        ) : null}
      </div>
    </div>
  );
}

/* =========================================================
   MAIN PAGE
========================================================= */

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(null);

  /* =======================================================
     LOAD RECOMMENDATIONS
  ======================================================= */

  const loadRecommendations = useCallback(async (showRefresh = false) => {
    try {
      setError("");

      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const response = await getRecommendations();

      const items = getItems(response);

      setRecommendations(items);
    } catch (err) {
      console.error("MUGONEXT recommendations error:", err);

      setError(
        err?.message || "Unable to load recommendations. Please try again.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  /* =======================================================
     INITIAL LOAD
  ======================================================= */

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  /* =======================================================
     MARK ACTIONED
  ======================================================= */

  async function handleAction(recommendationId) {
    try {
      setActionLoading(recommendationId);
      setError("");

      await markRecommendationActioned(recommendationId);

      await loadRecommendations(true);
    } catch (err) {
      console.error("MUGONEXT recommendation action error:", err);

      setError(
        err?.message || "Unable to mark the recommendation as actioned.",
      );
    } finally {
      setActionLoading(null);
    }
  }

  /* =======================================================
     ARCHIVE
  ======================================================= */

  async function handleArchive(recommendationId) {
    try {
      setActionLoading(recommendationId);
      setError("");

      await archiveRecommendation(recommendationId);

      await loadRecommendations(true);
    } catch (err) {
      console.error("MUGONEXT recommendation archive error:", err);

      setError(err?.message || "Unable to archive the recommendation.");
    } finally {
      setActionLoading(null);
    }
  }

  /* =======================================================
     ACTIVE RECOMMENDATIONS
  ======================================================= */

  const activeRecommendations = useMemo(() => {
    return recommendations.filter((item) => {
      const actioned = Boolean(
        item.action_taken ?? item.actioned ?? item.is_actioned,
      );

      const archived = Boolean(
        item.archived ?? item.is_archived ?? item.archived_at,
      );

      return !actioned && !archived;
    });
  }, [recommendations]);

  /* =======================================================
     SUMMARY
  ======================================================= */

  const summary = useMemo(() => {
    const totalActive = activeRecommendations.length;

    const highPriority = activeRecommendations.filter((item) =>
      ["critical", "high"].includes(String(item.priority || "").toLowerCase()),
    ).length;

    const actioned = recommendations.filter((item) =>
      Boolean(item.action_taken ?? item.actioned ?? item.is_actioned),
    ).length;

    const averageConfidenceValues = activeRecommendations
      .map((item) => Number(item.confidence_score ?? item.confidence ?? NaN))
      .filter((value) => Number.isFinite(value));

    const averageConfidence =
      averageConfidenceValues.length > 0
        ? averageConfidenceValues.reduce((sum, value) => sum + value, 0) /
          averageConfidenceValues.length
        : null;

    return {
      totalActive,
      highPriority,
      actioned,
      averageConfidence,
    };
  }, [recommendations, activeRecommendations]);

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <div className="min-h-screen bg-[#0b0f14] text-white">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content */}
        <main className="min-w-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
            {/* Page Header */}
            <div className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-500/10 ring-1 ring-emerald-400/20">
                    <Lightbulb className="h-5 w-5 text-emerald-300" />
                  </div>

                  <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                      AI Recommendations
                    </h1>

                    <p className="mt-1 text-sm text-slate-500">
                      Turn forecasts into actionable business decisions.
                    </p>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => loadRecommendations(true)}
                disabled={refreshing}
                className="inline-flex items-center justify-center gap-2 self-start rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-50 lg:self-auto"
              >
                <RefreshCw
                  className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
                />

                {refreshing ? "Refreshing..." : "Refresh"}
              </button>
            </div>

            {/* Error */}
            {error ? (
              <div className="mb-6 rounded-2xl border border-red-400/20 bg-red-500/10 px-5 py-4 text-sm text-red-300">
                {error}
              </div>
            ) : null}

            {/* Summary */}
            <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <MetricCard
                label="Active recommendations"
                value={summary.totalActive}
                icon={Lightbulb}
              />

              <MetricCard
                label="High priority"
                value={summary.highPriority}
                icon={AlertTriangle}
              />

              <MetricCard
                label="Actioned"
                value={summary.actioned}
                icon={CheckCircle2}
              />

              <MetricCard
                label="Avg confidence"
                value={
                  summary.averageConfidence !== null
                    ? formatNumber(summary.averageConfidence)
                    : "—"
                }
                suffix={summary.averageConfidence !== null ? "/100" : ""}
                icon={ShieldCheck}
              />
            </div>

            {/* Main grid */}
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Recommendations */}
              <div className="space-y-5 lg:col-span-2">
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <h2 className="text-lg font-semibold">
                        Decision intelligence
                      </h2>

                      <p className="mt-1 text-sm text-slate-500">
                        MUGONEXT recommendations generated from forecast
                        intelligence.
                      </p>
                    </div>

                    <Sparkles className="h-5 w-5 text-emerald-300" />
                  </div>
                </div>

                {loading ? (
                  <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-10 text-center">
                    <div className="mx-auto h-9 w-9 animate-spin rounded-full border-2 border-white/10 border-t-emerald-300" />

                    <p className="mt-4 text-sm text-slate-500">
                      Loading MUGONEXT recommendations...
                    </p>
                  </div>
                ) : activeRecommendations.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-emerald-400/20 bg-emerald-500/[0.03] px-6 py-14 text-center">
                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10">
                      <CheckCircle2 className="h-7 w-7 text-emerald-300" />
                    </div>

                    <h3 className="mt-5 text-base font-semibold">
                      All recommendations actioned
                    </h3>

                    <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
                      There are no pending recommendations requiring action
                      right now. MUGONEXT will show new decisions here when
                      additional forecast intelligence is generated.
                    </p>

                    {summary.actioned > 0 ? (
                      <p className="mt-4 text-xs font-medium text-emerald-300">
                        {summary.actioned} recommendation
                        {summary.actioned === 1 ? "" : "s"} completed.
                      </p>
                    ) : null}
                  </div>
                ) : (
                  activeRecommendations.map((recommendation) => (
                    <RecommendationCard
                      key={recommendation.id}
                      recommendation={recommendation}
                      onAction={handleAction}
                      onArchive={handleArchive}
                      actionLoading={actionLoading === recommendation.id}
                    />
                  ))
                )}
              </div>

              {/* Workflow */}
              <div className="h-fit rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-emerald-300" />

                  <h2 className="text-lg font-semibold">
                    Recommendation workflow
                  </h2>
                </div>

                <div className="mt-7 space-y-7">
                  {[
                    [
                      "Analyze",
                      "MUGONEXT examines forecast values, trend, volatility, accuracy, and confidence.",
                    ],
                    [
                      "Prioritize",
                      "Business actions are ranked using forecast impact and confidence.",
                    ],
                    [
                      "Decide",
                      "The system converts forecast signals into a concrete business recommendation.",
                    ],
                    [
                      "Act",
                      "Your team can mark the recommendation as actioned once the decision is implemented.",
                    ],
                  ].map(([title, description], index) => (
                    <div key={title} className="flex gap-3">
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-xs font-semibold text-emerald-300 ring-1 ring-emerald-400/20">
                        {index + 1}
                      </div>

                      <div>
                        <p className="text-sm font-semibold">{title}</p>

                        <p className="mt-1 text-xs leading-5 text-slate-500">
                          {description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-8 rounded-2xl border border-emerald-400/10 bg-emerald-500/[0.04] p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-300">
                    Intelligence chain
                  </p>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Historical data → Forecast → Business signals →
                    Recommendation → Action
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
