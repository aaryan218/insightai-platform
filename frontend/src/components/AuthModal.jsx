import React, { useState } from "react";
import { Lock, User, KeyRound, Sparkles, AlertCircle } from "lucide-react";
import { api } from "../api";

export default function AuthModal({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        await api.login(username, password);
        onLoginSuccess();
      } else {
        await api.signup(username, password);
        // auto login after signup
        await api.login(username, password);
        onLoginSuccess();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "20px" }}>
      <div className="glass-card animate-fade-in" style={{ width: "100%", maxWidth: "440px", padding: "40px" }}>
        <div style={{ textAlign: "center", marginBottom: "30px" }}>
          <div style={{ width: "56px", height: "56px", borderRadius: "16px", background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px auto", boxShadow: "0 8px 24px rgba(99, 102, 241, 0.4)" }}>
            <Sparkles size={28} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: "24px", fontWeight: "800", marginBottom: "6px" }}>MLWorkbench</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
            {isLogin ? "Sign in to access your models and datasets" : "Create your ML workbench account"}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "18px" }}>
            <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "6px", color: "var(--text-muted)" }}>
              Username
            </label>
            <div style={{ position: "relative" }}>
              <User size={16} color="#64748b" style={{ position: "absolute", left: "14px", top: "14px" }} />
              <input
                type="text"
                className="input-field"
                placeholder="e.g. aaryan"
                style={{ paddingLeft: "40px" }}
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "6px", color: "var(--text-muted)" }}>
              Password
            </label>
            <div style={{ position: "relative" }}>
              <KeyRound size={16} color="#64748b" style={{ position: "absolute", left: "14px", top: "14px" }} />
              <input
                type="password"
                className="input-field"
                placeholder="••••••••"
                style={{ paddingLeft: "40px" }}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {error && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "12px", background: "rgba(244, 63, 94, 0.15)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: "10px", color: "#fb7185", marginBottom: "20px", fontSize: "13px" }}>
              <AlertCircle size={15} /> {error}
            </div>
          )}

          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%", padding: "12px", fontSize: "15px" }}>
            {loading ? "Processing..." : isLogin ? "Sign In" : "Create Free Account"}
          </button>
        </form>

        <div style={{ textAlign: "center", marginTop: "24px", fontSize: "13px", color: "var(--text-muted)" }}>
          {isLogin ? "Don't have an account yet?" : "Already have an account?"}{" "}
          <button
            type="button"
            onClick={() => { setIsLogin(!isLogin); setError(null); }}
            style={{ background: "none", border: "none", color: "#818cf8", fontWeight: "600", cursor: "pointer" }}
          >
            {isLogin ? "Sign Up" : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}
