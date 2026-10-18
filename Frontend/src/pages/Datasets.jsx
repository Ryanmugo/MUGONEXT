import { useEffect, useRef, useState } from "react";

import {
  ArrowRight,
  CheckCircle2,
  Database,
  FileSpreadsheet,
  Loader2,
  Upload,
  XCircle,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import { getUploads, uploadDataset } from "../services/api";

import Sidebar from "../components/Sidebar";

export default function Datasets() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [datasets, setDatasets] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  const [datasetName, setDatasetName] = useState("");

  // Optional:
  // Leave blank and MUGONEXT will automatically detect them.
  const [targetColumn, setTargetColumn] = useState("");
  const [dateColumn, setDateColumn] = useState("");

  const [description, setDescription] = useState("");

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [creatingForecast, setCreatingForecast] = useState(null);

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // =========================================================
  // LOAD DATASETS
  // =========================================================

  async function loadDatasets() {
    try {
      setLoading(true);
      setErrorMessage("");

      const data = await getUploads();

      const items = Array.isArray(data)
        ? data
        : data?.items || data?.uploads || data?.data || [];

      setDatasets(items);
    } catch (error) {
      console.error("Failed to load datasets:", error);

      setErrorMessage(error?.message || "Failed to load datasets.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDatasets();
  }, []);

  // =========================================================
  // FILE SELECTION
  // =========================================================

  function handleChooseFile() {
    setSuccessMessage("");
    setErrorMessage("");

    fileInputRef.current?.click();
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);

    setSuccessMessage("");
    setErrorMessage("");

    // Automatically create dataset name from filename
    const filenameWithoutExtension = file.name.replace(/\.[^/.]+$/, "");

    setDatasetName(filenameWithoutExtension);

    // Reset manual column overrides when a new file is selected.
    setTargetColumn("");
    setDateColumn("");
  }

  function handleRemoveSelectedFile() {
    setSelectedFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  // =========================================================
  // UPLOAD DATASET
  // =========================================================

  async function handleUpload(event) {
    event.preventDefault();

    setSuccessMessage("");
    setErrorMessage("");

    if (!selectedFile) {
      setErrorMessage("Please choose a dataset first.");
      return;
    }

    if (!datasetName.trim()) {
      setErrorMessage("Please enter a dataset name.");
      return;
    }

    try {
      setUploading(true);

      /*
       * IMPORTANT:
       *
       * Target column and date column are OPTIONAL.
       *
       * If the user leaves them blank, we do NOT send them.
       *
       * This allows the MUGONEXT backend to automatically detect:
       *
       *   Date / Order Date / Transaction Date / etc.
       *
       *   Sales / Revenue / Amount / Quantity / etc.
       */

      const uploadOptions = {
        dataset_name: datasetName.trim(),
        description: description.trim(),
      };

      if (targetColumn.trim()) {
        uploadOptions.target_column = targetColumn.trim();
      }

      if (dateColumn.trim()) {
        uploadOptions.date_column = dateColumn.trim();
      }

      const result = await uploadDataset(selectedFile, uploadOptions);

      console.log("Upload successful:", result);

      // Show detected columns if backend returned them.
      const detectedTarget =
        result?.target_column ||
        result?.column_metadata?.detected_columns?.target_column;

      const detectedDate =
        result?.date_column ||
        result?.column_metadata?.detected_columns?.date_column;

      if (detectedTarget && detectedDate) {
        setSuccessMessage(
          `Dataset uploaded successfully. MUGONEXT detected "${detectedTarget}" as the target column and "${detectedDate}" as the date column.`,
        );
      } else {
        setSuccessMessage("Dataset uploaded successfully.");
      }

      setSelectedFile(null);
      setDatasetName("");
      setTargetColumn("");
      setDateColumn("");
      setDescription("");

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadDatasets();
    } catch (error) {
      console.error("Dataset upload failed:", error);

      setErrorMessage(error?.message || "Dataset upload failed.");
    } finally {
      setUploading(false);
    }
  }

  // =========================================================
  // CREATE FORECAST
  // =========================================================

  function getUploadId(dataset) {
    return dataset?.id ?? dataset?.upload_id ?? dataset?.uploadId;
  }

  function handleCreateForecast(dataset) {
    const uploadId = getUploadId(dataset);

    if (!uploadId) {
      setErrorMessage("This dataset does not have a valid upload ID.");
      return;
    }

    setSuccessMessage("");
    setErrorMessage("");

    setCreatingForecast(uploadId);

    localStorage.setItem("mugonext_selected_upload_id", String(uploadId));

    navigate(`/forecasts?upload_id=${uploadId}`);
  }

  // =========================================================
  // HELPERS
  // =========================================================

  function formatFileSize(bytes) {
    if (!bytes || bytes <= 0) {
      return "";
    }

    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function getDatasetName(dataset) {
    return (
      dataset?.dataset_name ||
      dataset?.name ||
      dataset?.original_filename ||
      dataset?.filename ||
      "Unnamed dataset"
    );
  }

  function getTarget(dataset) {
    return dataset?.target_column || dataset?.target || "—";
  }

  function getDateColumn(dataset) {
    return dataset?.date_column || dataset?.date || "—";
  }

  function getStatus(dataset) {
    return dataset?.status || "Uploaded";
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="min-h-screen bg-[#0b0f14] text-white">
      <div className="flex min-h-screen">
        <Sidebar />

        <main className="min-w-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-6 py-8">
            {/* HEADER */}

            <div className="mb-8">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10">
                  <Database className="h-5 w-5" />
                </div>

                <div>
                  <h1 className="text-2xl font-semibold">Datasets</h1>

                  <p className="mt-1 text-sm text-gray-400">
                    Upload and manage your business data.
                  </p>
                </div>
              </div>
            </div>

            {/* UPLOAD CARD */}

            <div className="rounded-2xl border border-white/10 bg-[#11161d] p-6 shadow-xl">
              <div className="mb-6">
                <h2 className="text-lg font-semibold">Upload dataset</h2>

                <p className="mt-1 text-sm text-gray-400">
                  Import CSV or spreadsheet data into MUGONEXT.
                </p>
              </div>

              {/* SUCCESS */}

              {successMessage && (
                <div className="mb-5 flex items-start gap-3 rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-300">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0" />

                  <span>{successMessage}</span>
                </div>
              )}

              {/* ERROR */}

              {errorMessage && (
                <div className="mb-5 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  <XCircle className="mt-0.5 h-5 w-5 shrink-0" />

                  <span>{errorMessage}</span>
                </div>
              )}

              <form onSubmit={handleUpload}>
                {/* FILE SELECTOR */}

                <div className="rounded-xl border border-dashed border-white/15 bg-black/10 p-6">
                  <div className="flex flex-col items-center justify-center text-center">
                    <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-white/5">
                      <FileSpreadsheet className="h-7 w-7 text-gray-300" />
                    </div>

                    <h3 className="text-sm font-medium">Dataset upload</h3>

                    <p className="mt-2 max-w-lg text-sm text-gray-500">
                      Select a CSV or Excel spreadsheet containing your business
                      data. MUGONEXT will automatically detect the relevant
                      columns and validate the dataset before forecasting.
                    </p>

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv,.xlsx,.xls"
                      onChange={handleFileChange}
                      className="hidden"
                    />

                    <button
                      type="button"
                      onClick={handleChooseFile}
                      disabled={uploading}
                      className="mt-5 inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-medium text-black transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      <Upload className="h-4 w-4" />
                      Choose dataset
                    </button>

                    {selectedFile && (
                      <div className="mt-5 w-full max-w-lg rounded-xl border border-white/10 bg-white/5 p-4 text-left">
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium">
                              {selectedFile.name}
                            </p>

                            <p className="mt-1 text-xs text-gray-500">
                              {formatFileSize(selectedFile.size)}
                            </p>
                          </div>

                          <button
                            type="button"
                            onClick={handleRemoveSelectedFile}
                            disabled={uploading}
                            className="text-gray-500 transition hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                          >
                            <XCircle className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* FORM FIELDS */}

                <div className="mt-6 grid gap-5 md:grid-cols-2">
                  {/* DATASET NAME */}

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-300">
                      Dataset name
                    </label>

                    <input
                      type="text"
                      value={datasetName}
                      onChange={(event) => setDatasetName(event.target.value)}
                      placeholder="e.g. Daily Sales"
                      disabled={uploading}
                      className="w-full rounded-lg border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-gray-600 focus:border-white/30 disabled:cursor-not-allowed disabled:opacity-50"
                    />
                  </div>

                  {/* TARGET COLUMN */}

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-300">
                      Target column
                      <span className="ml-2 text-xs font-normal text-gray-600">
                        Optional
                      </span>
                    </label>

                    <input
                      type="text"
                      value={targetColumn}
                      onChange={(event) => setTargetColumn(event.target.value)}
                      placeholder="Leave blank for automatic detection"
                      disabled={uploading}
                      className="w-full rounded-lg border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-gray-600 focus:border-white/30 disabled:cursor-not-allowed disabled:opacity-50"
                    />

                    <p className="mt-1.5 text-xs text-gray-600">
                      MUGONEXT can detect Sales, Revenue, Amount, Quantity,
                      Units Sold, etc.
                    </p>
                  </div>

                  {/* DATE COLUMN */}

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-300">
                      Date column
                      <span className="ml-2 text-xs font-normal text-gray-600">
                        Optional
                      </span>
                    </label>

                    <input
                      type="text"
                      value={dateColumn}
                      onChange={(event) => setDateColumn(event.target.value)}
                      placeholder="Leave blank for automatic detection"
                      disabled={uploading}
                      className="w-full rounded-lg border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-gray-600 focus:border-white/30 disabled:cursor-not-allowed disabled:opacity-50"
                    />

                    <p className="mt-1.5 text-xs text-gray-600">
                      MUGONEXT can detect Date, Order Date, Transaction Date,
                      Invoice Date, etc.
                    </p>
                  </div>

                  {/* DESCRIPTION */}

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-300">
                      Description
                    </label>

                    <input
                      type="text"
                      value={description}
                      onChange={(event) => setDescription(event.target.value)}
                      placeholder="Optional description"
                      disabled={uploading}
                      className="w-full rounded-lg border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-gray-600 focus:border-white/30 disabled:cursor-not-allowed disabled:opacity-50"
                    />
                  </div>
                </div>

                {/* AUTOMATIC DETECTION INFO */}

                <div className="mt-5 rounded-xl border border-blue-500/10 bg-blue-500/5 px-4 py-3">
                  <div className="flex items-start gap-3">
                    <Database className="mt-0.5 h-4 w-4 shrink-0 text-blue-300" />

                    <div>
                      <p className="text-xs font-medium text-blue-300">
                        Automatic column detection
                      </p>

                      <p className="mt-1 text-xs leading-5 text-gray-500">
                        Leave Target column and Date column blank and MUGONEXT
                        will analyze your spreadsheet to identify the most
                        likely business metric and date column automatically.
                      </p>
                    </div>
                  </div>
                </div>

                {/* UPLOAD BUTTON */}

                <div className="mt-6 flex justify-end">
                  <button
                    type="submit"
                    disabled={uploading || !selectedFile}
                    className="inline-flex items-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Analyzing dataset...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4" />
                        Upload dataset
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* DATA PIPELINE */}

            <div className="mt-8 rounded-2xl border border-white/10 bg-[#11161d] p-6">
              <div className="mb-6">
                <h2 className="text-lg font-semibold">Data pipeline</h2>

                <p className="mt-1 text-sm text-gray-400">
                  How MUGONEXT processes your data.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-5">
                {[
                  ["01", "Upload", "Import business data"],
                  ["02", "Validate", "Check data quality"],
                  ["03", "Forecast", "Predict future performance"],
                  ["04", "Analyze", "Understand the drivers"],
                  ["05", "Recommend", "Generate actions"],
                ].map(([number, title, pipelineDescription]) => (
                  <div
                    key={number}
                    className="rounded-xl border border-white/10 bg-white/[0.02] p-4"
                  >
                    <div className="text-xs font-semibold text-gray-600">
                      {number}
                    </div>

                    <div className="mt-3 text-sm font-medium">{title}</div>

                    <div className="mt-1 text-xs text-gray-500">
                      {pipelineDescription}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* UPLOADED DATASETS */}

            <div className="mt-8 rounded-2xl border border-white/10 bg-[#11161d] p-6">
              <div className="mb-6">
                <h2 className="text-lg font-semibold">Uploaded datasets</h2>

                <p className="mt-1 text-sm text-gray-400">
                  Datasets available to MUGONEXT.
                </p>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-12 text-gray-500">
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Loading datasets...
                </div>
              ) : datasets.length === 0 ? (
                <div className="rounded-xl border border-white/10 bg-white/[0.02] p-8 text-center text-sm text-gray-500">
                  No datasets have been uploaded yet.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[850px] text-left">
                    <thead>
                      <tr className="border-b border-white/10 text-xs uppercase tracking-wide text-gray-600">
                        <th className="px-4 py-3 font-medium">Dataset</th>

                        <th className="px-4 py-3 font-medium">Target</th>

                        <th className="px-4 py-3 font-medium">Date</th>

                        <th className="px-4 py-3 font-medium">Status</th>

                        <th className="px-4 py-3 text-right font-medium">
                          Action
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {datasets.map((dataset, index) => {
                        const uploadId = getUploadId(dataset);

                        return (
                          <tr
                            key={
                              uploadId || `${getDatasetName(dataset)}-${index}`
                            }
                            className="border-b border-white/5 last:border-0"
                          >
                            <td className="px-4 py-4">
                              <div className="flex items-center gap-3">
                                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5">
                                  <FileSpreadsheet className="h-4 w-4 text-gray-400" />
                                </div>

                                <div className="min-w-0">
                                  <div className="font-medium text-white">
                                    {getDatasetName(dataset)}
                                  </div>

                                  {dataset?.original_filename &&
                                    dataset.original_filename !==
                                      getDatasetName(dataset) && (
                                      <div className="mt-1 truncate text-xs text-gray-600">
                                        {dataset.original_filename}
                                      </div>
                                    )}
                                </div>
                              </div>
                            </td>

                            <td className="px-4 py-4 text-sm text-gray-400">
                              {getTarget(dataset)}
                            </td>

                            <td className="px-4 py-4 text-sm text-gray-400">
                              {getDateColumn(dataset)}
                            </td>

                            <td className="px-4 py-4">
                              <span className="inline-flex items-center gap-1.5 rounded-full border border-green-500/20 bg-green-500/10 px-2.5 py-1 text-xs text-green-300">
                                <CheckCircle2 className="h-3.5 w-3.5" />

                                {getStatus(dataset)}
                              </span>
                            </td>

                            <td className="px-4 py-4 text-right">
                              <button
                                type="button"
                                disabled={
                                  !uploadId || creatingForecast === uploadId
                                }
                                onClick={() => handleCreateForecast(dataset)}
                                className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                              >
                                {creatingForecast === uploadId ? (
                                  <>
                                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                    Opening...
                                  </>
                                ) : (
                                  <>
                                    Create Forecast
                                    <ArrowRight className="h-3.5 w-3.5" />
                                  </>
                                )}
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
