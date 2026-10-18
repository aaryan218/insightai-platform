import React, { useState, useEffect } from "react";
import { Upload, BarChart3, Brain, LogOut, Coins, Plus, FileSpreadsheet, Sparkles } from "lucide-react";
import { api } from "./api";
import AuthModal from "./components/AuthModal";
import UploadPage from "./components/UploadPage";
import EdaPage from "./components/EdaPage";
import TrainPage from "./components/TrainPage";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(api.isAuthenticated());
  const [user, setUser] = useState(api.getUser());
  const [tokens, setTokens] = useState(0);

  // App workflow state
  const [currentPage, setCurrentPage] = useState("upload"); // "upload" | "eda" | "train"
  const [datasetFile, setDatasetFile] = useState(null);
  const [edaData, setEdaData] = useState(null);
  const [loadingEda, setLoadingEda] = useState(false);
  const [loadingTokens, setLoadingTokens] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user) {
      refreshTokens();
    }
  }, [isAuthenticated, user]);

  const refreshTokens = async () => {
    if (!user) return;
    try {
      const t = await api.getTokens(user);
      setTokens(t);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddTokens = async () => {
    setLoadingTokens(true);
    try {
      const newTokens = await api.addTokens(user, 20);
      setTokens(newTokens);
    } catch (e) {
      alert("Error adding tokens: " + e.message);
    } finally {
      setLoadingTokens(false);
    }
  };

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
    setUser(null);
    setDatasetFile(null);
    setEdaData(null);
    setCurrentPage("upload");
  };

  // Upload & auto-redirect logic
  const handleFileUpload = async (file) => {
    setDatasetFile(file);
    setLoadingEda(true);
    try {
      // Run EDA profiling on backend
      const edaResult = await api.runEda(file);
      setEdaData(edaResult);

      // AUTOMATIC REDIRECTION:
      setCurrentPage("eda");
    } catch (err) {
      alert("Error generating EDA: " + err.message);
    } finally {
      setLoadingEda(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!datasetFile) return;
    try {
      await api.downloadEdaReport(datasetFile);
    } catch (e) {
      alert("Download failed: " + e.message);
    }
  };

  if (!isAuthenticated) {
    return (
      <AuthModal
        onLoginSuccess={() => {
          setIsAuthenticated(true);
          setUser(api.getUser());
        }}
      />
    );
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Top Navbar */}
      <header
        style={{
          height: "70px",
          borderBottom: "1px solid var(--border-card)",
          background: "rgba(10, 14, 23, 0.8)",
          backdropFilter: "blur(16px)",
          position: "sticky",
          top: 0,
          zIndex: 50,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 28px",
        }}
      >
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", cursor: "pointer" }} onClick={() => setCurrentPage("upload")}>
          <div style={{ width: "38px", height: "38px", borderRadius: "10px", background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 12px rgba(99, 102, 241, 0.4)" }}>
            <Sparkles size={20} color="#ffffff" />
          </div>
          <div>
            <span style={{ fontSize: "17px", fontWeight: "800", letterSpacing: "-0.02em" }}>MLWorkbench</span>
            <span style={{ fontSize: "11px", color: "#38bdf8", display: "block", fontWeight: "600" }}>FastAPI &bull; React Suite</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <button
            className="btn"
            onClick={() => setCurrentPage("upload")}
            style={{
              background: currentPage === "upload" ? "rgba(99, 102, 241, 0.15)" : "transparent",
              color: currentPage === "upload" ? "#818cf8" : "var(--text-muted)",
              border: currentPage === "upload" ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
              padding: "8px 16px",
              fontSize: "13px",
            }}
          >
            <Upload size={15} /> 1. Upload
          </button>

          <button
            className="btn"
            onClick={() => {
              if (edaData) setCurrentPage("eda");
              else alert("Please upload a CSV dataset first!");
            }}
            style={{
              background: currentPage === "eda" ? "rgba(99, 102, 241, 0.15)" : "transparent",
              color: currentPage === "eda" ? "#818cf8" : "var(--text-muted)",
              border: currentPage === "eda" ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
              padding: "8px 16px",
              fontSize: "13px",
              opacity: edaData ? 1 : 0.5,
            }}
          >
            <BarChart3 size={15} /> 2. Auto EDA
          </button>

          <button
            className="btn"
            onClick={() => {
              if (datasetFile) setCurrentPage("train");
              else alert("Please upload a CSV dataset first!");
            }}
            style={{
              background: currentPage === "train" ? "rgba(99, 102, 241, 0.15)" : "transparent",
              color: currentPage === "train" ? "#818cf8" : "var(--text-muted)",
              border: currentPage === "train" ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid transparent",
              padding: "8px 16px",
              fontSize: "13px",
              opacity: datasetFile ? 1 : 0.5,
            }}
          >
            <Brain size={15} /> 3. Model Studio
          </button>
        </nav>

        {/* User & Wallet */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          {/* Tokens pill */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              background: "rgba(16, 185, 129, 0.12)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              padding: "6px 14px",
              borderRadius: "20px",
            }}
          >
            <Coins size={15} color="#34d399" />
            <span style={{ fontSize: "13px", fontWeight: "700", color: "#34d399" }}>
              {tokens} Tokens
            </span>
            <button
              onClick={handleAddTokens}
              disabled={loadingTokens}
              title="Add 20 Demo Tokens"
              style={{
                background: "rgba(16, 185, 129, 0.3)",
                border: "none",
                borderRadius: "50%",
                width: "20px",
                height: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                color: "#ffffff",
                marginLeft: "4px",
              }}
            >
              <Plus size={12} />
            </button>
          </div>

          {/* User & Logout */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
              User: <strong style={{ color: "#ffffff" }}>{user}</strong>
            </span>
            <button
              onClick={handleLogout}
              className="btn btn-secondary"
              style={{ padding: "6px 12px", fontSize: "12px" }}
              title="Logout"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </header>

      {/* Loading Overlay */}
      {loadingEda && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(10, 14, 23, 0.85)",
            backdropFilter: "blur(8px)",
            zIndex: 100,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "16px",
          }}
        >
          <div
            className="animate-pulse-glow"
            style={{
              width: "60px",
              height: "60px",
              borderRadius: "20px",
              background: "linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 30px rgba(99, 102, 241, 0.5)",
            }}
          >
            <Sparkles size={32} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: "20px", fontWeight: "700" }}>Analyzing Dataset & Generating EDA...</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
            Computing statistics, correlations, quality checks, and distributions...
          </p>
        </div>
      )}

      {/* Main Content Pages */}
      <main style={{ flex: 1 }}>
        {currentPage === "upload" && (
          <UploadPage
            onFileUpload={handleFileUpload}
            activeDataset={datasetFile}
            onNavigate={setCurrentPage}
          />
        )}

        {currentPage === "eda" && (
          <EdaPage
            edaData={edaData}
            datasetFile={datasetFile}
            onDownloadReport={handleDownloadReport}
            onNavigate={setCurrentPage}
          />
        )}

        {currentPage === "train" && (
          <TrainPage
            datasetFile={datasetFile}
            onNavigate={setCurrentPage}
            onTokensUpdated={refreshTokens}
          />
        )}
      </main>
    </div>
  );
}
