const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "mugonext_access_token";

/* =========================================================
   REQUEST HELPER
========================================================= */

async function request(endpoint, options = {}) {
  if (typeof endpoint !== "string" || !endpoint) {
    throw new Error("Invalid API endpoint.");
  }

  const normalizedEndpoint = endpoint.startsWith("/")
    ? endpoint
    : `/${endpoint}`;

  const token = localStorage.getItem(TOKEN_KEY);

  const headers = {
    ...(options.headers || {}),
  };

  // Let the browser set Content-Type for FormData.
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  // Attach JWT to authenticated requests.
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${normalizedEndpoint}`;

  console.log("[MUGONEXT API REQUEST]", {
    url,
    method: options.method || "GET",
    authenticated: Boolean(token),
  });

  let response;

  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (error) {
    console.error("[MUGONEXT API NETWORK ERROR]", error);

    throw new Error(
      "Unable to connect to the MUGONEXT backend. Make sure the FastAPI server is running.",
    );
  }

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  console.log("[MUGONEXT API RESPONSE]", {
    url,
    status: response.status,
    data,
  });

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      `Request failed with status ${response.status}`;

    const error = new Error(
      typeof message === "string" ? message : JSON.stringify(message),
    );

    error.status = response.status;
    error.data = data;

    throw error;
  }

  return data;
}

/* =========================================================
   AUTH
========================================================= */

export async function login(email, password) {
  if (!email) {
    throw new Error("Email is required.");
  }

  if (!password) {
    throw new Error("Password is required.");
  }

  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
    }),
  });
}

export async function forgotPassword(email) {
  if (!email) {
    throw new Error("Email is required.");
  }

  return request("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({
      email,
    }),
  });
}

export async function resetPassword(token, newPassword) {
  if (!token) {
    throw new Error("Reset token is required.");
  }

  if (!newPassword) {
    throw new Error("New password is required.");
  }

  return request("/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({
      token,
      new_password: newPassword,
    }),
  });
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}

/* =========================================================
   COMPANY
========================================================= */

export async function getCompany() {
  return request("/companies/");
}

/* =========================================================
   USERS
========================================================= */

export async function getUsers() {
  return request("/users/");
}

/* =========================================================
   UPLOADS / DATASETS
========================================================= */

export async function getUploads() {
  return request("/uploads/");
}

export async function getUpload(uploadId) {
  if (!uploadId) {
    throw new Error("Upload ID is required.");
  }

  return request(`/uploads/${uploadId}`);
}

export async function uploadDataset(file, options = {}) {
  if (!file) {
    throw new Error("A file is required.");
  }

  const formData = new FormData();

  formData.append("file", file);

  formData.append(
    "dataset_name",
    options.dataset_name || options.name || file.name.replace(/\.[^/.]+$/, ""),
  );

  if (options.target_column && String(options.target_column).trim()) {
    formData.append("target_column", String(options.target_column).trim());
  }

  if (options.date_column && String(options.date_column).trim()) {
    formData.append("date_column", String(options.date_column).trim());
  }

  if (options.description && String(options.description).trim()) {
    formData.append("description", String(options.description).trim());
  }

  return request("/uploads/file", {
    method: "POST",
    body: formData,
  });
}

export async function deleteUpload(uploadId) {
  if (!uploadId) {
    throw new Error("Upload ID is required.");
  }

  return request(`/uploads/${uploadId}`, {
    method: "DELETE",
  });
}

/* =========================================================
   FORECASTS
========================================================= */

export async function getForecasts() {
  return request("/forecasts/");
}

export async function getForecast(forecastId) {
  if (!forecastId) {
    throw new Error("Forecast ID is required.");
  }

  return request(`/forecasts/${forecastId}`);
}

export async function createForecast({
  name,
  upload_id,
  description = "",
  forecast_model = "auto",
  target_column,
  date_column,
  forecast_periods = 30,
  frequency = "daily",
}) {
  if (!name || !String(name).trim()) {
    throw new Error("Forecast name is required.");
  }

  if (!upload_id) {
    throw new Error("A dataset is required.");
  }

  if (!target_column || !String(target_column).trim()) {
    throw new Error("Target column is required.");
  }

  if (!date_column || !String(date_column).trim()) {
    throw new Error("Date column is required.");
  }

  const periods = Number(forecast_periods);

  if (!Number.isInteger(periods) || periods < 1 || periods > 3650) {
    throw new Error("Forecast periods must be between 1 and 3650.");
  }

  return request("/forecasts/", {
    method: "POST",
    body: JSON.stringify({
      name: String(name).trim(),
      upload_id: Number(upload_id),
      description: String(description || "").trim(),
      forecast_model,
      target_column: String(target_column).trim(),
      date_column: String(date_column).trim(),
      forecast_periods: periods,
      frequency,
    }),
  });
}

export async function archiveForecast(forecastId) {
  if (!forecastId) {
    throw new Error("Forecast ID is required.");
  }

  return request(`/forecasts/${forecastId}/archive`, {
    method: "POST",
  });
}

export async function restoreForecast(forecastId) {
  if (!forecastId) {
    throw new Error("Forecast ID is required.");
  }

  return request(`/forecasts/${forecastId}/restore`, {
    method: "POST",
  });
}

/* =========================================================
   RECOMMENDATIONS
========================================================= */

export async function getRecommendations() {
  return request("/recommendations/");
}

export async function getRecommendation(recommendationId) {
  if (!recommendationId) {
    throw new Error("Recommendation ID is required.");
  }

  return request(`/recommendations/${recommendationId}`);
}

export async function generateRecommendations(forecastId) {
  if (!forecastId) {
    throw new Error("Forecast ID is required.");
  }

  return request("/recommendations/generate", {
    method: "POST",
    body: JSON.stringify({
      forecast_id: Number(forecastId),
    }),
  });
}

export async function markRecommendationActioned(
  recommendationId,
  actionNotes = "Recommendation actioned from MUGONEXT.",
) {
  if (!recommendationId) {
    throw new Error("Recommendation ID is required.");
  }

  return request(`/recommendations/${recommendationId}/action`, {
    method: "POST",
    body: JSON.stringify({
      action_taken: true,
      action_notes: actionNotes,
    }),
  });
}

export async function archiveRecommendation(recommendationId) {
  if (!recommendationId) {
    throw new Error("Recommendation ID is required.");
  }

  return request(`/recommendations/${recommendationId}/archive`, {
    method: "POST",
  });
}

export async function restoreRecommendation(recommendationId) {
  if (!recommendationId) {
    throw new Error("Recommendation ID is required.");
  }

  return request(`/recommendations/${recommendationId}/restore`, {
    method: "POST",
  });
}

/* =========================================================
   DEFAULT EXPORT
========================================================= */

export default {
  login,
  forgotPassword,
  resetPassword,
  logout,

  getCompany,
  getUsers,

  getUploads,
  getUpload,
  uploadDataset,
  deleteUpload,

  getForecasts,
  getForecast,
  createForecast,
  archiveForecast,
  restoreForecast,

  getRecommendations,
  getRecommendation,
  generateRecommendations,
  markRecommendationActioned,
  archiveRecommendation,
  restoreRecommendation,
};
