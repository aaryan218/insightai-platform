import React, { useState, useEffect } from "react";
import { Play, Sparkles, Brain, CheckCircle2, AlertCircle, ArrowLeft, History, Cpu } from "lucide-react";
import { api } from "../api";
import confetti from "canvas-confetti";

export default function TrainPage({ datasetFile, onNavigate, onTokensUpdated }) {
  const [modelType, setModelType] = useState("linear");
  const [columns, setColumns] = useState([]);
  const [targetLabel, setTargetLabel] = useState("");
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);
  const [error, setError] = useState(null);

  // Prediction testing state
  const [predictInputs, setPredictInputs] = useState({});
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [predictError, setPredictError] = useState(null);

  // Models history
  const [modelsList, setModelsList] = useState([]);

  useEffect(() => {
    loadModels();
    parseColumns();
  }, [datasetFile]);

  const loadModels = async () => {
    try {
      const list = await api.getModels();
      setModelsList(list);
    } catch (e) {
      console.error(e);
    }
  };

  const parseColumns = async () => {
    if (!datasetFile) return;
    try {
      const text = await datasetFile.text();
      const firstLine = text.split("\n")[0];
      const cols = firstLine.split(",").map(c => c.trim().replace(/^"|"$/g, "")).filter(Boolean);
      setColumns(cols);
      if (cols.length > 0) {
        const lastCol = cols[cols.length - 1];
        setTargetLabel(lastCol);
        setSelectedFeatures(cols.filter(c => c !== lastCol));
      }
    } catch (e) {
      console.error("Error reading CSV header:", e);
    }
  };

  const handleTargetChange = (e) => {
    const newTarget = e.target.value;
    setTargetLabel(newTarget);
    setSelectedFeatures(columns.filter(c => c !== newTarget));
  };

  const toggleFeature = (col) => {
    if (selectedFeatures.includes(col)) {
      if (selectedFeatures.length === 1) {
        setError("You must select at least one feature.");
        return;
      }
      setSelectedFeatures(selectedFeatures.filter(c => c !== col));
    } else {
      setSelectedFeatures([...selectedFeatures, col]);
    }
  };

  const handleTrain = async (e) => {
    e.preventDefault();
    if (!targetLabel || selectedFeatures.length === 0) {
      setError("Please select a target and at least one input feature.");
      return;
    }

    setTraining(true);
    setError(null);
    setTrainResult(null);

    try {
      const res = await api.trainModel(datasetFile, modelType, selectedFeatures, targetLabel);
      setTrainResult(res);
      confetti({ particleCount: 75, spread: 60, origin: { y: 0.85 } });
      loadModels();
      if (onTokensUpdated) onTokensUpdated();

      // Pre-fill prediction inputs
      const initialInputs = {};
      selectedFeatures.forEach(f => {
        initialInputs[f] = 0;
      });
      setPredictInputs(initialInputs);
    } catch (err) {
      setError(err.message);
    } finally {
      setTraining(false);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setPredicting(true);
    setPredictError(null);
    setPrediction(null);

    try {
      const numericPayload = {};
      for (const [k, v] of Object.entries(predictInputs)) {
        numericPayload[k] = parseFloat(v) || 0;
      }
      const val = await api.predict(trainResult.model_name, numericPayload);
      setPrediction(val);
      if (onTokensUpdated) onTokensUpdated();
    } catch (err) {
      setPredictError(err.message);
    } finally {
      setPredicting(false);
    }
  };

  if (!datasetFile) {
    return (
      <div style={{ textAlign: "center", padding: "80px 20px" }}>
        <p style={{ color: "var(--text-muted)", marginBottom: "20px" }}>No dataset found. Please upload a CSV first.</p>
        <button className="btn btn-primary" onClick={() => onNavigate("upload")}>
          Go to Upload Page
        </button>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ maxWidth: "1100px", margin: "0 auto", padding: "30px 20px 60px 20px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "28px", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <button className="btn btn-secondary" onClick={() => onNavigate("eda")} style={{ marginBottom: "12px", padding: "6px 14px", fontSize: "13px" }}>
            <ArrowLeft size={14} /> Back to Auto EDA
          </button>
          <h1 style={{ fontSize: "28px", fontWeight: "800" }}>Model Training & Real-Time Predictions</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
            Train algorithms against your dataset and run live predictions directly through the FastAPI inference engine.
          </p>
        </div>
        <span className="badge badge-emerald" style={{ padding: "8px 16px" }}>
          Active File: {datasetFile.name}
        </span>
      </div>

      {/* STEP 1: MODEL CONFIGURATION */}
      <div className="glass-card" style={{ padding: "30px", marginBottom: "28px" }}>
        <h3 style={{ fontSize: "18px", marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
          <Brain size={20} color="#818cf8" /> 1. Select Algorithm & Configure Columns
        </h3>

        <form onSubmit={handleTrain}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px", marginBottom: "24px" }}>
            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "8px", color: "var(--text-muted)" }}>
                Machine Learning Algorithm
              </label>
              <select className="input-field" value={modelType} onChange={e => setModelType(e.target.value)}>
                <option value="linear">Linear Regression</option>
                <option value="random_forest">Random Forest Regressor</option>
                <option value="svr">Support Vector Regressor (SVR)</option>
                <option value="logistic">Logistic Regression (Classification)</option>
                <option value="xgboost">XGBoost Regressor</option>
              </select>
              <span style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "4px", display: "block" }}>
                Cost: 1 Token from your balance per training run.
              </span>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "8px", color: "var(--text-muted)" }}>
                Target / Prediction Label (Y)
              </label>
              <select className="input-field" value={targetLabel} onChange={handleTargetChange}>
                {columns.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              <span style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "4px", display: "block" }}>
                The dependent column you want your model to learn to predict.
              </span>
            </div>
          </div>

          {/* Features Multiselect */}
          <div style={{ marginBottom: "24px" }}>
            <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "10px", color: "var(--text-muted)" }}>
              Selected Input Features (X) &bull; ({selectedFeatures.length} selected)
            </label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {columns.filter(c => c !== targetLabel).map(col => {
                const isSelected = selectedFeatures.includes(col);
                return (
                  <button
                    key={col}
                    type="button"
                    onClick={() => toggleFeature(col)}
                    style={{
                      padding: "8px 16px",
                      borderRadius: "8px",
                      fontSize: "13px",
                      fontWeight: "600",
                      cursor: "pointer",
                      border: isSelected ? "1px solid #6366f1" : "1px solid var(--border-card)",
                      background: isSelected ? "rgba(99, 102, 241, 0.2)" : "rgba(255, 255, 255, 0.04)",
                      color: isSelected ? "#c7d2fe" : "var(--text-muted)",
                      transition: "all 0.15s ease",
                    }}
                  >
                    {isSelected ? "✓ " : "+ "}{col}
                  </button>
                );
              })}
            </div>
          </div>

          {error && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "12px 16px", background: "rgba(244, 63, 94, 0.15)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: "10px", color: "#fb7185", marginBottom: "20px", fontSize: "13px" }}>
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <button className="btn btn-primary" type="submit" disabled={training} style={{ padding: "12px 30px", fontSize: "15px" }}>
            {training ? <Sparkles className="animate-pulse-glow" size={18} /> : <Play size={18} />}
            {training ? "Training Model on Server..." : "Train Model Now"}
          </button>
        </form>
      </div>

      {/* STEP 2: PERFORMANCE METRICS */}
      {trainResult && (
        <div className="glass-card animate-fade-in" style={{ padding: "30px", marginBottom: "28px", border: "1px solid rgba(16, 185, 129, 0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
            <div style={{ width: "36px", height: "36px", borderRadius: "10px", background: "rgba(16, 185, 129, 0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <CheckCircle2 size={20} color="#34d399" />
            </div>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: "700" }}>Model Trained Successfully!</h3>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>Saved in models_storage/ as a Joblib binary</span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "16px", marginTop: "20px" }}>
            {Object.entries(trainResult.metrics || {}).map(([mName, val]) => (
              <div key={mName} style={{ background: "rgba(255, 255, 255, 0.03)", border: "1px solid var(--border-card)", borderRadius: "12px", padding: "16px" }}>
                <div style={{ fontSize: "12px", color: "var(--text-dim)", textTransform: "uppercase" }}>{mName}</div>
                <div style={{ fontSize: "24px", fontWeight: "800", color: "#38bdf8", marginTop: "4px" }}>
                  {typeof val === "number" ? val.toFixed(4) : val}
                </div>
              </div>
            ))}
          </div>

          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "14px" }}>
            * Note: These metrics are evaluated against the training split.
          </div>
        </div>
      )}

      {/* STEP 3: LIVE PREDICTION TESTING */}
      {trainResult && (
        <div className="glass-card animate-fade-in" style={{ padding: "30px", marginBottom: "28px" }}>
          <h3 style={{ fontSize: "18px", marginBottom: "12px", display: "flex", alignItems: "center", gap: "10px" }}>
            <Cpu size={20} color="#38bdf8" /> 2. Test Model with Real-Time Predictions
          </h3>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginBottom: "20px" }}>
            Input numeric values for each feature to invoke <code>/predict/{trainResult.model_name}</code> (Costs 5 tokens).
          </p>

          <form onSubmit={handlePredict}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginBottom: "20px" }}>
              {selectedFeatures.map(feat => (
                <div key={feat}>
                  <label style={{ display: "block", fontSize: "12px", fontWeight: "600", marginBottom: "6px", color: "var(--text-muted)" }}>
                    {feat}
                  </label>
                  <input
                    type="number"
                    step="any"
                    className="input-field"
                    value={predictInputs[feat] ?? ""}
                    onChange={e => setPredictInputs({ ...predictInputs, [feat]: e.target.value })}
                    required
                  />
                </div>
              ))}
            </div>

            {predictError && (
              <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "12px 16px", background: "rgba(244, 63, 94, 0.15)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: "10px", color: "#fb7185", marginBottom: "20px", fontSize: "13px" }}>
                <AlertCircle size={16} /> {predictError}
              </div>
            )}

            <button className="btn btn-emerald" type="submit" disabled={predicting}>
              <Play size={16} /> {predicting ? "Computing Prediction..." : "Generate Prediction"}
            </button>
          </form>

          {prediction !== null && (
            <div style={{ marginTop: "24px", padding: "20px", borderRadius: "12px", background: "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%)", border: "1px solid rgba(16, 185, 129, 0.4)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div>
                <div style={{ fontSize: "12px", textTransform: "uppercase", color: "#34d399", fontWeight: "700" }}>Predicted Output ({targetLabel})</div>
                <div style={{ fontSize: "32px", fontWeight: "900", color: "#ffffff", marginTop: "2px" }}>
                  {typeof prediction === "number" ? prediction.toLocaleString(undefined, { maximumFractionDigits: 4 }) : prediction}
                </div>
              </div>
              <span className="badge badge-emerald" style={{ padding: "6px 14px" }}>Inference Live</span>
            </div>
          )}
        </div>
      )}

      {/* STEP 4: TRAINED MODELS HISTORY */}
      <div className="glass-card" style={{ padding: "30px" }}>
        <h3 style={{ fontSize: "18px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "10px" }}>
          <History size={20} color="#c084fc" /> 3. Trained Model Registry
        </h3>

        {modelsList.length > 0 ? (
          <div className="custom-table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Model ID</th>
                  <th>Algorithm</th>
                  <th>Model Key</th>
                  <th>Target Label</th>
                  <th>Input Features</th>
                  <th>Train Count</th>
                  <th>Predict Count</th>
                  <th>Created UTC</th>
                </tr>
              </thead>
              <tbody>
                {modelsList.map(m => (
                  <tr key={m.id}>
                    <td>#{m.id}</td>
                    <td><span className="badge badge-purple">{m.model_type}</span></td>
                    <td style={{ fontWeight: "700" }}>{m.model_name}</td>
                    <td style={{ color: "#34d399" }}>{m.label}</td>
                    <td style={{ fontSize: "12px", color: "var(--text-muted)" }}>{m.features?.join(", ")}</td>
                    <td>{m.train_count}</td>
                    <td>{m.predict_count}</td>
                    <td style={{ fontSize: "11px", color: "var(--text-dim)" }}>{m.created_at?.split("T")?.[0]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>No models registered in the database yet.</p>
        )}
      </div>
    </div>
  );
}
