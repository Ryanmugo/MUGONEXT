import { useEffect, useMemo, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

import {
  Activity,
  AlertCircle,
  Archive,
  BarChart3,
  Brain,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Database,
  FileSpreadsheet,
  Gauge,
  History,
  Layers3,
  Loader2,
  Menu,
  MoreVertical,
  Play,
  Plus,
  RefreshCw,
  Search,
  Settings,
  Sparkles,
  Target,
  Trash2,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";

import {
  getForecasts,
  getUploads,
  createForecast,
  archiveForecast,
  deleteForecast,
} from "./services/api";

const navigation = [
  {
    label: "Dashboard",
    to: "/dashboard",
    icon: BarChart3,
  },
  {
    label: "Datasets",
    to: "/datasets",
    icon: Database,
  },
  {
    label: "Forecasts",
    to: "/forecasts",
    icon: TrendingUp,
  },
  {
    label: "Recommendations",
    to: "/recommendations",
    icon: Sparkles,
  },
  {
    label: "Team",
    to: "/team",
    icon: Layers3,
  },
  {
    label: "Settings",
    to: "/settings",
    icon: Settings,
  },
];

const MODEL_OPTIONS = [
  {
    value: "auto",
    label: "Auto Select",
    description: "Let MUGONEXT select the strongest model",
  },
  {
    value: "linear_regression",
    label: "Linear Regression",
    description: "Best for linear trends",
  },
  {
    value: "random_forest",
    label: "Random Forest",
    description: "Captures nonlinear relationships",
  },
  {
    value: "gradient_boosting",
    label: "Gradient Boosting",
    description: "Advanced predictive performance",
  },
];

const FREQUENCY_OPTIONS = [
  {
    value: "daily",
    label: "Daily",
  },
  {
    value: "weekly",
    label: "Weekly",
  },
  {
    value: "monthly",
    label: "Monthly",
  },
];

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatDateTime(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

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

function formatPercent(value) {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${Number(value).toFixed(1)}%`;
}

function prettyModel(model) {
  if (!model) return "Auto";

  return String(model)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusLabel(status) {
  if (!status) return "Unknown";

  return String(status)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function normalizedStatus(status) {
  return String(status || "").toLowerCase();
}

function isCompletedStatus(status) {
  const normalized = normalizedStatus(status);

  return (
    normalized.includes("complete") ||
    normalized.includes("success") ||
    normalized.includes("finished")
  );
}

function isProcessingStatus(status) {
  const normalized = normalizedStatus(status);

  return (
    normalized.includes("process") ||
    normalized.includes("running") ||
    normalized.includes("pending") ||
    normalized.includes("queued") ||
    normalized.includes("started")
  );
}

function isFailedStatus(status) {
  const normalized = normalizedStatus(status);

  return (
    normalized.includes("fail") ||
    normalized.includes("error") ||
    normalized.includes("cancel")
  );
}

function getStatusClasses(status) {
  if (isCompletedStatus(status)) {
    return "border-emerald-500/20 bg-emerald-500/10 text-emerald-300";
  }

  if (isProcessingStatus(status)) {
    return "border-amber-500/20 bg-amber-500/10 text-amber-300";
  }

  if (isFailedStatus(status)) {
    return "border-red-500/20 bg-red-500/10 text-red-300";
  }

  return "border-white/10 bg-white/5 text-slate-300";
}

/*
 * Dataset readiness is intentionally defensive.
 *
 * Different backend records may not contain every processing field.
 * We only reject a dataset when the backend explicitly tells us
 * that validation/processing failed or has not completed.
 */
function isDatasetReady(upload) {
  if (!upload) return false;

  if (upload.is_archived || upload.deleted_at) {
    return false;
  }

  if (upload.validation_passed === false) {
    return false;
  }

  if (upload.is_processed === false) {
    return false;
  }

  if (upload.preview_generated === false && upload.is_processed === false) {
    return false;
  }

  const status = normalizedStatus(upload.status);

  if (
    status.includes("fail") ||
    status.includes("error") ||
    status.includes("invalid")
  ) {
    return false;
  }

  return true;
}

function MetricCard({ label, value, icon: Icon, description }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#11151c] p-5 shadow-xl shadow-black/10">
      <div className="mb-4 flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5">
          <Icon size={19} className="text-slate-300" />
        </div>
      </div>

      <p className="text-xs font-medium uppercase tracking-[0.12em] text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold tracking-tight text-white">
        {value}
      </p>

      {description && (
        <p className="mt-1 text-xs text-slate-500">{description}</p>
      )}
    </div>
  );
}

function PredictionChart({ predictions = [] }) {
  const chartData = useMemo(() => {
    return predictions
      .map((item, index) => {
        const date =
          item?.date ??
          item?.datetime ??
          item?.timestamp ??
          item?.period ??
          item?.forecast_date ??
          item?.forecasted_date;

        const rawValue =
          item?.prediction ??
          item?.predicted_value ??
          item?.value ??
          item?.forecast ??
          item?.yhat;

        const value = Number(rawValue);

        return {
          index,
          date,
          value: Number.isFinite(value) ? value : null,
        };
      })
      .filter((item) => item.value !== null);
  }, [predictions]);

  if (!chartData.length) {
    return (
      <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-white/10 bg-[#0d1117]">
        <div className="text-center">
          <BarChart3 size={32} className="mx-auto mb-3 text-slate-600" />

          <p className="text-sm text-slate-400">
            No prediction points available.
          </p>

          <p className="mt-1 text-xs text-slate-600">
            Results will appear here when the forecast engine returns data.
          </p>
        </div>
      </div>
    );
  }

  const width = 900;
  const height = 320;
  const paddingX = 40;
  const paddingY = 30;

  const values = chartData.map((item) => item.value);

  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);

  const range = maxValue - minValue === 0 ? 1 : maxValue - minValue;

  const points = chartData.map((item, index) => {
    const x =
      paddingX +
      (index / Math.max(chartData.length - 1, 1)) * (width - paddingX * 2);

    const y =
      height -
      paddingY -
      ((item.value - minValue) / range) * (height - paddingY * 2);

    return {
      ...item,
      x,
      y,
    };
  });

  const linePath = points
    .map((point, index) => {
      return `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`;
    })
    .join(" ");

  const areaPath = `
    ${linePath}
    L ${points[points.length - 1].x} ${height - paddingY}
    L ${points[0].x} ${height - paddingY}
    Z
  `;

  const firstDate = chartData[0]?.date;
  const lastDate = chartData[chartData.length - 1]?.date;

  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#0d1117] p-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-white">
            Forecast trajectory
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {chartData.length} prediction points
          </p>
        </div>

        <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-400">
          {formatNumber(minValue)} — {formatNumber(maxValue)}
        </div>
      </div>

      <div className="w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="h-80 min-w-[700px] w-full"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="forecastArea" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="currentColor" stopOpacity="0.22" />

              <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
            </linearGradient>
          </defs>

          {[0, 1, 2, 3, 4].map((line) => {
            const y = paddingY + (line / 4) * (height - paddingY * 2);

            return (
              <line
                key={line}
                x1={paddingX}
                x2={width - paddingX}
                y1={y}
                y2={y}
                stroke="currentColor"
                className="text-white/5"
              />
            );
          })}

          <path
            d={areaPath}
            fill="url(#forecastArea)"
            className="text-indigo-500"
          />

          <path
            d={linePath}
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-indigo-400"
          />

          {points.length <= 60 &&
            points.map((point) => (
              <circle
                key={point.index}
                cx={point.x}
                cy={point.y}
                r="3"
                fill="currentColor"
                className="text-indigo-300"
              />
            ))}
        </svg>
      </div>

      <div className="mt-2 flex justify-between px-2 text-[11px] text-slate-600">
        <span>{firstDate ? formatDate(firstDate) : "Start"}</span>

        <span>{lastDate ? formatDate(lastDate) : "End"}</span>
      </div>
    </div>
  );
}

function ConfidenceBar({ score }) {
  if (
    score === null ||
    score === undefined ||
    score === "" ||
    Number.isNaN(Number(score))
  ) {
    return null;
  }

  const normalized = Math.max(0, Math.min(100, Number(score)));

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs text-slate-500">Confidence</span>

        <span className="text-sm font-semibold text-white">
          {formatPercent(normalized)}
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-white/5">
        <div
          className="h-full rounded-full bg-indigo-400 transition-all"
          style={{
            width: `${normalized}%`,
          }}
        />
      </div>
    </div>
  );
}

function EmptyState({ onCreate, hasDatasets }) {
  return (
    <div className="rounded-2xl border border-dashed border-white/10 bg-[#11151c] px-6 py-16 text-center">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-500/10">
        <TrendingUp size={28} className="text-indigo-400" />
      </div>

      <h3 className="mt-5 text-lg font-semibold text-white">
        No forecasts yet
      </h3>

      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
        Turn your historical business data into forward-looking predictions with
        MUGONEXT AI.
      </p>

      <button
        type="button"
        onClick={onCreate}
        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-400"
      >
        <Plus size={17} />

        {hasDatasets ? "Create Forecast" : "Prepare Dataset"}
      </button>

      {!hasDatasets && (
        <p className="mt-3 text-xs text-slate-600">
          Upload a validated dataset from the Datasets workspace first.
        </p>
      )}
    </div>
  );
}

export default function Forecasts() {
  const navigate = useNavigate();

  const [mobileMenu, setMobileMenu] = useState(false);

  const [forecasts, setForecasts] = useState([]);
  const [uploads, setUploads] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [showCreate, setShowCreate] = useState(false);

  const [selectedForecast, setSelectedForecast] = useState(null);

  const [openActionMenu, setOpenActionMenu] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");

  const [error, setError] = useState("");

  const [creating, setCreating] = useState(false);

  const [actionLoading, setActionLoading] = useState(null);

  const [form, setForm] = useState({
    name: "",
    uploadId: "",
    description: "",
    forecastModel: "auto",
    targetColumn: "",
    dateColumn: "",
    forecastPeriods: 30,
    frequency: "daily",
  });

  async function loadData(showRefresh = false) {
    try {
      setError("");

      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const [forecastData, uploadData] = await Promise.all([
        getForecasts(),
        getUploads(),
      ]);

      const nextForecasts = Array.isArray(forecastData) ? forecastData : [];

      const nextUploads = Array.isArray(uploadData) ? uploadData : [];

      setForecasts(nextForecasts);
      setUploads(nextUploads);

      /*
       * Keep the open result drawer synchronized with the newest
       * backend response. This matters when a forecast is still
       * processing and later becomes completed.
       */
      setSelectedForecast((current) => {
        if (!current?.id) {
          return current;
        }

        const refreshed = nextForecasts.find(
          (forecast) => String(forecast.id) === String(current.id),
        );

        return refreshed || current;
      });
    } catch (err) {
      setError(err?.message || "Unable to load forecasting data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      loadData(true);
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  /*
   * Only datasets that are usable for forecasting should appear
   * in the creation modal.
   */
  const processedUploads = useMemo(() => {
    return uploads.filter(isDatasetReady);
  }, [uploads]);

  const filteredForecasts = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    if (!query) {
      return forecasts;
    }

    return forecasts.filter((forecast) => {
      return [
        forecast.name,
        forecast.target_column,
        forecast.date_column,
        forecast.forecast_model,
        forecast.status,
        forecast.frequency,
      ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query));
    });
  }, [forecasts, searchTerm]);

  const completedForecasts = useMemo(
    () =>
      forecasts.filter((forecast) => isCompletedStatus(forecast.status)).length,
    [forecasts],
  );

  const averageAccuracy = useMemo(() => {
    const values = forecasts
      .map((forecast) => Number(forecast.accuracy_score))
      .filter((value) => Number.isFinite(value));

    if (!values.length) return null;

    return values.reduce((sum, value) => sum + value, 0) / values.length;
  }, [forecasts]);

  const averageConfidence = useMemo(() => {
    const values = forecasts
      .map((forecast) => Number(forecast.confidence_score))
      .filter((value) => Number.isFinite(value));

    if (!values.length) return null;

    return values.reduce((sum, value) => sum + value, 0) / values.length;
  }, [forecasts]);

  function resetForm() {
    setForm({
      name: "",
      uploadId: "",
      description: "",
      forecastModel: "auto",
      targetColumn: "",
      dateColumn: "",
      forecastPeriods: 30,
      frequency: "daily",
    });
  }

  function openCreate() {
    resetForm();
    setError("");
    setOpenActionMenu(null);
    setShowCreate(true);
  }

  function closeCreate() {
    if (creating) return;

    setShowCreate(false);
  }

  function handleDatasetChange(event) {
    const uploadId = event.target.value;

    const dataset = processedUploads.find(
      (upload) => String(upload.id) === String(uploadId),
    );

    setForm((current) => ({
      ...current,
      uploadId,
      targetColumn: dataset?.target_column || "",
      dateColumn: dataset?.date_column || "",
    }));
  }

  function getDatasetName(uploadId) {
    const dataset = uploads.find(
      (upload) => String(upload.id) === String(uploadId),
    );

    return (
      dataset?.dataset_name ||
      dataset?.original_filename ||
      `Dataset #${uploadId}`
    );
  }

  async function handleCreateForecast(event) {
    event.preventDefault();

    setError("");

    if (!form.name.trim()) {
      setError("Forecast name is required.");
      return;
    }

    if (!form.uploadId) {
      setError("Please select a dataset.");
      return;
    }

    const selectedDataset = processedUploads.find(
      (upload) => String(upload.id) === String(form.uploadId),
    );

    if (!selectedDataset) {
      setError("The selected dataset is no longer available for forecasting.");
      return;
    }

    if (!form.targetColumn.trim()) {
      setError("Target column is required.");
      return;
    }

    if (!form.dateColumn.trim()) {
      setError("Date column is required.");
      return;
    }

    const periods = Number(form.forecastPeriods);

    if (!Number.isInteger(periods) || periods < 1 || periods > 3650) {
      setError("Forecast periods must be between 1 and 3650.");
      return;
    }

    try {
      setCreating(true);

      const created = await createForecast({
        name: form.name.trim(),
        uploadId: Number(form.uploadId),
        description: form.description.trim(),
        forecastModel: form.forecastModel,
        targetColumn: form.targetColumn.trim(),
        dateColumn: form.dateColumn.trim(),
        forecastPeriods: periods,
        frequency: form.frequency,
      });

      setShowCreate(false);
      resetForm();

      if (created) {
        setSelectedForecast(created);
      }

      await loadData(true);
    } catch (err) {
      setError(err?.message || "Forecast generation failed.");
    } finally {
      setCreating(false);
    }
  }

  async function handleArchive(forecast) {
    if (!forecast?.id) return;

    const confirmed = window.confirm(`Archive "${forecast.name}"?`);

    if (!confirmed) return;

    try {
      setActionLoading(`archive-${forecast.id}`);
      setError("");
      setOpenActionMenu(null);

      await archiveForecast(forecast.id);

      if (selectedForecast?.id === forecast.id) {
        setSelectedForecast(null);
      }

      await loadData(true);
    } catch (err) {
      setError(
        err?.message ||
          "Unable to archive forecast. Manager permissions may be required.",
      );
    } finally {
      setActionLoading(null);
    }
  }

  async function handleDelete(forecast) {
    if (!forecast?.id) return;

    const confirmed = window.confirm(
      `Delete "${forecast.name}"? This is a soft delete and the database record will be retained.`,
    );

    if (!confirmed) return;

    try {
      setActionLoading(`delete-${forecast.id}`);
      setError("");
      setOpenActionMenu(null);

      await deleteForecast(forecast.id);

      if (selectedForecast?.id === forecast.id) {
        setSelectedForecast(null);
      }

      await loadData(true);
    } catch (err) {
      setError(
        err?.message ||
          "Unable to delete forecast. Manager permissions may be required.",
      );
    } finally {
      setActionLoading(null);
    }
  }

  function openForecast(forecast) {
    setOpenActionMenu(null);
    setSelectedForecast(forecast);
  }

  const selectedPredictions = selectedForecast?.predictions || [];

  return (
    <div className="min-h-screen bg-[#090c11] text-white">
      <div className="flex min-h-screen">
        {/* SIDEBAR */}
        <aside
          className={`
            fixed inset-y-0 left-0 z-50 w-64
            border-r border-white/10
            bg-[#0c1016]
            transition-transform duration-300
            lg:static lg:translate-x-0
            ${mobileMenu ? "translate-x-0" : "-translate-x-full"}
          `}
        >
          <div className="flex h-full flex-col">
            <div className="flex h-20 items-center border-b border-white/10 px-6">
              <div>
                <div className="text-xl font-bold tracking-tight">
                  MUGO<span className="text-indigo-400">NEXT</span>
                </div>

                <div className="mt-0.5 text-[10px] uppercase tracking-[0.22em] text-slate-600">
                  Intelligent Business AI
                </div>
              </div>
            </div>

            <div className="flex-1 px-3 py-6">
              <p className="px-3 pb-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600">
                Workspace
              </p>

              <nav className="space-y-1">
                {navigation.map(({ label, to, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileMenu(false)}
                    className={({ isActive }) =>
                      `
                          group flex items-center gap-3 rounded-xl
                          px-3 py-2.5 text-sm font-medium
                          transition
                          ${
                            isActive
                              ? "bg-indigo-500/10 text-indigo-300"
                              : "text-slate-500 hover:bg-white/5 hover:text-slate-200"
                          }
                        `
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <Icon
                          size={18}
                          className={
                            isActive
                              ? "text-indigo-400"
                              : "text-slate-600 group-hover:text-slate-300"
                          }
                        />

                        <span>{label}</span>

                        {isActive && (
                          <span className="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-400" />
                        )}
                      </>
                    )}
                  </NavLink>
                ))}
              </nav>
            </div>

            <div className="border-t border-white/10 p-4">
              <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10">
                    <Brain size={16} className="text-indigo-400" />
                  </div>

                  <div>
                    <p className="text-xs font-semibold text-white">
                      MUGONEXT AI
                    </p>

                    <p className="text-[10px] text-slate-600">
                      Forecast engine active
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* MOBILE OVERLAY */}
        {mobileMenu && (
          <button
            type="button"
            aria-label="Close menu"
            onClick={() => setMobileMenu(false)}
            className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          />
        )}

        {/* MAIN */}
        <main className="min-w-0 flex-1">
          {/* HEADER */}
          <header className="sticky top-0 z-30 border-b border-white/10 bg-[#090c11]/90 backdrop-blur-xl">
            <div className="flex h-20 items-center justify-between px-4 sm:px-6 lg:px-8">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setMobileMenu(true)}
                  className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-white lg:hidden"
                >
                  <Menu size={21} />
                </button>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-500">Workspace</span>

                    <ChevronRight size={14} className="text-slate-700" />

                    <span className="text-sm font-medium text-white">
                      Forecasts
                    </span>
                  </div>

                  <p className="mt-1 hidden text-xs text-slate-600 sm:block">
                    Turn historical data into forward-looking intelligence.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => loadData(true)}
                  disabled={refreshing}
                  className="rounded-xl border border-white/10 bg-white/[0.03] p-2.5 text-slate-500 transition hover:bg-white/5 hover:text-white disabled:opacity-50"
                  title="Refresh"
                >
                  <RefreshCw
                    size={17}
                    className={refreshing ? "animate-spin" : ""}
                  />
                </button>

                <button
                  type="button"
                  onClick={openCreate}
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-400"
                >
                  <Plus size={17} />

                  <span className="hidden sm:inline">New Forecast</span>
                </button>
              </div>
            </div>
          </header>

          <div className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            {/* ERROR */}
            {error && (
              <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/5 p-4">
                <AlertCircle
                  size={18}
                  className="mt-0.5 shrink-0 text-red-400"
                />

                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-red-300">{error}</p>
                </div>

                <button
                  type="button"
                  onClick={() => setError("")}
                  className="text-slate-600 hover:text-white"
                >
                  <X size={16} />
                </button>
              </div>
            )}

            {/* TITLE */}
            <div className="mb-7 flex flex-col justify-between gap-5 md:flex-row md:items-end">
              <div>
                <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/5 px-3 py-1.5 text-[11px] font-medium text-indigo-300">
                  <Zap size={13} />
                  AI FORECASTING ENGINE
                </div>

                <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                  Forecasts
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Generate predictive business intelligence from your validated
                  datasets.
                </p>
              </div>

              <div className="flex items-center gap-2 text-xs text-slate-600">
                <Activity size={14} />
                Live workspace data
              </div>
            </div>

            {/* KPI GRID */}
            <div className="mb-7 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard
                label="Total Forecasts"
                value={forecasts.length}
                icon={TrendingUp}
                description="Active forecasts"
              />

              <MetricCard
                label="Completed"
                value={completedForecasts}
                icon={CheckCircle2}
                description="Successfully generated"
              />

              <MetricCard
                label="Avg Accuracy"
                value={
                  averageAccuracy === null
                    ? "—"
                    : formatPercent(averageAccuracy)
                }
                icon={Gauge}
                description="Across available forecasts"
              />

              <MetricCard
                label="Avg Confidence"
                value={
                  averageConfidence === null
                    ? "—"
                    : formatPercent(averageConfidence)
                }
                icon={Brain}
                description="Model confidence"
              />
            </div>

            {/* SEARCH / TOOLBAR */}
            <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="relative w-full sm:max-w-md">
                <Search
                  size={17}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600"
                />

                <input
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Search forecasts..."
                  className="w-full rounded-xl border border-white/10 bg-[#11151c] py-3 pl-10 pr-4 text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-indigo-500/40"
                />
              </div>

              <div className="flex items-center gap-2 text-xs text-slate-600">
                <Database size={14} />
                {processedUploads.length} datasets available
              </div>
            </div>

            {/* CONTENT */}
            {loading ? (
              <div className="flex min-h-[420px] items-center justify-center rounded-2xl border border-white/10 bg-[#11151c]">
                <div className="text-center">
                  <Loader2
                    size={30}
                    className="mx-auto animate-spin text-indigo-400"
                  />

                  <p className="mt-4 text-sm text-slate-400">
                    Loading forecasting workspace...
                  </p>
                </div>
              </div>
            ) : filteredForecasts.length === 0 ? (
              <EmptyState
                onCreate={
                  processedUploads.length
                    ? openCreate
                    : () => navigate("/datasets")
                }
                hasDatasets={processedUploads.length > 0}
              />
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {filteredForecasts.map((forecast) => {
                  const processing = isProcessingStatus(forecast.status);

                  const completed = isCompletedStatus(forecast.status);

                  const failed = isFailedStatus(forecast.status);

                  const menuOpen = openActionMenu === forecast.id;

                  return (
                    <div
                      key={forecast.id}
                      className="group rounded-2xl border border-white/10 bg-[#11151c] p-5 transition hover:border-white/15 hover:bg-[#131821]"
                    >
                      <div className="flex flex-col gap-5 xl:flex-row xl:items-center">
                        {/* MAIN INFO */}
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="truncate text-base font-semibold text-white">
                              {forecast.name}
                            </h3>

                            <span
                              className={`rounded-full border px-2.5 py-1 text-[10px] font-medium ${getStatusClasses(
                                forecast.status,
                              )}`}
                            >
                              {statusLabel(forecast.status)}
                            </span>
                          </div>

                          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
                            <span className="inline-flex items-center gap-1.5">
                              <FileSpreadsheet size={13} />

                              {getDatasetName(forecast.upload_id)}
                            </span>

                            <span className="inline-flex items-center gap-1.5">
                              <Target size={13} />

                              {forecast.target_column}
                            </span>

                            <span className="inline-flex items-center gap-1.5">
                              <CalendarDays size={13} />
                              {forecast.forecast_periods} {forecast.frequency}
                            </span>
                          </div>

                          <div className="mt-4 flex flex-wrap items-center gap-3">
                            <div className="rounded-lg border border-white/10 bg-white/[0.025] px-3 py-2">
                              <p className="text-[10px] uppercase tracking-wider text-slate-600">
                                Model
                              </p>

                              <p className="mt-1 text-xs font-medium text-slate-300">
                                {prettyModel(forecast.forecast_model)}
                              </p>
                            </div>

                            <div className="rounded-lg border border-white/10 bg-white/[0.025] px-3 py-2">
                              <p className="text-[10px] uppercase tracking-wider text-slate-600">
                                Accuracy
                              </p>

                              <p className="mt-1 text-xs font-medium text-slate-300">
                                {formatPercent(forecast.accuracy_score)}
                              </p>
                            </div>

                            <div className="rounded-lg border border-white/10 bg-white/[0.025] px-3 py-2">
                              <p className="text-[10px] uppercase tracking-wider text-slate-600">
                                Confidence
                              </p>

                              <p className="mt-1 text-xs font-medium text-slate-300">
                                {formatPercent(forecast.confidence_score)}
                              </p>
                            </div>

                            {completed && (
                              <div className="rounded-lg border border-emerald-500/10 bg-emerald-500/5 px-3 py-2">
                                <p className="text-[10px] uppercase tracking-wider text-emerald-500/60">
                                  Result
                                </p>

                                <p className="mt-1 text-xs font-medium text-emerald-300">
                                  Ready
                                </p>
                              </div>
                            )}

                            {failed && (
                              <div className="rounded-lg border border-red-500/10 bg-red-500/5 px-3 py-2">
                                <p className="text-[10px] uppercase tracking-wider text-red-500/60">
                                  Result
                                </p>

                                <p className="mt-1 text-xs font-medium text-red-300">
                                  Attention required
                                </p>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* RIGHT SIDE */}
                        <div className="flex items-center justify-between gap-3 border-t border-white/5 pt-4 xl:border-t-0 xl:pt-0">
                          <div className="hidden text-right sm:block">
                            <p className="text-[10px] uppercase tracking-wider text-slate-600">
                              Created
                            </p>

                            <p className="mt-1 text-xs text-slate-400">
                              {formatDate(forecast.created_at)}
                            </p>
                          </div>

                          <button
                            type="button"
                            onClick={() => openForecast(forecast)}
                            className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-xs font-semibold text-slate-300 transition hover:bg-white/5 hover:text-white"
                          >
                            {processing ? "View Progress" : "View Results"}

                            <ChevronRight size={15} />
                          </button>

                          {/* ACTION MENU */}
                          <div className="relative">
                            <button
                              type="button"
                              onClick={() =>
                                setOpenActionMenu(menuOpen ? null : forecast.id)
                              }
                              disabled={actionLoading !== null}
                              aria-label={`Actions for ${forecast.name}`}
                              aria-expanded={menuOpen}
                              className="rounded-xl border border-white/10 bg-white/[0.03] p-2.5 text-slate-500 transition hover:bg-white/5 hover:text-white disabled:opacity-50"
                            >
                              {actionLoading ? (
                                <Loader2 size={16} className="animate-spin" />
                              ) : (
                                <MoreVertical size={17} />
                              )}
                            </button>

                            {menuOpen && (
                              <div className="absolute right-0 top-full z-40 mt-2 w-48 overflow-hidden rounded-xl border border-white/10 bg-[#0e131a] p-1.5 shadow-2xl shadow-black/40">
                                <button
                                  type="button"
                                  onClick={() => openForecast(forecast)}
                                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-xs font-medium text-slate-300 transition hover:bg-white/5 hover:text-white"
                                >
                                  <TrendingUp
                                    size={15}
                                    className="text-slate-500"
                                  />
                                  View Results
                                </button>

                                <button
                                  type="button"
                                  onClick={() => handleArchive(forecast)}
                                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-xs font-medium text-slate-300 transition hover:bg-white/5 hover:text-white"
                                >
                                  <Archive
                                    size={15}
                                    className="text-slate-500"
                                  />
                                  Archive Forecast
                                </button>

                                <div className="my-1 border-t border-white/5" />

                                <button
                                  type="button"
                                  onClick={() => handleDelete(forecast)}
                                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-xs font-medium text-red-400 transition hover:bg-red-500/5 hover:text-red-300"
                                >
                                  <Trash2 size={15} />
                                  Delete Forecast
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* PROGRESS */}
                      {processing && (
                        <div className="mt-5 border-t border-white/5 pt-4">
                          <div className="mb-2 flex items-center justify-between">
                            <span className="inline-flex items-center gap-2 text-xs text-amber-300">
                              <Loader2 size={13} className="animate-spin" />
                              Forecast processing
                            </span>

                            <span className="text-xs text-slate-500">
                              {forecast.progress ?? 0}%
                            </span>
                          </div>

                          <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                            <div
                              className="h-full rounded-full bg-amber-400 transition-all"
                              style={{
                                width: `${Math.max(
                                  0,
                                  Math.min(100, Number(forecast.progress || 0)),
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* CREATE FORECAST MODAL */}
      {showCreate && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-white/10 bg-[#0e131a] shadow-2xl">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-[#0e131a] px-6 py-5">
              <div>
                <div className="flex items-center gap-2">
                  <Sparkles size={17} className="text-indigo-400" />

                  <h2 className="text-lg font-semibold text-white">
                    Create AI Forecast
                  </h2>
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  Configure the forecasting engine for your dataset.
                </p>
              </div>

              <button
                type="button"
                onClick={closeCreate}
                disabled={creating}
                className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-white disabled:opacity-50"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateForecast} className="space-y-6 p-6">
              {/* NAME */}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                  Forecast Name
                </label>

                <input
                  type="text"
                  value={form.name}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      name: event.target.value,
                    }))
                  }
                  placeholder="e.g. Q4 Sales Forecast"
                  className="w-full rounded-xl border border-white/10 bg-[#090c11] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-700 focus:border-indigo-500/50"
                />
              </div>

              {/* DATASET */}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                  Dataset
                </label>

                <select
                  value={form.uploadId}
                  onChange={handleDatasetChange}
                  className="w-full rounded-xl border border-white/10 bg-[#090c11] px-4 py-3 text-sm text-white outline-none focus:border-indigo-500/50"
                >
                  <option value="">Select a validated dataset</option>

                  {processedUploads.map((upload) => (
                    <option key={upload.id} value={upload.id}>
                      {upload.dataset_name || upload.original_filename}
                    </option>
                  ))}
                </select>

                {!processedUploads.length && (
                  <div className="mt-3 rounded-xl border border-amber-500/15 bg-amber-500/5 p-3">
                    <p className="text-xs text-amber-300">
                      No validated datasets are currently available.
                    </p>

                    <button
                      type="button"
                      onClick={() => {
                        setShowCreate(false);
                        navigate("/datasets");
                      }}
                      className="mt-2 text-xs font-medium text-amber-400 underline underline-offset-4 hover:text-amber-300"
                    >
                      Go to Datasets
                    </button>
                  </div>
                )}
              </div>

              {/* TARGET + DATE */}
              <div className="grid gap-5 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Target Column
                  </label>

                  <input
                    type="text"
                    value={form.targetColumn}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        targetColumn: event.target.value,
                      }))
                    }
                    placeholder="e.g. sales"
                    className="w-full rounded-xl border border-white/10 bg-[#090c11] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-700 focus:border-indigo-500/50"
                  />

                  <p className="mt-2 text-[11px] text-slate-600">
                    The numeric business variable to predict.
                  </p>
                </div>

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Date Column
                  </label>

                  <input
                    type="text"
                    value={form.dateColumn}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        dateColumn: event.target.value,
                      }))
                    }
                    placeholder="e.g. date"
                    className="w-full rounded-xl border border-white/10 bg-[#090c11] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-700 focus:border-indigo-500/50"
                  />

                  <p className="mt-2 text-[11px] text-slate-600">
                    The historical time dimension used for forecasting.
                  </p>
                </div>
              </div>

              {/* MODEL */}
              <div>
                <label className="mb-3 block text-xs font-medium uppercase tracking-wider text-slate-500">
                  Forecasting Model
                </label>

                <div className="grid gap-2">
                  {MODEL_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() =>
                        setForm((current) => ({
                          ...current,
                          forecastModel: option.value,
                        }))
                      }
                      className={`
                        flex items-center justify-between rounded-xl border p-4 text-left transition
                        ${
                          form.forecastModel === option.value
                            ? "border-indigo-500/40 bg-indigo-500/10"
                            : "border-white/10 bg-white/[0.02] hover:bg-white/5"
                        }
                      `}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`
                            flex h-9 w-9 items-center justify-center rounded-lg
                            ${
                              form.forecastModel === option.value
                                ? "bg-indigo-500/15 text-indigo-300"
                                : "bg-white/5 text-slate-500"
                            }
                          `}
                        >
                          <Brain size={17} />
                        </div>

                        <div>
                          <p className="text-sm font-medium text-white">
                            {option.label}
                          </p>

                          <p className="mt-0.5 text-xs text-slate-600">
                            {option.description}
                          </p>
                        </div>
                      </div>

                      <div
                        className={`
                          h-4 w-4 rounded-full border
                          ${
                            form.forecastModel === option.value
                              ? "border-indigo-400 bg-indigo-400"
                              : "border-slate-700"
                          }
                        `}
                      />
                    </button>
                  ))}
                </div>
              </div>

              {/* PERIOD + FREQUENCY */}
              <div className="grid gap-5 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Forecast Periods
                  </label>

                  <input
                    type="number"
                    min="1"
                    max="3650"
                    value={form.forecastPeriods}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        forecastPeriods: event.target.value,
                      }))
                    }
                    className="w-full rounded-xl border border-white/10 bg-[#090c11] px-4 py-3 text-sm text-white outline-none focus:border-indigo-500/50"
                  />

                  <p className="mt-2 text-[11px] text-slate-600">
                    Maximum: 3,650 periods
                  </p>
                </div>

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Frequency
                  </label>

                  <select
                    value={form.frequency}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        frequency: event.target.value,
                      }))
                    }
                    className="w-full rounded-xl border border-white/10 bg-[#090c11] px-4 py-3 text-sm text-white outline-none focus:border-indigo-500/50"
                  >
                    {FREQUENCY_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* DESCRIPTION */}
              <div>
                <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                  Description
                  <span className="ml-2 normal-case tracking-normal text-slate-700">
                    optional
                  </span>
                </label>

                <textarea
                  rows="4"
                  value={form.description}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      description: event.target.value,
                    }))
                  }
                  placeholder="Describe what this forecast will be used for..."
                  className="w-full resize-none rounded-xl border border-white/10 bg-[#090c11] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-700 focus:border-indigo-500/50"
                />
              </div>

              {/* AI INFO */}
              <div className="rounded-xl border border-indigo-500/15 bg-indigo-500/5 p-4">
                <div className="flex gap-3">
                  <Brain
                    size={17}
                    className="mt-0.5 shrink-0 text-indigo-400"
                  />

                  <div>
                    <p className="text-sm font-medium text-indigo-200">
                      MUGONEXT AI will handle the analysis
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      The backend forecasting engine will validate the data,
                      select or use your chosen model, generate predictions,
                      calculate statistical metrics and produce the AI
                      explanation.
                    </p>
                  </div>
                </div>
              </div>

              {/* ACTIONS */}
              <div className="flex flex-col-reverse gap-3 border-t border-white/10 pt-5 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={closeCreate}
                  disabled={creating}
                  className="rounded-xl border border-white/10 px-5 py-3 text-sm font-medium text-slate-400 transition hover:bg-white/5 hover:text-white disabled:opacity-50"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={creating || !processedUploads.length}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {creating ? (
                    <>
                      <Loader2 size={17} className="animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Play size={17} />
                      Generate Forecast
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* FORECAST RESULTS DRAWER */}
      {selectedForecast && (
        <div className="fixed inset-0 z-[60] flex justify-end bg-black/60 backdrop-blur-sm">
          <button
            type="button"
            aria-label="Close results"
            onClick={() => setSelectedForecast(null)}
            className="absolute inset-0 cursor-default"
          />

          <section className="relative z-10 h-full w-full max-w-5xl overflow-y-auto border-l border-white/10 bg-[#0b0f15] shadow-2xl">
            {/* DRAWER HEADER */}
            <div className="sticky top-0 z-20 border-b border-white/10 bg-[#0b0f15]/95 px-5 py-5 backdrop-blur-xl sm:px-7">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-2.5 py-1 text-[10px] font-medium text-indigo-300">
                      <Sparkles size={11} />
                      AI FORECAST
                    </span>

                    <span
                      className={`rounded-full border px-2.5 py-1 text-[10px] font-medium ${getStatusClasses(
                        selectedForecast.status,
                      )}`}
                    >
                      {statusLabel(selectedForecast.status)}
                    </span>
                  </div>

                  <h2 className="truncate text-xl font-semibold text-white">
                    {selectedForecast.name}
                  </h2>

                  <p className="mt-1 text-xs text-slate-600">
                    Created {formatDateTime(selectedForecast.created_at)}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setSelectedForecast(null)}
                  className="rounded-xl border border-white/10 bg-white/[0.03] p-2.5 text-slate-500 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="space-y-6 p-5 sm:p-7">
              {/* ERROR */}
              {selectedForecast.error_message && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4">
                  <div className="flex gap-3">
                    <AlertCircle size={18} className="text-red-400" />

                    <div>
                      <p className="text-sm font-semibold text-red-300">
                        Forecast processing error
                      </p>

                      <p className="mt-1 text-xs leading-5 text-red-300/70">
                        {selectedForecast.error_message}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* PROCESSING NOTICE */}
              {isProcessingStatus(selectedForecast.status) && (
                <div className="rounded-xl border border-amber-500/15 bg-amber-500/5 p-4">
                  <div className="flex items-start gap-3">
                    <Loader2
                      size={18}
                      className="mt-0.5 shrink-0 animate-spin text-amber-400"
                    />

                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-amber-200">
                        Forecast is being generated
                      </p>

                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        MUGONEXT is processing the dataset and running the
                        forecasting engine. This view will update when the
                        latest forecast data is available.
                      </p>

                      <div className="mt-4">
                        <div className="mb-2 flex items-center justify-between">
                          <span className="text-xs text-slate-600">
                            Progress
                          </span>

                          <span className="text-xs font-medium text-amber-300">
                            {selectedForecast.progress ?? 0}%
                          </span>
                        </div>

                        <div className="h-2 overflow-hidden rounded-full bg-white/5">
                          <div
                            className="h-full rounded-full bg-amber-400 transition-all"
                            style={{
                              width: `${Math.max(
                                0,
                                Math.min(
                                  100,
                                  Number(selectedForecast.progress || 0),
                                ),
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* OVERVIEW */}
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                <MetricCard
                  label="Accuracy"
                  value={formatPercent(selectedForecast.accuracy_score)}
                  icon={Gauge}
                />

                <MetricCard
                  label="Confidence"
                  value={formatPercent(selectedForecast.confidence_score)}
                  icon={Brain}
                />

                <MetricCard
                  label="Quality"
                  value={formatPercent(selectedForecast.quality_score)}
                  icon={CheckCircle2}
                />

                <MetricCard
                  label="Periods"
                  value={selectedForecast.forecast_periods}
                  icon={CalendarDays}
                  description={selectedForecast.frequency}
                />
              </div>

              {/* FORECAST CONFIG */}
              <div className="rounded-2xl border border-white/10 bg-[#11151c] p-5">
                <div className="mb-5 flex items-center gap-2">
                  <Settings size={17} className="text-slate-500" />

                  <h3 className="text-sm font-semibold text-white">
                    Forecast Configuration
                  </h3>
                </div>

                <div className="grid grid-cols-2 gap-x-6 gap-y-5 sm:grid-cols-3">
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Dataset
                    </p>

                    <p className="mt-1 text-sm text-slate-300">
                      {getDatasetName(selectedForecast.upload_id)}
                    </p>
                  </div>

                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Model
                    </p>

                    <p className="mt-1 text-sm text-slate-300">
                      {prettyModel(selectedForecast.forecast_model)}
                    </p>
                  </div>

                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Frequency
                    </p>

                    <p className="mt-1 text-sm capitalize text-slate-300">
                      {selectedForecast.frequency}
                    </p>
                  </div>

                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Target
                    </p>

                    <p className="mt-1 text-sm text-slate-300">
                      {selectedForecast.target_column}
                    </p>
                  </div>

                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Date Column
                    </p>

                    <p className="mt-1 text-sm text-slate-300">
                      {selectedForecast.date_column}
                    </p>
                  </div>

                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-600">
                      Version
                    </p>

                    <p className="mt-1 text-sm text-slate-300">
                      v{selectedForecast.forecast_version}
                    </p>
                  </div>
                </div>
              </div>

              {/* DATE RANGE */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-[#11151c] p-5">
                  <div className="flex items-center gap-2">
                    <CalendarDays size={16} className="text-indigo-400" />

                    <p className="text-xs uppercase tracking-wider text-slate-600">
                      Forecast Start
                    </p>
                  </div>

                  <p className="mt-3 text-sm font-medium text-white">
                    {formatDate(selectedForecast.forecast_start_date)}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/10 bg-[#11151c] p-5">
                  <div className="flex items-center gap-2">
                    <CalendarDays size={16} className="text-indigo-400" />

                    <p className="text-xs uppercase tracking-wider text-slate-600">
                      Forecast End
                    </p>
                  </div>

                  <p className="mt-3 text-sm font-medium text-white">
                    {formatDate(selectedForecast.forecast_end_date)}
                  </p>
                </div>
              </div>

              {/* CHART */}
              <div>
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-white">
                      Predictions
                    </h3>

                    <p className="mt-1 text-xs text-slate-600">
                      Generated by the MUGONEXT forecasting engine
                    </p>
                  </div>

                  <span className="rounded-lg border border-white/10 bg-white/5 px-2.5 py-1.5 text-[10px] text-slate-500">
                    {selectedPredictions.length} points
                  </span>
                </div>

                <PredictionChart predictions={selectedPredictions} />
              </div>

              {/* STATISTICS */}
              <div>
                <div className="mb-3">
                  <h3 className="text-sm font-semibold text-white">
                    Model Performance
                  </h3>

                  <p className="mt-1 text-xs text-slate-600">
                    Statistical validation metrics returned by the backend.
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
                  <MetricCard
                    label="MAE"
                    value={formatNumber(selectedForecast.mae)}
                    icon={Activity}
                  />

                  <MetricCard
                    label="MSE"
                    value={formatNumber(selectedForecast.mse)}
                    icon={BarChart3}
                  />

                  <MetricCard
                    label="RMSE"
                    value={formatNumber(selectedForecast.rmse)}
                    icon={TrendingUp}
                  />

                  <MetricCard
                    label="MAPE"
                    value={formatPercent(selectedForecast.mape)}
                    icon={Target}
                  />

                  <MetricCard
                    label="R²"
                    value={formatNumber(selectedForecast.r_squared)}
                    icon={Gauge}
                  />
                </div>
              </div>

              {/* CONFIDENCE */}
              <div className="rounded-2xl border border-white/10 bg-[#11151c] p-5">
                <div className="mb-5 flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10">
                    <Brain size={17} className="text-indigo-400" />
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold text-white">
                      Model Confidence
                    </h3>

                    <p className="text-xs text-slate-600">
                      Confidence score produced by the forecasting engine.
                    </p>
                  </div>
                </div>

                <ConfidenceBar score={selectedForecast.confidence_score} />
              </div>

              {/* AI EXPLANATION */}
              {selectedForecast.ai_explanation && (
                <div className="rounded-2xl border border-indigo-500/15 bg-indigo-500/5 p-5">
                  <div className="flex gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10">
                      <Sparkles size={17} className="text-indigo-400" />
                    </div>

                    <div>
                      <h3 className="text-sm font-semibold text-indigo-200">
                        MUGONEXT AI Analysis
                      </h3>

                      <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-400">
                        {selectedForecast.ai_explanation}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* FEATURE IMPORTANCE */}
              {selectedForecast.feature_importance &&
                Object.keys(selectedForecast.feature_importance).length > 0 && (
                  <div className="rounded-2xl border border-white/10 bg-[#11151c] p-5">
                    <div className="mb-5 flex items-center gap-2">
                      <Layers3 size={17} className="text-slate-500" />

                      <div>
                        <h3 className="text-sm font-semibold text-white">
                          Feature Importance
                        </h3>

                        <p className="mt-1 text-xs text-slate-600">
                          Variables contributing to the model.
                        </p>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {Object.entries(selectedForecast.feature_importance)
                        .sort(
                          ([, a], [, b]) =>
                            Math.abs(Number(b)) - Math.abs(Number(a)),
                        )
                        .map(([feature, importance]) => {
                          const numeric = Number(importance);

                          const width = Math.min(100, Math.abs(numeric) * 100);

                          return (
                            <div key={feature}>
                              <div className="mb-1.5 flex items-center justify-between gap-4">
                                <span className="truncate text-xs text-slate-400">
                                  {feature}
                                </span>

                                <span className="shrink-0 text-xs font-medium text-slate-300">
                                  {formatNumber(numeric, 4)}
                                </span>
                              </div>

                              <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                                <div
                                  className="h-full rounded-full bg-indigo-400"
                                  style={{
                                    width: `${width}%`,
                                  }}
                                />
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  </div>
                )}

              {/* PROCESSING */}
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-xl border border-white/10 bg-[#11151c] p-4">
                  <div className="flex items-center gap-2 text-slate-600">
                    <Clock3 size={14} />

                    <span className="text-[10px] uppercase tracking-wider">
                      Processing Time
                    </span>
                  </div>

                  <p className="mt-2 text-sm text-white">
                    {selectedForecast.processing_time_seconds != null
                      ? `${selectedForecast.processing_time_seconds}s`
                      : "—"}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-[#11151c] p-4">
                  <div className="flex items-center gap-2 text-slate-600">
                    <History size={14} />

                    <span className="text-[10px] uppercase tracking-wider">
                      Started
                    </span>
                  </div>

                  <p className="mt-2 text-xs text-white">
                    {formatDateTime(selectedForecast.started_at)}
                  </p>
                </div>

                <div className="rounded-xl border border-white/10 bg-[#11151c] p-4">
                  <div className="flex items-center gap-2 text-slate-600">
                    <CheckCircle2 size={14} />

                    <span className="text-[10px] uppercase tracking-wider">
                      Completed
                    </span>
                  </div>

                  <p className="mt-2 text-xs text-white">
                    {formatDateTime(selectedForecast.completed_at)}
                  </p>
                </div>
              </div>

              {/* DESCRIPTION */}
              {selectedForecast.description && (
                <div className="rounded-xl border border-white/10 bg-[#11151c] p-5">
                  <p className="text-[10px] uppercase tracking-wider text-slate-600">
                    Description
                  </p>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    {selectedForecast.description}
                  </p>
                </div>
              )}

              {/* ACTIONS */}
              <div className="flex flex-col gap-3 border-t border-white/10 pt-6 sm:flex-row">
                <button
                  type="button"
                  onClick={() => handleArchive(selectedForecast)}
                  disabled={actionLoading !== null}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm font-medium text-slate-400 hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {actionLoading === `archive-${selectedForecast.id}` ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Archive size={16} />
                  )}
                  Archive Forecast
                </button>

                <button
                  type="button"
                  onClick={() => handleDelete(selectedForecast)}
                  disabled={actionLoading !== null}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm font-medium text-red-400 hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {actionLoading === `delete-${selectedForecast.id}` ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Trash2 size={16} />
                  )}
                  Delete Forecast
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
