import React, { useState } from "react";
import { 
  Download, ArrowRight, RefreshCw, AlertTriangle, CheckCircle2, 
  Info, XCircle, BarChart3, Database, Layers, Hash, Activity, 
  TrendingUp, Table, Flame, FileSpreadsheet
} from "lucide-react";

export default function EdaPage({ edaData, datasetFile, onDownloadReport, onNavigate }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedColumn, setSelectedColumn] = useState(
    edaData?.columns_summary?.[0]?.name || ""
  );

  if (!edaData) {
    return (
      <div style={{ textAlign: "center", padding: "80px 20px" }}>
        <p style={{ color: "var(--text-muted)", marginBottom: "20px" }}>No EDA data found. Please upload a dataset first.</p>
        <button className="btn btn-primary" onClick={() => onNavigate("upload")}>
          Go to Upload Page
        </button>
      </div>
    );
  }

  const { overview: ov, columns_summary: cols, numeric_summary: numSum, categorical_summary: catSum, outliers_summary: outSum, correlation: corr } = edaData;
  const healthScore = ov?.health_score || 100;
  const healthColor = healthScore >= 80 ? "#10b981" : healthScore >= 60 ? "#f59e0b" : "#f43f5e";

  const numCols = cols.filter(c => c.is_numeric);
  const catCols = cols.filter(c => !c.is_numeric);

  // Selected column stats
  const activeColStats = numSum?.[selectedColumn];
  const activeCatStats = catSum?.[selectedColumn];
  const isSelectedNumeric = !!activeColStats;

  return (
    <div className="animate-fade-in" style={{ maxWidth: "1280px", margin: "0 auto", padding: "30px 24px 60px 24px" }}>
      {/* Top Banner */}
      <div className="glass-card" style={{ padding: "28px 32px", marginBottom: "28px", background: "linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "20px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
            <span className="badge badge-purple">Automated Profiler</span>
            <span style={{ fontSize: "14px", color: "var(--text-muted)" }}>Dataset: <strong style={{ color: "var(--text-main)" }}>{datasetFile?.name || "Uploaded Dataset"}</strong></span>
          </div>
          <h1 style={{ fontSize: "28px", fontWeight: "800", letterSpacing: "-0.02em" }}>
            Exploratory Data Analysis Studio
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "14px", marginTop: "4px" }}>
            Deep health diagnostics, descriptive statistics, interactive distributions, and feature correlation matrix.
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          <button className="btn btn-emerald" onClick={onDownloadReport}>
            <Download size={16} /> Download HTML Report
          </button>
          <button className="btn btn-secondary" onClick={() => onNavigate("upload")}>
            <RefreshCw size={15} /> Upload Different CSV
          </button>
        </div>
      </div>

      {/* KPI Stat Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginBottom: "28px" }}>
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "12px", textTransform: "uppercase", fontWeight: "600", marginBottom: "6px" }}>
            <span>Total Rows</span>
            <Database size={16} color="#818cf8" />
          </div>
          <div style={{ fontSize: "26px", fontWeight: "800", color: "#ffffff" }}>{ov?.num_rows?.toLocaleString()}</div>
          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "4px" }}>
            {ov?.duplicate_rows} duplicates ({ov?.duplicate_pct}%)
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "12px", textTransform: "uppercase", fontWeight: "600", marginBottom: "6px" }}>
            <span>Total Columns</span>
            <Layers size={16} color="#38bdf8" />
          </div>
          <div style={{ fontSize: "26px", fontWeight: "800", color: "#ffffff" }}>{ov?.num_cols}</div>
          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "4px" }}>
            {ov?.numeric_cols_count} Numeric &bull; {ov?.categorical_cols_count} Categorical
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "12px", textTransform: "uppercase", fontWeight: "600", marginBottom: "6px" }}>
            <span>Missing Cells</span>
            <AlertTriangle size={16} color={ov?.missing_cells > 0 ? "#f43f5e" : "#10b981"} />
          </div>
          <div style={{ fontSize: "26px", fontWeight: "800", color: ov?.missing_cells > 0 ? "#fb7185" : "#34d399" }}>
            {ov?.missing_pct}%
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "4px" }}>
            {ov?.missing_cells?.toLocaleString()} empty cells
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "12px", textTransform: "uppercase", fontWeight: "600", marginBottom: "6px" }}>
            <span>Memory Footprint</span>
            <Activity size={16} color="#c084fc" />
          </div>
          <div style={{ fontSize: "26px", fontWeight: "800", color: "#ffffff" }}>{ov?.memory_formatted}</div>
          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "4px" }}>
            {ov?.total_cells?.toLocaleString()} data points
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px", borderLeft: `4px solid ${healthColor}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "12px", textTransform: "uppercase", fontWeight: "600", marginBottom: "6px" }}>
            <span>Data Health Score</span>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: healthColor, display: "inline-block" }}></span>
          </div>
          <div style={{ fontSize: "26px", fontWeight: "800", color: healthColor }}>
            {healthScore} <span style={{ fontSize: "16px", color: "var(--text-dim)" }}>/ 100</span>
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginTop: "4px" }}>
            {healthScore >= 80 ? "Healthy Dataset" : healthScore >= 60 ? "Moderate Quality" : "Needs Cleaning"}
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid var(--border-card)", marginBottom: "28px", overflowX: "auto" }}>
        {[
          { id: "overview", label: "📋 Overview & Schema" },
          { id: "stats", label: "🔢 Descriptive Statistics" },
          { id: "distributions", label: "📊 Distributions & Outliers" },
          { id: "correlation", label: "🔗 Correlation Matrix" },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: "12px 20px",
              background: activeTab === tab.id ? "rgba(99, 102, 241, 0.15)" : "transparent",
              color: activeTab === tab.id ? "#818cf8" : "var(--text-muted)",
              border: "none",
              borderBottom: activeTab === tab.id ? "2px solid #6366f1" : "2px solid transparent",
              fontWeight: "600",
              fontSize: "14px",
              cursor: "pointer",
              transition: "all 0.2s ease",
              whiteSpace: "nowrap",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: OVERVIEW & SCHEMA */}
      {activeTab === "overview" && (
        <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Quality Alerts */}
          <div className="glass-card" style={{ padding: "24px" }}>
            <h3 style={{ fontSize: "16px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Activity size={18} color="#818cf8" /> Quality & Hygiene Alerts
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {ov?.quality_alerts?.map((alert, idx) => {
                const isSuccess = alert.type === "success";
                const isWarn = alert.type === "warning";
                const isDanger = alert.type === "danger";
                const bg = isSuccess ? "rgba(16, 185, 129, 0.1)" : isWarn ? "rgba(245, 158, 11, 0.1)" : isDanger ? "rgba(244, 63, 94, 0.1)" : "rgba(99, 102, 241, 0.1)";
                const border = isSuccess ? "rgba(16, 185, 129, 0.3)" : isWarn ? "rgba(245, 158, 11, 0.3)" : isDanger ? "rgba(244, 63, 94, 0.3)" : "rgba(99, 102, 241, 0.3)";
                const color = isSuccess ? "#34d399" : isWarn ? "#fbbf24" : isDanger ? "#fb7185" : "#818cf8";
                const IconComp = isSuccess ? CheckCircle2 : isWarn ? AlertTriangle : isDanger ? XCircle : Info;

                return (
                  <div key={idx} style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px 16px", borderRadius: "10px", background: bg, border: `1px solid ${border}`, color: "var(--text-main)", fontSize: "13px" }}>
                    <IconComp size={16} color={color} style={{ flexShrink: 0 }} />
                    <span>{alert.message}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Schema Breakdown Table */}
          <div className="glass-card" style={{ padding: "24px" }}>
            <h3 style={{ fontSize: "16px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Table size={18} color="#38bdf8" /> Column Schema & Null Analysis
            </h3>
            <div className="custom-table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Column Name</th>
                    <th>Data Type</th>
                    <th>Type Category</th>
                    <th>Non-Null Count</th>
                    <th>Missing Count</th>
                    <th>Missing %</th>
                    <th>Unique Values</th>
                    <th>Sample Preview</th>
                  </tr>
                </thead>
                <tbody>
                  {cols.map((col, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: "700" }}>{col.name}</td>
                      <td><code style={{ background: "rgba(255, 255, 255, 0.06)", padding: "2px 6px", borderRadius: "4px" }}>{col.dtype}</code></td>
                      <td>
                        <span className={`badge ${col.is_numeric ? "badge-cyan" : "badge-purple"}`}>
                          {col.is_numeric ? "Numeric" : "Categorical"}
                        </span>
                      </td>
                      <td>{col.non_null?.toLocaleString()}</td>
                      <td>
                        <span style={{ color: col.null_count > 0 ? "#fb7185" : "inherit" }}>
                          {col.null_count?.toLocaleString()}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <div style={{ width: "60px", height: "6px", background: "#1e293b", borderRadius: "3px", overflow: "hidden" }}>
                            <div style={{ width: `${Math.min(100, col.null_pct)}%`, height: "100%", background: "#f43f5e" }}></div>
                          </div>
                          <span style={{ fontSize: "12px", color: col.null_count > 0 ? "#fb7185" : "var(--text-dim)" }}>
                            {col.null_pct}%
                          </span>
                        </div>
                      </td>
                      <td>{col.unique_count?.toLocaleString()} ({col.unique_pct}%)</td>
                      <td style={{ color: "var(--text-muted)", fontSize: "12px" }}>
                        {col.sample_values?.slice(0, 3).join(", ") || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: DESCRIPTIVE STATISTICS */}
      {activeTab === "stats" && (
        <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Numerical Variables */}
          {Object.keys(numSum || {}).length > 0 && (
            <div className="glass-card" style={{ padding: "24px" }}>
              <h3 style={{ fontSize: "16px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                <Hash size={18} color="#38bdf8" /> Numerical Features Summary
              </h3>
              <div className="custom-table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Feature</th>
                      <th>Count</th>
                      <th>Mean</th>
                      <th>Std Dev</th>
                      <th>Min</th>
                      <th>25% (Q1)</th>
                      <th>Median (50%)</th>
                      <th>75% (Q3)</th>
                      <th>Max</th>
                      <th>IQR</th>
                      <th>Skewness</th>
                      <th>Outliers (IQR)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(numSum).map(([feat, s], idx) => (
                      <tr key={idx}>
                        <td style={{ fontWeight: "700" }}>{feat}</td>
                        <td>{s.count?.toLocaleString()}</td>
                        <td>{s.mean?.toLocaleString()}</td>
                        <td>{s.std?.toLocaleString()}</td>
                        <td>{s.min?.toLocaleString()}</td>
                        <td>{s.q25?.toLocaleString()}</td>
                        <td style={{ fontWeight: "700", color: "#38bdf8" }}>{s.median?.toLocaleString()}</td>
                        <td>{s.q75?.toLocaleString()}</td>
                        <td>{s.max?.toLocaleString()}</td>
                        <td>{s.iqr?.toLocaleString()}</td>
                        <td>{s.skew}</td>
                        <td>
                          <span style={{ color: s.outliers_count > 0 ? "#fb7185" : "var(--text-muted)", fontWeight: s.outliers_count > 0 ? "700" : "400" }}>
                            {s.outliers_count} ({s.outliers_pct}%)
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Categorical Variables */}
          {Object.keys(catSum || {}).length > 0 && (
            <div className="glass-card" style={{ padding: "24px" }}>
              <h3 style={{ fontSize: "16px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                <Layers size={18} color="#c084fc" /> Categorical Features Summary
              </h3>
              <div className="custom-table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Feature</th>
                      <th>Valid Count</th>
                      <th>Unique Categories</th>
                      <th>Top Mode Value</th>
                      <th>Top Frequency</th>
                      <th>Top Dominance %</th>
                      <th>Category Distribution Sample</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(catSum).map(([feat, s], idx) => (
                      <tr key={idx}>
                        <td style={{ fontWeight: "700" }}>{feat}</td>
                        <td>{s.count?.toLocaleString()}</td>
                        <td>{s.unique?.toLocaleString()}</td>
                        <td style={{ fontWeight: "700", color: "#c084fc" }}>{s.top_value}</td>
                        <td>{s.top_freq?.toLocaleString()}</td>
                        <td>{s.top_pct}%</td>
                        <td style={{ color: "var(--text-muted)", fontSize: "12px" }}>
                          {s.distribution?.slice(0, 3).map(d => `${d.label} (${d.count})`).join(", ")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: DISTRIBUTIONS & OUTLIERS */}
      {activeTab === "distributions" && (
        <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <div className="glass-card" style={{ padding: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px", marginBottom: "20px" }}>
              <div>
                <h3 style={{ fontSize: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <BarChart3 size={18} color="#818cf8" /> Univariate Distribution Inspector
                </h3>
                <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>Choose a column to inspect its distribution and spread metrics.</p>
              </div>

              <select
                className="input-field"
                value={selectedColumn}
                onChange={(e) => setSelectedColumn(e.target.value)}
                style={{ width: "240px" }}
              >
                {cols.map(c => (
                  <option key={c.name} value={c.name}>{c.name} ({c.is_numeric ? "Numeric" : "Categorical"})</option>
                ))}
              </select>
            </div>

            {isSelectedNumeric && activeColStats ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px" }}>
                {/* Metrics Breakdown */}
                <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--border-card)", borderRadius: "12px", padding: "20px" }}>
                  <h4 style={{ fontSize: "14px", color: "var(--text-muted)", marginBottom: "16px" }}>Detailed Metrics for <code>{selectedColumn}</code></h4>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                    <div>
                      <div style={{ fontSize: "12px", color: "var(--text-dim)" }}>Mean</div>
                      <div style={{ fontSize: "18px", fontWeight: "700" }}>{activeColStats.mean?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "12px", color: "var(--text-dim)" }}>Median</div>
                      <div style={{ fontSize: "18px", fontWeight: "700", color: "#38bdf8" }}>{activeColStats.median?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "12px", color: "var(--text-dim)" }}>Std Deviation</div>
                      <div style={{ fontSize: "16px", fontWeight: "600" }}>{activeColStats.std?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "12px", color: "var(--text-dim)" }}>Min &bull; Max</div>
                      <div style={{ fontSize: "14px", fontWeight: "600" }}>{activeColStats.min} &rarr; {activeColStats.max}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "12px", color: "var(--text-dim)" }}>IQR Range</div>
                      <div style={{ fontSize: "16px", fontWeight: "600" }}>{activeColStats.iqr}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "12px", color: "var(--text-dim)" }}>Skewness</div>
                      <div style={{ fontSize: "16px", fontWeight: "600" }}>{activeColStats.skew}</div>
                    </div>
                  </div>

                  <div style={{ marginTop: "20px", padding: "12px", borderRadius: "8px", background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
                    <div style={{ fontSize: "12px", color: "#a5b4fc" }}>Distribution Shape:</div>
                    <div style={{ fontSize: "13px", fontWeight: "600", marginTop: "2px" }}>
                      {Math.abs(activeColStats.skew) < 0.5 ? "Approximately Symmetric (Normal-like)" : activeColStats.skew > 0 ? "Right-Skewed (Long tail on positive side)" : "Left-Skewed (Long tail on negative side)"}
                    </div>
                  </div>
                </div>

                {/* Outliers info */}
                <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--border-card)", borderRadius: "12px", padding: "20px" }}>
                  <h4 style={{ fontSize: "14px", color: "var(--text-muted)", marginBottom: "16px" }}>Outlier Boundary (Tukey's IQR 1.5x)</h4>
                  <div style={{ marginBottom: "16px" }}>
                    <div style={{ fontSize: "12px", color: "var(--text-dim)" }}>Detected Outliers</div>
                    <div style={{ fontSize: "24px", fontWeight: "800", color: activeColStats.outliers_count > 0 ? "#fb7185" : "#34d399" }}>
                      {activeColStats.outliers_count} <span style={{ fontSize: "14px", color: "var(--text-dim)" }}>({activeColStats.outliers_pct}%)</span>
                    </div>
                  </div>
                  <div style={{ fontSize: "13px", color: "var(--text-muted)", lineHeight: "1.7" }}>
                    &bull; Values below <code>{activeColStats.q25 - 1.5 * activeColStats.iqr}</code> or above <code>{activeColStats.q75 + 1.5 * activeColStats.iqr}</code> are tagged as outliers.
                  </div>
                </div>
              </div>
            ) : activeCatStats ? (
              <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--border-card)", borderRadius: "12px", padding: "20px" }}>
                <h4 style={{ fontSize: "14px", color: "var(--text-muted)", marginBottom: "14px" }}>Top Categories in <code>{selectedColumn}</code></h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {activeCatStats.distribution?.map((item, idx) => (
                    <div key={idx} style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <span style={{ width: "120px", fontSize: "13px", fontWeight: "600", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {item.label}
                      </span>
                      <div style={{ flex: 1, height: "10px", background: "#1e293b", borderRadius: "5px", overflow: "hidden" }}>
                        <div style={{ width: `${item.pct}%`, height: "100%", background: "linear-gradient(90deg, #6366f1, #a855f7)" }}></div>
                      </div>
                      <span style={{ width: "80px", textAlign: "right", fontSize: "12px", color: "var(--text-muted)" }}>
                        {item.count} ({item.pct}%)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>

          {/* Outliers Table */}
          <div className="glass-card" style={{ padding: "24px" }}>
            <h3 style={{ fontSize: "16px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
              <TrendingUp size={18} color="#f43f5e" /> Outlier Diagnostics Table (All Numeric Columns)
            </h3>
            <div className="custom-table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th>Lower Bound (Q1 - 1.5*IQR)</th>
                    <th>Upper Bound (Q3 + 1.5*IQR)</th>
                    <th>Outlier Count</th>
                    <th>Outlier %</th>
                    <th>Cleanliness Status</th>
                  </tr>
                </thead>
                <tbody>
                  {outSum?.map((o, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: "700" }}>{o.column}</td>
                      <td>{o.lower_bound}</td>
                      <td>{o.upper_bound}</td>
                      <td style={{ fontWeight: "700", color: o.outliers_count > 0 ? "#fb7185" : "inherit" }}>{o.outliers_count}</td>
                      <td>{o.outliers_pct}%</td>
                      <td>
                        <span className={`badge ${o.outliers_count > 0 ? "badge-rose" : "badge-emerald"}`}>
                          {o.outliers_count > 0 ? "Outliers Present" : "Clean"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: CORRELATIONS */}
      {activeTab === "correlation" && (
        <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <div className="glass-card" style={{ padding: "24px" }}>
            <h3 style={{ fontSize: "16px", marginBottom: "8px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Flame size={18} color="#f97316" /> Pearson Feature Correlation Heatmap
            </h3>
            <p style={{ color: "var(--text-muted)", fontSize: "13px", marginBottom: "20px" }}>
              Calculates linear pairwise correlations across all continuous numeric variables.
            </p>

            {corr?.columns && corr.columns.length >= 2 ? (
              <>
                <div className="custom-table-container" style={{ marginBottom: "24px" }}>
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Feature</th>
                        {corr.columns.map(c => <th key={c}>{c}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {corr.columns.map((rowCol, i) => (
                        <tr key={rowCol}>
                          <td style={{ fontWeight: "700", background: "rgba(255, 255, 255, 0.03)" }}>{rowCol}</td>
                          {corr.matrix[i].map((val, j) => {
                            const isSelf = i === j;
                            const isHigh = Math.abs(val) >= 0.70 && !isSelf;
                            const isPos = val > 0;
                            const bg = isSelf 
                              ? "rgba(255, 255, 255, 0.08)"
                              : isPos 
                                ? `rgba(99, 102, 241, ${Math.min(0.9, Math.abs(val) * 0.8 + 0.15)})`
                                : `rgba(244, 63, 94, ${Math.min(0.9, Math.abs(val) * 0.8 + 0.15)})`;
                            return (
                              <td 
                                key={j} 
                                style={{ 
                                  backgroundColor: bg, 
                                  textAlign: "center", 
                                  fontWeight: "700", 
                                  color: isSelf ? "#94a3b8" : "#ffffff",
                                  border: isHigh ? "1px solid rgba(255, 255, 255, 0.4)" : "none"
                                }}
                              >
                                {val.toFixed(2)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Multicollinearity Warning Cards */}
                {corr.high_correlations && corr.high_correlations.length > 0 && (
                  <div style={{ marginTop: "16px" }}>
                    <h4 style={{ fontSize: "14px", color: "#fbbf24", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                      <AlertTriangle size={16} /> Strong Multicollinearity Warning (|r| &ge; 0.70)
                    </h4>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "12px" }}>
                      {corr.high_correlations.map((pair, idx) => (
                        <div key={idx} style={{ background: "rgba(245, 158, 11, 0.08)", border: "1px solid rgba(245, 158, 11, 0.25)", borderRadius: "10px", padding: "12px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <div>
                            <span style={{ fontWeight: "700" }}>{pair.col1}</span> &bull; <span style={{ fontWeight: "700" }}>{pair.col2}</span>
                            <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                              {pair.correlation > 0 ? "Strong Positive Linear Correlation" : "Strong Negative Linear Correlation"}
                            </div>
                          </div>
                          <span style={{ fontWeight: "800", color: "#fbbf24", background: "rgba(0, 0, 0, 0.3)", padding: "4px 10px", borderRadius: "6px" }}>
                            r = {pair.correlation}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
                At least 2 numeric features with variation are required to compute a correlation matrix.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Bottom Next Step Call-To-Action */}
      <div className="glass-card" style={{ marginTop: "32px", padding: "28px", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "20px", background: "linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)", border: "1px solid rgba(99, 102, 241, 0.25)" }}>
        <div>
          <h3 style={{ fontSize: "18px", fontWeight: "700", marginBottom: "4px" }}>Ready to Train a Machine Learning Model?</h3>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
            Select target columns, choose algorithms (Linear, Random Forest, SVR, XGBoost), and test live predictions in real time.
          </p>
        </div>
        <button className="btn btn-primary" style={{ padding: "12px 28px", fontSize: "15px" }} onClick={() => onNavigate("train")}>
          Proceed to Model Training <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
}
