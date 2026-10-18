import { useEffect, useRef, useState } from "react";
import {
  Database,
  FileSpreadsheet,
  Upload,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";

import { getUploads, uploadDataset } from "../services/api";

export default function Datasets() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [datasetName, setDatasetName] = useState("");
  const [targetColumn, setTargetColumn] = useState("sales");
  const [dateColumn, setDateColumn] = useState("date");
  const [description, setDescription] = useState("");

  const [uploads, setUploads] = useState([]);
  const [loadingUploads, setLoadingUploads] = useState(true);
  const [uploading, setUploading] = useState(false);

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  async function loadUploads() {
    try {
      setLoadingUploads(true);

      const data = await getUploads();

      if (Array.isArray(data)) {
        setUploads(data);
      } else if (Array.isArray(data?.items)) {
        setUploads(data.items);
      } else {
        setUploads([]);
      }
    } catch (error) {
      console.error("Failed to load datasets:", error);
      setErrorMessage(error.message || "Failed to load datasets.");
    } finally {
      setLoadingUploads(false);
    }
  }

  useEffect(() => {
    loadUploads();
  }, []);

  function handleChooseFile() {
    setErrorMessage("");
    setSuccessMessage("");

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

    const filenameWithoutExtension = file.name.replace(/\.[^/.]+$/, "");

    if (!datasetName.trim()) {
      setDatasetName(filenameWithoutExtension);
    }
  }

  async function handleUpload() {
    if (!selectedFile) {
      setErrorMessage("Please select a CSV or spreadsheet file first.");
      return;
    }

    if (!datasetName.trim()) {
      setErrorMessage("Please enter a dataset name.");
      return;
    }

    if (!targetColumn.trim()) {
      setErrorMessage("Please enter the target column.");
      return;
    }

    if (!dateColumn.trim()) {
      setErrorMessage("Please enter the date column.");
      return;
    }

    try {
      setUploading(true);
      setErrorMessage("");
      setSuccessMessage("");

      await uploadDataset({
        file: selectedFile,
        datasetName,
        targetColumn,
        dateColumn,
        description,
      });

      setSuccessMessage(`${selectedFile.name} uploaded successfully.`);

      setSelectedFile(null);
      setDatasetName("");
      setDescription("");

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadUploads();
    } catch (error) {
      console.error("Dataset upload failed:", error);

      setErrorMessage(
        error?.message || "Dataset upload failed. Please try again.",
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0b0f14] text-white">
      <div className="mx-auto max-w-7xl px-6 py-10 lg:px-8">
        {/* HEADER */}
        <div className="mb-10">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 ring-1 ring-blue-400/20">
              <Database className="h-5 w-5 text-blue-300" />
            </div>

            <div>
              <h1 className="text-3xl font-bold tracking-tight">Datasets</h1>

              <p className="mt-1 text-sm text-slate-500">
                Upload and manage your business data.
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* UPLOAD PANEL */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 lg:col-span-2">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold">Upload dataset</h2>

                <p className="mt-1 text-sm text-slate-500">
                  Import CSV or spreadsheet data into MUGONEXT.
                </p>
              </div>

              <Upload className="h-5 w-5 text-blue-300" />
            </div>

            {/* HIDDEN FILE INPUT */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileChange}
              className="hidden"
            />

            <div className="mt-8 rounded-2xl border border-dashed border-white/10 bg-[#0a0f15] px-6 py-10">
              <div className="text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10">
                  <FileSpreadsheet className="h-7 w-7 text-blue-300" />
                </div>

                <h3 className="mt-5 text-base font-semibold">Dataset upload</h3>

                <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
                  Select a CSV or spreadsheet containing your business data.
                  MUGONEXT will validate it before forecasting.
                </p>

                {/* SELECT FILE BUTTON */}
                <button
                  type="button"
                  onClick={handleChooseFile}
                  disabled={uploading}
                  className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Upload className="h-4 w-4" />
                  Choose dataset
                </button>

                {selectedFile && (
                  <div className="mt-5 rounded-xl border border-blue-400/20 bg-blue-500/5 p-4 text-left">
                    <p className="text-xs uppercase tracking-wider text-slate-500">
                      Selected file
                    </p>

                    <p className="mt-1 break-all text-sm font-semibold text-white">
                      {selectedFile.name}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                )}
              </div>

              {/* FORM */}
              {selectedFile && (
                <div className="mt-8 space-y-5">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">
                      Dataset name
                    </label>

                    <input
                      type="text"
                      value={datasetName}
                      onChange={(e) => setDatasetName(e.target.value)}
                      placeholder="e.g. Monthly Sales"
                      className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-blue-400/50"
                    />
                  </div>

                  <div className="grid gap-5 sm:grid-cols-2">
                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-300">
                        Target column
                      </label>

                      <input
                        type="text"
                        value={targetColumn}
                        onChange={(e) => setTargetColumn(e.target.value)}
                        placeholder="sales"
                        className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-blue-400/50"
                      />
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-300">
                        Date column
                      </label>

                      <input
                        type="text"
                        value={dateColumn}
                        onChange={(e) => setDateColumn(e.target.value)}
                        placeholder="date"
                        className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-blue-400/50"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">
                      Description
                    </label>

                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Optional description of this dataset"
                      rows={3}
                      className="w-full resize-none rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-blue-400/50"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={handleUpload}
                    disabled={uploading}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4" />
                        Upload dataset
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* SUCCESS */}
              {successMessage && (
                <div className="mt-5 flex items-start gap-3 rounded-xl border border-emerald-400/20 bg-emerald-500/5 p-4">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />

                  <p className="text-sm text-emerald-300">{successMessage}</p>
                </div>
              )}

              {/* ERROR */}
              {errorMessage && (
                <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-400/20 bg-red-500/5 p-4">
                  <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />

                  <p className="text-sm text-red-300">{errorMessage}</p>
                </div>
              )}
            </div>
          </div>

          {/* PIPELINE */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-lg font-semibold">Data pipeline</h2>

            <p className="mt-1 text-sm text-slate-500">
              How MUGONEXT processes your data.
            </p>

            <div className="mt-8 space-y-5">
              {[
                ["01", "Upload", "Import business data"],
                ["02", "Validate", "Check data quality"],
                ["03", "Forecast", "Predict future performance"],
                ["04", "Analyze", "Understand the drivers"],
                ["05", "Recommend", "Generate actions"],
              ].map(([number, title, description]) => (
                <div key={number} className="flex gap-4">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/5 text-xs font-semibold text-slate-400">
                    {number}
                  </div>

                  <div>
                    <p className="text-sm font-semibold">{title}</p>

                    <p className="mt-1 text-xs text-slate-600">{description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* UPLOADED DATASETS */}
        <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Uploaded datasets</h2>

              <p className="mt-1 text-sm text-slate-500">
                Datasets available to MUGONEXT.
              </p>
            </div>
          </div>

          <div className="mt-6 overflow-x-auto">
            {loadingUploads ? (
              <div className="flex items-center gap-2 py-8 text-sm text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading datasets...
              </div>
            ) : uploads.length === 0 ? (
              <div className="py-8 text-sm text-slate-500">
                No datasets uploaded yet.
              </div>
            ) : (
              <table className="w-full min-w-[700px] text-left">
                <thead>
                  <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                    <th className="px-4 py-3">Dataset</th>
                    <th className="px-4 py-3">Target</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>

                <tbody>
                  {uploads.map((upload) => (
                    <tr
                      key={upload.id}
                      className="border-b border-white/5 text-sm"
                    >
                      <td className="px-4 py-4 font-medium">
                        {upload.name ||
                          upload.dataset_name ||
                          `Dataset #${upload.id}`}
                      </td>

                      <td className="px-4 py-4 text-slate-400">
                        {upload.target_column || "—"}
                      </td>

                      <td className="px-4 py-4 text-slate-400">
                        {upload.date_column || "—"}
                      </td>

                      <td className="px-4 py-4">
                        <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                          Uploaded
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
