import {
  Activity,
  AlertCircle,
  BarChart3,
  Brain,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Database,
  Gauge,
  Layers3,
  Loader2,
  RefreshCw,
  Sparkles,
  Target,
  TrendingUp,
  Wand2,
  X,
  Zap,
} from "lucide-react";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import {
  getUploads,
  getForecasts,
  createForecast,
  generateRecommendations,
} from "../services/api";

import Sidebar from "../components/Sidebar";

/* =========================================================
   HELPERS
========================================================= */

function getDatasetId(dataset) {
  return dataset?.id ?? dataset?.upload_id ?? dataset?.uploadId ?? "";
}

function getDatasetName(dataset) {
  return (
    dataset?.dataset_name ??
    dataset?.name ??
    dataset?.original_filename ??
    dataset?.filename ??
    `Dataset ${getDatasetId(dataset)}`
  );
}

function getTargetColumn(dataset) {
  return dataset?.target_column ?? dataset?.targetColumn ?? "sales";
}

function getDateColumn(dataset) {
  return dataset?.date_column ?? dataset?.dateColumn ?? "date";
}

function getForecastId(forecast) {
  return forecast?.id ?? forecast?.forecast_id ?? "";
}

function getForecastName(forecast) {
  return forecast?.name ?? forecast?.forecast_name ?? "Untitled forecast";
}

function toNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function formatNumber(value, decimals = 2) {
  const number = toNumber(value);

  if (number === null) {
    return "—";
  }

  return number.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatPercent(value) {
  const number = toNumber(value);

  if (number === null) {
    return "—";
  }

  return `${number.toFixed(2)}%`;
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatModel(model) {
  if (!model) {
    return "Auto";
  }

  const labels = {
    auto: "Auto",
    linear_regression: "Linear Regression",
    random_forest: "Random Forest",
    gradient_boosting: "Gradient Boosting",
  };

  return (
    labels[model] ||
    String(model)
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase())
  );
}

function normalizeArray(value) {
  if (Array.isArray(value)) {
    return value;
  }

  if (Array.isArray(value?.items)) {
    return value.items;
  }

  if (Array.isArray(value?.data)) {
    return value.data;
  }

  return [];
}

/* =========================================================
   SMALL UI COMPONENTS
========================================================= */

function MetricCard({ label, value, icon: Icon, description }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#111720] p-4 shadow-lg shadow-black/10">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            {label}
          </p>

          <p className="mt-2 text-2xl font-semibold tracking-tight text-white">
            {value}
          </p>

          {description && (
            <p className="mt-1 text-xs text-slate-500">{description}</p>
          )}
        </div>

        <div className="rounded-xl border border-white/10 bg-white/[0.04] p-2.5">
          <Icon className="h-4 w-4 text-blue-400" />
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ children, type = "blue" }) {
  const classes = {
    blue: "border-blue-400/20 bg-blue-400/10 text-blue-300",
    green: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
    amber: "border-amber-400/20 bg-amber-400/10 text-amber-300",
    red: "border-red-400/20 bg-red-400/10 text-red-300",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${
        classes[type] || classes.blue
      }`}
    >
      {children}
    </span>
  );
}

function SectionHeader({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-3">
        <div className="rounded-xl border border-white/10 bg-white/[0.04] p-2.5">
          <Icon className="h-5 w-5 text-blue-400" />
        </div>

        <div>
          <h2 className="text-base font-semibold text-white">{title}</h2>

          {description && (
            <p className="mt-1 text-sm text-slate-500">{description}</p>
          )}
        </div>
      </div>

      {action}
    </div>
  );
}

/* =========================================================
   MAIN PAGE
========================================================= */

export default function Forecasts() {
  const [searchParams] = useSearchParams();

  const [uploads, setUploads] = useState([]);
  const [forecasts, setForecasts] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [creating, setCreating] = useState(false);
  const [generatingRecommendations, setGeneratingRecommendations] =
    useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showCreate, setShowCreate] = useState(false);
  const [selectedForecast, setSelectedForecast] = useState(null);

  const [form, setForm] = useState({
    name: "Sales Forecast",
    uploadId: "",
    description:
      "AI-generated forecast created by the MUGONEXT forecasting engine.",
    forecastModel: "auto",
    targetColumn: "sales",
    dateColumn: "date",
    forecastPeriods: 30,
    frequency: "daily",
  });

  /* =========================================================
     DATASET NORMALIZATION
  ========================================================= */

  const processedUploads = useMemo(() => {
    return normalizeArray(uploads);
  }, [uploads]);

  const sortedForecasts = useMemo(() => {
    return [...forecasts].sort((a, b) => {
      const dateA = new Date(
        a?.created_at ?? a?.createdAt ?? a?.created ?? 0,
      ).getTime();

      const dateB = new Date(
        b?.created_at ?? b?.createdAt ?? b?.created ?? 0,
      ).getTime();

      return dateB - dateA;
    });
  }, [forecasts]);

  /* =========================================================
     LOAD DATA
  ========================================================= */

  const loadData = useCallback(
    async (silent = false) => {
      try {
        if (!silent) {
          setLoading(true);
        } else {
          setRefreshing(true);
        }

        setError("");

        const [uploadResponse, forecastResponse] = await Promise.all([
          getUploads(),
          getForecasts(),
        ]);

        const uploadData = normalizeArray(uploadResponse);
        const forecastData = normalizeArray(forecastResponse);

        setUploads(uploadData);
        setForecasts(forecastData);

        const requestedUploadId = searchParams.get("upload_id");

        const savedUploadId = localStorage.getItem(
          "mugonext_selected_upload_id",
        );

        const preferredUploadId = requestedUploadId || savedUploadId || "";

        let preferredDataset = null;

        if (preferredUploadId) {
          preferredDataset = uploadData.find(
            (upload) =>
              String(getDatasetId(upload)) === String(preferredUploadId),
          );
        }

        if (!preferredDataset) {
          preferredDataset = uploadData.find((upload) =>
            getDatasetName(upload)
              .toLowerCase()
              .includes("realistic_sales_180"),
          );
        }

        if (!preferredDataset) {
          preferredDataset = uploadData[0] || null;
        }

        if (preferredDataset) {
          const datasetId = getDatasetId(preferredDataset);

          setForm((previous) => ({
            ...previous,
            uploadId: String(datasetId),
            targetColumn: getTargetColumn(preferredDataset),
            dateColumn: getDateColumn(preferredDataset),
          }));
        }

        setSelectedForecast((previousSelected) => {
          if (previousSelected) {
            const updatedSelected = forecastData.find(
              (forecast) =>
                String(getForecastId(forecast)) ===
                String(getForecastId(previousSelected)),
            );

            return updatedSelected || previousSelected;
          }

          return forecastData[0] || null;
        });
      } catch (err) {
        setError(err?.message || "Unable to load MUGONEXT forecast data.");
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [searchParams],
  );

  useEffect(() => {
    loadData(false);
  }, [loadData]);

  /* =========================================================
     SELECTED DATASET
  ========================================================= */

  const selectedDataset = useMemo(() => {
    return (
      processedUploads.find(
        (upload) => String(getDatasetId(upload)) === String(form.uploadId),
      ) || null
    );
  }, [processedUploads, form.uploadId]);

  /* =========================================================
     FORM HANDLERS
  ========================================================= */

  function updateForm(field, value) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  }

  function handleDatasetChange(value) {
    const dataset = processedUploads.find(
      (upload) => String(getDatasetId(upload)) === String(value),
    );

    setForm((previous) => ({
      ...previous,
      uploadId: value,
      targetColumn: dataset ? getTargetColumn(dataset) : previous.targetColumn,
      dateColumn: dataset ? getDateColumn(dataset) : previous.dateColumn,
    }));

    if (value) {
      localStorage.setItem("mugonext_selected_upload_id", String(value));
    }
  }

  function resetForm() {
    const dataset =
      selectedDataset ||
      processedUploads.find((upload) =>
        getDatasetName(upload).toLowerCase().includes("realistic_sales_180"),
      ) ||
      processedUploads[0];

    setForm({
      name: "Sales Forecast",
      uploadId: dataset ? String(getDatasetId(dataset)) : "",
      description:
        "AI-generated forecast created by the MUGONEXT forecasting engine.",
      forecastModel: "auto",
      targetColumn: dataset ? getTargetColumn(dataset) : "sales",
      dateColumn: dataset ? getDateColumn(dataset) : "date",
      forecastPeriods: 30,
      frequency: "daily",
    });
  }

  /* =========================================================
     CREATE FORECAST
  ========================================================= */

  async function handleCreateForecast(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!form.name.trim()) {
      setError("Forecast name is required.");
      return;
    }

    if (!form.uploadId) {
      setError("Please select a dataset.");
      return;
    }

    const dataset = processedUploads.find(
      (upload) => String(getDatasetId(upload)) === String(form.uploadId),
    );

    if (!dataset) {
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
        upload_id: Number(form.uploadId),
        description: form.description.trim(),
        forecast_model: form.forecastModel,
        target_column: form.targetColumn.trim(),
        date_column: form.dateColumn.trim(),
        forecast_periods: periods,
        frequency: form.frequency,
      });

      setSuccess(
        "Forecast created successfully. MUGONEXT has generated the predictions.",
      );

      setShowCreate(false);

      if (created) {
        setSelectedForecast(created);
      }

      await loadData(true);

      if (created) {
        const createdId = getForecastId(created);

        const refreshedForecasts = await getForecasts();

        const refreshed = normalizeArray(refreshedForecasts);

        setForecasts(refreshed);

        const matching = refreshed.find(
          (forecast) => String(getForecastId(forecast)) === String(createdId),
        );

        setSelectedForecast(matching || created);
      }

      resetForm();
    } catch (err) {
      setError(err?.message || "Forecast generation failed.");
    } finally {
      setCreating(false);
    }
  }

  /* =========================================================
     RECOMMENDATIONS
  ========================================================= */

  async function handleGenerateRecommendations() {
    if (!selectedForecast) {
      setError(
        "Create or select a forecast before generating recommendations.",
      );
      return;
    }

    try {
      setGeneratingRecommendations(true);
      setError("");
      setSuccess("");

      const forecastId = getForecastId(selectedForecast);

      await generateRecommendations(forecastId);

      setSuccess("AI recommendations generated successfully.");
    } catch (err) {
      setError(err?.message || "Unable to generate recommendations.");
    } finally {
      setGeneratingRecommendations(false);
    }
  }

  /* =========================================================
     FORECAST METRICS
  ========================================================= */

  const selectedMetrics = useMemo(() => {
    if (!selectedForecast) {
      return {
        accuracy: null,
        confidence: null,
        quality: null,
        mae: null,
        rmse: null,
        mape: null,
        rSquared: null,
        predictions: [],
      };
    }

    const accuracy =
      toNumber(selectedForecast.accuracy_score) ??
      (() => {
        const mape = toNumber(selectedForecast.mape);

        if (mape === null) {
          return null;
        }

        return Math.max(0, Math.min(100, 100 - mape));
      })();

    const predictions =
      selectedForecast.predictions ??
      selectedForecast.forecast_predictions ??
      selectedForecast.prediction_values ??
      [];

    return {
      accuracy,
      confidence: toNumber(selectedForecast.confidence_score),
      quality: toNumber(selectedForecast.quality_score),
      mae: toNumber(selectedForecast.mae),
      rmse: toNumber(selectedForecast.rmse),
      mape: toNumber(selectedForecast.mape),
      rSquared: toNumber(selectedForecast.r_squared ?? selectedForecast.r2),
      predictions: Array.isArray(predictions) ? predictions : [],
    };
  }, [selectedForecast]);

  const averageAccuracy = useMemo(() => {
    const values = forecasts
      .map((forecast) => {
        const direct = toNumber(forecast.accuracy_score);

        if (direct !== null) {
          return direct;
        }

        const mape = toNumber(forecast.mape);

        if (mape !== null) {
          return Math.max(0, Math.min(100, 100 - mape));
        }

        return null;
      })
      .filter((value) => value !== null);

    if (!values.length) {
      return null;
    }

    return values.reduce((sum, value) => sum + value, 0) / values.length;
  }, [forecasts]);

  /* =========================================================
     PREDICTION NORMALIZATION
  ========================================================= */

  const normalizedPredictions = useMemo(() => {
    return selectedMetrics.predictions.map((prediction, index) => {
      if (typeof prediction === "number") {
        return {
          index: index + 1,
          date: null,
          value: prediction,
        };
      }

      if (typeof prediction === "object" && prediction !== null) {
        return {
          index: index + 1,
          date:
            prediction.date ??
            prediction.ds ??
            prediction.period ??
            prediction.timestamp ??
            null,
          value:
            prediction.value ??
            prediction.prediction ??
            prediction.predicted_value ??
            prediction.yhat ??
            prediction.sales ??
            null,
        };
      }

      return {
        index: index + 1,
        date: null,
        value: null,
      };
    });
  }, [selectedMetrics.predictions]);

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <div className="min-h-screen bg-[#0b0f14] text-white">
      <div className="flex min-h-screen">
        {/* SIDEBAR */}

        <Sidebar />

        {/* MAIN CONTENT */}

        <main className="min-w-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8">
            {/* HEADER */}

            <div className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-blue-400/20 bg-blue-400/10">
                    <Brain className="h-5 w-5 text-blue-400" />
                  </div>

                  <span className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
                    MUGONEXT AI
                  </span>
                </div>

                <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                  Forecasts
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Predict future business performance with AI-powered
                  forecasting.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <StatusBadge type="green">
                  <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  AI Engine Online
                </StatusBadge>

                <button
                  type="button"
                  onClick={() => loadData(true)}
                  disabled={refreshing}
                  className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <RefreshCw
                    className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
                  />
                  Refresh
                </button>

                <button
                  type="button"
                  onClick={() => {
                    resetForm();
                    setError("");
                    setSuccess("");
                    setShowCreate(true);
                  }}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-400"
                >
                  <Sparkles className="h-4 w-4" />
                  New Forecast
                </button>
              </div>
            </div>

            {/* ALERTS */}

            {error && (
              <div className="mb-6 flex items-start gap-3 rounded-2xl border border-red-400/20 bg-red-400/[0.06] p-4">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />

                <div className="flex-1">
                  <p className="text-sm font-medium text-red-300">{error}</p>
                </div>

                <button
                  type="button"
                  onClick={() => setError("")}
                  className="text-red-400/70 transition hover:text-red-300"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            {success && (
              <div className="mb-6 flex items-start gap-3 rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.06] p-4">
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />

                <div className="flex-1">
                  <p className="text-sm font-medium text-emerald-300">
                    {success}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setSuccess("")}
                  className="text-emerald-400/70 transition hover:text-emerald-300"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            {/* KPI OVERVIEW */}

            <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard
                label="Forecasts"
                value={forecasts.length}
                icon={BarChart3}
                description="Generated forecasts"
              />

              <MetricCard
                label="Average accuracy"
                value={formatPercent(averageAccuracy)}
                icon={Gauge}
                description="Across available forecasts"
              />

              <MetricCard
                label="Latest confidence"
                value={formatPercent(selectedMetrics.confidence)}
                icon={Brain}
                description="Composite AI confidence"
              />

              <MetricCard
                label="Predictions"
                value={
                  selectedMetrics.predictions.length
                    ? selectedMetrics.predictions.length
                    : "—"
                }
                icon={TrendingUp}
                description="Future periods generated"
              />
            </div>

            {/* FORECAST ENGINE */}

            <div className="mb-8 rounded-3xl border border-white/10 bg-[#0f151d] p-5 shadow-xl shadow-black/10 sm:p-6">
              <SectionHeader
                icon={Wand2}
                title="Forecast engine"
                description="Create forecasts from your uploaded datasets."
                action={
                  selectedDataset && (
                    <StatusBadge type="blue">
                      <Database className="mr-1.5 h-3.5 w-3.5" />
                      {getDatasetName(selectedDataset)}
                    </StatusBadge>
                  )
                }
              />

              <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
                {/* DATASET */}

                <div className="xl:col-span-2">
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Dataset
                  </label>

                  <div className="relative">
                    <select
                      value={form.uploadId}
                      onChange={(event) =>
                        handleDatasetChange(event.target.value)
                      }
                      className="w-full appearance-none rounded-xl border border-white/10 bg-[#111720] px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                    >
                      <option value="" className="bg-[#111720]">
                        Select a dataset
                      </option>

                      {processedUploads.map((dataset) => {
                        const id = getDatasetId(dataset);

                        return (
                          <option key={id} value={id} className="bg-[#111720]">
                            {getDatasetName(dataset)}
                          </option>
                        );
                      })}
                    </select>

                    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                  </div>

                  {selectedDataset && (
                    <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
                      <span>
                        Target:{" "}
                        <span className="text-slate-300">
                          {getTargetColumn(selectedDataset)}
                        </span>
                      </span>

                      <span className="text-slate-700">•</span>

                      <span>
                        Date:{" "}
                        <span className="text-slate-300">
                          {getDateColumn(selectedDataset)}
                        </span>
                      </span>
                    </div>
                  )}
                </div>

                {/* MODEL */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Forecast model
                  </label>

                  <div className="relative">
                    <select
                      value={form.forecastModel}
                      onChange={(event) =>
                        updateForm("forecastModel", event.target.value)
                      }
                      className="w-full appearance-none rounded-xl border border-white/10 bg-[#111720] px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                    >
                      <option value="auto" className="bg-[#111720]">
                        Auto — let MUGONEXT choose
                      </option>

                      <option
                        value="linear_regression"
                        className="bg-[#111720]"
                      >
                        Linear Regression
                      </option>

                      <option value="random_forest" className="bg-[#111720]">
                        Random Forest
                      </option>

                      <option
                        value="gradient_boosting"
                        className="bg-[#111720]"
                      >
                        Gradient Boosting
                      </option>
                    </select>

                    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                  </div>
                </div>

                {/* PERIODS */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Forecast periods
                  </label>

                  <input
                    type="number"
                    min="1"
                    max="3650"
                    value={form.forecastPeriods}
                    onChange={(event) =>
                      updateForm("forecastPeriods", event.target.value)
                    }
                    className="w-full rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                  />
                </div>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
                {/* TARGET */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Target column
                  </label>

                  <input
                    type="text"
                    value={form.targetColumn}
                    onChange={(event) =>
                      updateForm("targetColumn", event.target.value)
                    }
                    className="w-full rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                  />
                </div>

                {/* DATE */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Date column
                  </label>

                  <input
                    type="text"
                    value={form.dateColumn}
                    onChange={(event) =>
                      updateForm("dateColumn", event.target.value)
                    }
                    className="w-full rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                  />
                </div>

                {/* FREQUENCY */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Frequency
                  </label>

                  <div className="relative">
                    <select
                      value={form.frequency}
                      onChange={(event) =>
                        updateForm("frequency", event.target.value)
                      }
                      className="w-full appearance-none rounded-xl border border-white/10 bg-[#111720] px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                    >
                      <option value="daily" className="bg-[#111720]">
                        Daily
                      </option>

                      <option value="weekly" className="bg-[#111720]">
                        Weekly
                      </option>

                      <option value="monthly" className="bg-[#111720]">
                        Monthly
                      </option>
                    </select>

                    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                  </div>
                </div>
              </div>

              <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <Zap className="h-4 w-4 text-blue-400" />
                  MUGONEXT will analyze historical patterns and generate future
                  predictions.
                </div>

                <button
                  type="button"
                  onClick={() => {
                    resetForm();
                    setError("");
                    setSuccess("");
                    setShowCreate(true);
                  }}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-400"
                >
                  <Sparkles className="h-4 w-4" />
                  Create Forecast
                </button>
              </div>
            </div>

            {/* RESULTS */}

            <div className="rounded-3xl border border-white/10 bg-[#0f151d] p-5 shadow-xl shadow-black/10 sm:p-6">
              <SectionHeader
                icon={Activity}
                title="Forecast results"
                description="Results generated by the MUGONEXT forecasting engine."
                action={
                  selectedForecast && (
                    <button
                      type="button"
                      onClick={handleGenerateRecommendations}
                      disabled={generatingRecommendations}
                      className="inline-flex items-center gap-2 rounded-xl border border-blue-400/20 bg-blue-400/10 px-4 py-2.5 text-sm font-medium text-blue-300 transition hover:bg-blue-400/15 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {generatingRecommendations ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Sparkles className="h-4 w-4" />
                      )}

                      {generatingRecommendations
                        ? "Generating..."
                        : "Generate recommendations"}
                    </button>
                  )
                }
              />

              {loading ? (
                <div className="flex min-h-[300px] items-center justify-center">
                  <div className="text-center">
                    <Loader2 className="mx-auto h-8 w-8 animate-spin text-blue-400" />

                    <p className="mt-3 text-sm text-slate-500">
                      Loading forecast data...
                    </p>
                  </div>
                </div>
              ) : !selectedForecast ? (
                <div className="mt-6 flex min-h-[300px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.015] px-6 text-center">
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <BarChart3 className="h-8 w-8 text-slate-500" />
                  </div>

                  <h3 className="mt-4 text-base font-semibold text-white">
                    No forecast selected
                  </h3>

                  <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                    Create your first forecast from an uploaded dataset to see
                    AI predictions and performance metrics here.
                  </p>

                  <button
                    type="button"
                    onClick={() => {
                      resetForm();
                      setShowCreate(true);
                    }}
                    className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-400"
                  >
                    <Sparkles className="h-4 w-4" />
                    Create forecast
                  </button>
                </div>
              ) : (
                <>
                  {/* SELECTED FORECAST HEADER */}

                  <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.02] p-4">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-white">
                            {getForecastName(selectedForecast)}
                          </h3>

                          <StatusBadge type="green">
                            Forecast created
                          </StatusBadge>
                        </div>

                        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-500">
                          <span>
                            Selected model:{" "}
                            <span className="text-slate-300">
                              {formatModel(
                                selectedForecast.forecast_model ??
                                  selectedForecast.model,
                              )}
                            </span>
                          </span>

                          <span>
                            Created:{" "}
                            <span className="text-slate-300">
                              {formatDate(
                                selectedForecast.created_at ??
                                  selectedForecast.createdAt,
                              )}
                            </span>
                          </span>

                          <span>
                            Periods:{" "}
                            <span className="text-slate-300">
                              {selectedForecast.forecast_periods ??
                                selectedForecast.periods ??
                                normalizedPredictions.length}
                            </span>
                          </span>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() => loadData(true)}
                        disabled={refreshing}
                        className="self-start rounded-xl border border-white/10 bg-white/[0.03] p-2.5 text-slate-400 transition hover:bg-white/[0.06] hover:text-white disabled:opacity-50"
                        title="Refresh results"
                      >
                        <RefreshCw
                          className={`h-4 w-4 ${
                            refreshing ? "animate-spin" : ""
                          }`}
                        />
                      </button>
                    </div>
                  </div>

                  {/* PRIMARY METRICS */}

                  <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <MetricCard
                      label="Accuracy"
                      value={formatPercent(selectedMetrics.accuracy)}
                      icon={Gauge}
                      description="Historical forecast accuracy"
                    />

                    <MetricCard
                      label="Confidence"
                      value={formatPercent(selectedMetrics.confidence)}
                      icon={Brain}
                      description="Composite AI confidence"
                    />

                    <MetricCard
                      label="Quality"
                      value={formatPercent(selectedMetrics.quality)}
                      icon={CheckCircle2}
                      description="Forecast quality score"
                    />

                    <MetricCard
                      label="Periods"
                      value={
                        selectedForecast.forecast_periods ??
                        normalizedPredictions.length
                      }
                      icon={CalendarDays}
                      description="Future periods"
                    />
                  </div>

                  {/* ERROR METRICS */}

                  <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <MetricCard
                      label="MAE"
                      value={formatNumber(selectedMetrics.mae)}
                      icon={Target}
                      description="Mean absolute error"
                    />

                    <MetricCard
                      label="RMSE"
                      value={formatNumber(selectedMetrics.rmse)}
                      icon={Activity}
                      description="Root mean squared error"
                    />

                    <MetricCard
                      label="MAPE"
                      value={formatPercent(selectedMetrics.mape)}
                      icon={Gauge}
                      description="Mean absolute percentage error"
                    />

                    <MetricCard
                      label="R²"
                      value={formatNumber(selectedMetrics.rSquared)}
                      icon={TrendingUp}
                      description="Model fit score"
                    />
                  </div>

                  {/* PREDICTIONS */}

                  <div className="mt-6 rounded-2xl border border-white/10 bg-[#111720]">
                    <div className="flex flex-col gap-3 border-b border-white/10 p-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <h3 className="text-sm font-semibold text-white">
                          Future predictions
                        </h3>

                        <p className="mt-1 text-xs text-slate-500">
                          Values generated by the selected forecasting model.
                        </p>
                      </div>

                      <StatusBadge type="blue">
                        {normalizedPredictions.length} predictions
                      </StatusBadge>
                    </div>

                    {normalizedPredictions.length ? (
                      <div className="overflow-x-auto">
                        <table className="w-full min-w-[500px] text-left">
                          <thead>
                            <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                              <th className="px-4 py-3 font-medium">#</th>

                              <th className="px-4 py-3 font-medium">
                                Date / Period
                              </th>

                              <th className="px-4 py-3 text-right font-medium">
                                Prediction
                              </th>
                            </tr>
                          </thead>

                          <tbody>
                            {normalizedPredictions.map((prediction) => (
                              <tr
                                key={`${prediction.index}-${prediction.date || "prediction"}`}
                                className="border-b border-white/[0.06] last:border-0"
                              >
                                <td className="px-4 py-3 text-sm text-slate-500">
                                  {prediction.index}
                                </td>

                                <td className="px-4 py-3 text-sm text-slate-300">
                                  {prediction.date
                                    ? formatDate(prediction.date)
                                    : `Period ${prediction.index}`}
                                </td>

                                <td className="px-4 py-3 text-right text-sm font-semibold text-white">
                                  {formatNumber(prediction.value)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="p-8 text-center">
                        <TrendingUp className="mx-auto h-7 w-7 text-slate-600" />

                        <p className="mt-3 text-sm text-slate-500">
                          No prediction values were returned by the forecast.
                        </p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {/* FORECAST HISTORY */}

            {sortedForecasts.length > 0 && (
              <div className="mt-8 rounded-3xl border border-white/10 bg-[#0f151d] p-5 shadow-xl shadow-black/10 sm:p-6">
                <SectionHeader
                  icon={Layers3}
                  title="Forecast history"
                  description="Previously generated MUGONEXT forecasts."
                />

                <div className="mt-5 grid grid-cols-1 gap-3 lg:grid-cols-2">
                  {sortedForecasts.map((forecast) => {
                    const forecastId = getForecastId(forecast);

                    const forecastAccuracy =
                      toNumber(forecast.accuracy_score) ??
                      (() => {
                        const mape = toNumber(forecast.mape);

                        return mape === null
                          ? null
                          : Math.max(0, Math.min(100, 100 - mape));
                      })();

                    const isSelected =
                      String(getForecastId(selectedForecast)) ===
                      String(forecastId);

                    return (
                      <button
                        type="button"
                        key={forecastId}
                        onClick={() => setSelectedForecast(forecast)}
                        className={`rounded-2xl border p-4 text-left transition ${
                          isSelected
                            ? "border-blue-400/30 bg-blue-400/[0.06]"
                            : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <div
                                className={`h-2 w-2 rounded-full ${
                                  isSelected ? "bg-blue-400" : "bg-slate-600"
                                }`}
                              />

                              <p className="truncate text-sm font-semibold text-white">
                                {getForecastName(forecast)}
                              </p>
                            </div>

                            <p className="mt-2 text-xs text-slate-500">
                              {formatModel(
                                forecast.forecast_model ?? forecast.model,
                              )}
                              {" • "}
                              {forecast.forecast_periods ??
                                forecast.periods ??
                                "—"}{" "}
                              periods
                            </p>
                          </div>

                          <StatusBadge
                            type={
                              forecastAccuracy !== null &&
                              forecastAccuracy >= 90
                                ? "green"
                                : "blue"
                            }
                          >
                            {formatPercent(forecastAccuracy)}
                          </StatusBadge>
                        </div>

                        <div className="mt-4 grid grid-cols-3 gap-3">
                          <div>
                            <p className="text-[10px] uppercase tracking-wider text-slate-600">
                              Confidence
                            </p>

                            <p className="mt-1 text-sm font-medium text-slate-300">
                              {formatPercent(forecast.confidence_score)}
                            </p>
                          </div>

                          <div>
                            <p className="text-[10px] uppercase tracking-wider text-slate-600">
                              MAPE
                            </p>

                            <p className="mt-1 text-sm font-medium text-slate-300">
                              {formatPercent(forecast.mape)}
                            </p>
                          </div>

                          <div>
                            <p className="text-[10px] uppercase tracking-wider text-slate-600">
                              R²
                            </p>

                            <p className="mt-1 text-sm font-medium text-slate-300">
                              {formatNumber(forecast.r_squared ?? forecast.r2)}
                            </p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* CAPABILITIES */}

            <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-[#0f151d] p-5">
                <div className="w-fit rounded-xl border border-blue-400/20 bg-blue-400/10 p-2.5">
                  <Brain className="h-5 w-5 text-blue-400" />
                </div>

                <h3 className="mt-4 text-sm font-semibold text-white">
                  AI model selection
                </h3>

                <p className="mt-2 text-xs leading-5 text-slate-500">
                  MUGONEXT can compare available forecasting approaches and
                  select the model configured for the forecast.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-[#0f151d] p-5">
                <div className="w-fit rounded-xl border border-emerald-400/20 bg-emerald-400/10 p-2.5">
                  <TrendingUp className="h-5 w-5 text-emerald-400" />
                </div>

                <h3 className="mt-4 text-sm font-semibold text-white">
                  Future demand visibility
                </h3>

                <p className="mt-2 text-xs leading-5 text-slate-500">
                  Convert historical business data into forward-looking
                  predictions that can support planning and decision-making.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-[#0f151d] p-5">
                <div className="w-fit rounded-xl border border-purple-400/20 bg-purple-400/10 p-2.5">
                  <Sparkles className="h-5 w-5 text-purple-400" />
                </div>

                <h3 className="mt-4 text-sm font-semibold text-white">
                  Decision intelligence
                </h3>

                <p className="mt-2 text-xs leading-5 text-slate-500">
                  Forecasts can feed into MUGONEXT recommendations so businesses
                  can move from prediction toward action.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* CREATE FORECAST MODAL */}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl overflow-hidden rounded-3xl border border-white/10 bg-[#0f151d] shadow-2xl shadow-black/40">
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-4 sm:px-6">
              <div>
                <div className="flex items-center gap-2">
                  <div className="rounded-xl border border-blue-400/20 bg-blue-400/10 p-2">
                    <Sparkles className="h-4 w-4 text-blue-400" />
                  </div>

                  <h2 className="text-base font-semibold text-white">
                    Create forecast
                  </h2>
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  Configure how MUGONEXT should analyze your dataset.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="rounded-xl p-2 text-slate-500 transition hover:bg-white/[0.05] hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form
              onSubmit={handleCreateForecast}
              className="max-h-[80vh] overflow-y-auto p-5 sm:p-6"
            >
              <div className="space-y-5">
                {/* NAME */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Forecast name
                  </label>

                  <input
                    type="text"
                    value={form.name}
                    onChange={(event) => updateForm("name", event.target.value)}
                    placeholder="e.g. July Sales Forecast"
                    className="w-full rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white placeholder:text-slate-700 outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                  />
                </div>

                {/* DESCRIPTION */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Description
                  </label>

                  <textarea
                    value={form.description}
                    onChange={(event) =>
                      updateForm("description", event.target.value)
                    }
                    rows={3}
                    className="w-full resize-none rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white placeholder:text-slate-700 outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                  />
                </div>

                {/* DATASET */}

                <div>
                  <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                    Dataset
                  </label>

                  <div className="relative">
                    <select
                      value={form.uploadId}
                      onChange={(event) =>
                        handleDatasetChange(event.target.value)
                      }
                      className="w-full appearance-none rounded-xl border border-white/10 bg-[#111720] px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                    >
                      <option value="" className="bg-[#111720]">
                        Select dataset
                      </option>

                      {processedUploads.map((dataset) => {
                        const id = getDatasetId(dataset);

                        return (
                          <option key={id} value={id} className="bg-[#111720]">
                            {getDatasetName(dataset)}
                          </option>
                        );
                      })}
                    </select>

                    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                  </div>
                </div>

                {/* MODEL + FREQUENCY */}

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                      Forecast model
                    </label>

                    <div className="relative">
                      <select
                        value={form.forecastModel}
                        onChange={(event) =>
                          updateForm("forecastModel", event.target.value)
                        }
                        className="w-full appearance-none rounded-xl border border-white/10 bg-[#111720] px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                      >
                        <option value="auto" className="bg-[#111720]">
                          Auto — let MUGONEXT choose
                        </option>

                        <option
                          value="linear_regression"
                          className="bg-[#111720]"
                        >
                          Linear Regression
                        </option>

                        <option value="random_forest" className="bg-[#111720]">
                          Random Forest
                        </option>

                        <option
                          value="gradient_boosting"
                          className="bg-[#111720]"
                        >
                          Gradient Boosting
                        </option>
                      </select>

                      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                    </div>
                  </div>

                  <div>
                    <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                      Frequency
                    </label>

                    <div className="relative">
                      <select
                        value={form.frequency}
                        onChange={(event) =>
                          updateForm("frequency", event.target.value)
                        }
                        className="w-full appearance-none rounded-xl border border-white/10 bg-[#111720] px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                      >
                        <option value="daily" className="bg-[#111720]">
                          Daily
                        </option>

                        <option value="weekly" className="bg-[#111720]">
                          Weekly
                        </option>

                        <option value="monthly" className="bg-[#111720]">
                          Monthly
                        </option>
                      </select>

                      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                    </div>
                  </div>
                </div>

                {/* TARGET / DATE / PERIODS */}

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                      Target column
                    </label>

                    <input
                      type="text"
                      value={form.targetColumn}
                      onChange={(event) =>
                        updateForm("targetColumn", event.target.value)
                      }
                      className="w-full rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                      Date column
                    </label>

                    <input
                      type="text"
                      value={form.dateColumn}
                      onChange={(event) =>
                        updateForm("dateColumn", event.target.value)
                      }
                      className="w-full rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500">
                      Forecast periods
                    </label>

                    <input
                      type="number"
                      min="1"
                      max="3650"
                      value={form.forecastPeriods}
                      onChange={(event) =>
                        updateForm("forecastPeriods", event.target.value)
                      }
                      className="w-full rounded-xl border border-white/10 bg-[#111720] px-4 py-3 text-sm text-white outline-none transition focus:border-blue-400/40 focus:ring-2 focus:ring-blue-400/10"
                    />
                  </div>
                </div>
              </div>

              {/* MODAL ACTIONS */}

              <div className="mt-6 flex flex-col-reverse gap-3 border-t border-white/10 pt-5 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  disabled={creating}
                  className="rounded-xl border border-white/10 bg-white/[0.03] px-5 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/[0.06] disabled:opacity-50"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={creating || !form.uploadId}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {creating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating forecast...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Generate forecast
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
