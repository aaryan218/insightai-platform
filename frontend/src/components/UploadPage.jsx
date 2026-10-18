import React, { useState } from "react";
import { Upload, FileSpreadsheet, Sparkles, AlertCircle, ArrowRight, ShieldCheck, Zap } from "lucide-react";

export default function UploadPage({ onFileUpload, activeDataset, onNavigate }) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    if (!file.name.endsWith(".csv")) {
      setError("Please upload a valid tabular CSV file (.csv)");
      return;
    }
    setError(null);
    onFileUpload(file);
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: "1000px", margin: "0 auto", padding: "40px 20px" }}>
      {/* Hero Header */}
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", background: "rgba(99, 102, 241, 0.12)", border: "1px solid rgba(99, 102, 241, 0.3)", padding: "6px 16px", borderRadius: "30px", marginBottom: "16px" }}>
          <Sparkles size={16} color="#818cf8" />
          <span style={{ fontSize: "13px", fontWeight: "600", color: "#818cf8" }}>Automated Machine Learning & Analytics</span>
        </div>
        <h1 style={{ fontSize: "40px", fontWeight: "800", background: "linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", marginBottom: "12px", letterSpacing: "-0.03em" }}>
          Upload Your Dataset
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: "17px", maxWidth: "620px", margin: "0 auto" }}>
          Drop your CSV below. The system will <span style={{ color: "#38bdf8", fontWeight: "600" }}>instantly redirect you to the Auto EDA studio</span> with full health diagnostics, statistics, charts, and correlation matrix.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div
        className="glass-card"
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{
          padding: "60px 40px",
          textAlign: "center",
          border: dragActive ? "2px dashed #6366f1" : "2px dashed rgba(255, 255, 255, 0.15)",
          backgroundColor: dragActive ? "rgba(99, 102, 241, 0.08)" : "var(--bg-card)",
          boxShadow: dragActive ? "0 0 30px rgba(99, 102, 241, 0.25)" : "var(--shadow-md)",
          cursor: "pointer",
          position: "relative",
          marginBottom: "36px",
          transition: "all 0.25s ease",
        }}
      >
        <input
          type="file"
          accept=".csv"
          onChange={handleChange}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            opacity: 0,
            cursor: "pointer",
          }}
        />

        <div style={{ width: "80px", height: "80px", borderRadius: "20px", background: "linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)", border: "1px solid rgba(255, 255, 255, 0.1)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px auto" }}>
          <Upload size={36} color="#818cf8" />
        </div>

        <h3 style={{ fontSize: "20px", fontWeight: "700", marginBottom: "8px" }}>
          Drag and drop your CSV file here
        </h3>
        <p style={{ color: "var(--text-muted)", fontSize: "14px", marginBottom: "20px" }}>
          Supported file type: <code style={{ color: "#38bdf8", background: "rgba(6, 182, 212, 0.1)", padding: "2px 8px", borderRadius: "6px" }}>.csv</code> (Max size: 50MB)
        </p>

        <button className="btn btn-primary" type="button" style={{ pointerEvents: "none" }}>
          <FileSpreadsheet size={16} /> Browse Files
        </button>

        {error && (
          <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", marginTop: "20px", background: "rgba(244, 63, 94, 0.15)", border: "1px solid rgba(244, 63, 94, 0.3)", color: "#fb7185", padding: "8px 16px", borderRadius: "8px", fontSize: "13px" }}>
            <AlertCircle size={15} /> {error}
          </div>
        )}
      </div>

      {/* Active Dataset Shortcut (If already loaded) */}
      {activeDataset && (
        <div className="glass-card" style={{ padding: "24px 28px", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px", background: "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%)", border: "1px solid rgba(16, 185, 129, 0.25)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ width: "48px", height: "48px", borderRadius: "12px", background: "rgba(16, 185, 129, 0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <FileSpreadsheet size={24} color="#34d399" />
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontWeight: "700", fontSize: "16px" }}>{activeDataset.name}</span>
                <span className="badge badge-emerald">Active Dataset</span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
                Ready in memory. You can jump directly to the auto-generated EDA studio or model training.
              </p>
            </div>
          </div>
          <div style={{ display: "flex", gap: "12px" }}>
            <button className="btn btn-emerald" onClick={() => onNavigate("eda")}>
              View Auto EDA <ArrowRight size={16} />
            </button>
            <button className="btn btn-secondary" onClick={() => onNavigate("train")}>
              Train Model
            </button>
          </div>
        </div>
      )}

      {/* Feature Highlights Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px", marginTop: "40px" }}>
        <div className="glass-card" style={{ padding: "22px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
            <div style={{ background: "rgba(99, 102, 241, 0.2)", padding: "8px", borderRadius: "10px" }}>
              <Zap size={18} color="#818cf8" />
            </div>
            <h4 style={{ fontSize: "15px" }}>Instant Auto Redirection</h4>
          </div>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", lineHeight: "1.6" }}>
            No extra clicks. Selecting a CSV immediately runs full backend profiling and transports you directly to the EDA studio.
          </p>
        </div>

        <div className="glass-card" style={{ padding: "22px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
            <div style={{ background: "rgba(6, 182, 212, 0.2)", padding: "8px", borderRadius: "10px" }}>
              <ShieldCheck size={18} color="#22d3ee" />
            </div>
            <h4 style={{ fontSize: "15px" }}>Comprehensive Health Score</h4>
          </div>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", lineHeight: "1.6" }}>
            Automated quality diagnostics covering missing values, duplicate records, zero variance, and multicollinearity alerts.
          </p>
        </div>

        <div className="glass-card" style={{ padding: "22px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
            <div style={{ background: "rgba(168, 85, 247, 0.2)", padding: "8px", borderRadius: "10px" }}>
              <Sparkles size={18} color="#c084fc" />
            </div>
            <h4 style={{ fontSize: "15px" }}>Downloadable HTML Report</h4>
          </div>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", lineHeight: "1.6" }}>
            Export an interactive, self-contained HTML report with full summary tables and correlation heatmaps for offline review.
          </p>
        </div>
      </div>
    </div>
  );
}
