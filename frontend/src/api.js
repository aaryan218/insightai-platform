const API_BASE = "http://localhost:8000";

export const api = {
  getAuthHeaders() {
    const token = localStorage.getItem("mlworkbench_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  async signup(username, password) {
    const res = await fetch(`${API_BASE}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Signup failed");
    return data;
  },

  async login(username, password) {
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");
    localStorage.setItem("mlworkbench_token", data.access_token);
    localStorage.setItem("mlworkbench_user", username);
    return data;
  },

  logout() {
    localStorage.removeItem("mlworkbench_token");
    localStorage.removeItem("mlworkbench_user");
  },

  getUser() {
    return localStorage.getItem("mlworkbench_user");
  },

  isAuthenticated() {
    return !!localStorage.getItem("mlworkbench_token");
  },

  async getTokens(username) {
    const res = await fetch(`${API_BASE}/tokens/${username}`, {
      headers: this.getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Could not fetch tokens");
    const data = await res.json();
    return data.tokens;
  },

  async addTokens(username, amount = 20) {
    const res = await fetch(`${API_BASE}/add_tokens`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify({
        username,
        credit_card: "1111-2222-3333-4444",
        amount,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to add tokens");
    return data.tokens;
  },

  async runEda(file) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/eda`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "EDA analysis failed");
    return data;
  },

  async downloadEdaReport(file) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/eda/report`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: formData,
    });
    if (!res.ok) throw new Error("Failed to generate report");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `eda_report_${file.name || "dataset"}.html`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },

  async trainModel(file, modelName, features, label, params = null) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", modelName);
    formData.append("features", features.join(","));
    formData.append("label", label);
    if (params) {
      formData.append("model_params", JSON.stringify(params));
    }

    const res = await fetch(`${API_BASE}/train`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Model training failed");
    return data;
  },

  async predict(modelName, values) {
    const res = await fetch(`${API_BASE}/predict/${modelName}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(values),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Prediction failed");
    return data.prediction;
  },

  async getModels() {
    const res = await fetch(`${API_BASE}/models`, {
      headers: this.getAuthHeaders(),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.models || [];
  },
};
