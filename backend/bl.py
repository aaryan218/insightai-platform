# Buisness Logic layer
import io, os, time, hashlib, logging
from typing import Dict, Any, List
import pandas as pd

from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score

from models import MODEL_REGISTRY
from dal import (
    create_user, get_user, delete_user, add_tokens, get_tokens, deduct_tokens,
    insert_model_meta, save_model, load_model, list_models, get_latest_model,
    inc_user, inc_model, MODELS_DIR
)

# ===== Logs =====
logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===== Hash  =====
_SALT = "basic_salt"
def hash_password(pw: str) -> str:
    return hashlib.sha256(f"{_SALT}:{pw}".encode("utf-8")).hexdigest()

# ===== Users =====
def bl_signup(username: str, password: str) -> None:
    if get_user(username):
        raise ValueError("User exists")
    create_user(username, hash_password(password))
    logging.info(f"User {username} registered")

def bl_login(username: str, password: str) -> bool:
    u = get_user(username)
    return bool(u and u["password_hash"] == hash_password(password))

def bl_delete_user(username: str, password: str) -> None:
    u = get_user(username)
    if not u or u["password_hash"] != hash_password(password):
        raise ValueError("Bad credentials")
    delete_user(username)
    logging.info(f"User {username} deleted")

def bl_add_tokens(username: str, amount: int) -> int:
    add_tokens(username, amount)
    logging.info(f"User {username} added {amount} tokens")
    return get_tokens(username)

def bl_get_tokens(username: str) -> int:
    return get_tokens(username)

def require_tokens(username: str, amount: int) -> None:
    if not deduct_tokens(username, amount):
        raise ValueError("Not enough tokens")

# ===== Data =====
def df_from_upload(bytes_data: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(bytes_data))

# ===== Train =====
def train_model(username: str, df: pd.DataFrame,
                model_name: str, features: List[str], label: str,
                model_params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if model_name not in MODEL_REGISTRY:
        raise ValueError("Unknown model")
    info = MODEL_REGISTRY[model_name]
    Model = info["ctor"]
    model_type = info["type"]

    missing = [c for c in features + [label] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    X = df[features].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[label], errors="coerce") if model_type == "regression" else df[label]

    tmp = pd.concat([X, y], axis=1).dropna()
    X, y = tmp[features], tmp[label]

    model = Model(**(model_params or {}))
    model.fit(X, y)

    metrics: Dict[str, float] = {}
    if model_type == "regression":
        yhat = model.predict(X)
        metrics["MAE"] = float(mean_absolute_error(y, yhat))
        metrics["R2"] = float(r2_score(y, yhat))
    else:
        yhat = model.predict(X)
        metrics["ACC"] = float(accuracy_score(y, yhat))
        metrics["F1"]  = float(f1_score(y, yhat, average="weighted"))

    fname = f"{username}_{model_name}_{int(time.time())}.pkl"
    fpath = os.path.join(MODELS_DIR, fname)
    save_model(fpath, model)
    meta = insert_model_meta(username, model_name, model_type, features, label, fpath)

    logging.info(f"User {username} trained {model_name} ({model_type}) feats={features} label={label}")
    return {
        "status": "model trained",
        "model_name": model_name,
        "features": features,
        "label": label,
        "metrics": metrics,
        "created_at": meta["created_at"]
    }

# ===== Predict =====
def predict_latest(username: str, model_name: str, payload: Dict[str, Any]) -> float | int:
    meta = get_latest_model(username, model_name)
    if not meta:
        raise ValueError("Model not found")
    model = load_model(meta["path"])
    feats = meta["features"]
    X = pd.DataFrame([{f: payload.get(f, None) for f in feats}], columns=feats).apply(pd.to_numeric, errors="coerce")
    if X.isna().any().any():
        raise ValueError("Missing or non-numeric features")
    pred = model.predict(X)
    inc_user(username, "predict_count", 1)
    inc_model(meta["id"], "predict_count", 1)
    logging.info(f"User {username} predict via {model_name}")
    val = pred[0] if hasattr(pred, "__len__") else pred
    try:
        return float(val)
    except Exception:
        return int(val)

def list_user_models(username: str) -> List[Dict[str, Any]]:
    return list_models(username)


# ===== EDA (Exploratory Data Analysis) =====
def compute_eda(df: pd.DataFrame) -> Dict[str, Any]:
    num_rows = int(len(df))
    num_cols = int(len(df.columns))
    total_cells = int(df.size)
    missing_cells = int(df.isna().sum().sum())
    missing_pct = float(round((missing_cells / total_cells * 100), 2)) if total_cells > 0 else 0.0
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = float(round((duplicate_rows / num_rows * 100), 2)) if num_rows > 0 else 0.0

    mem_bytes = int(df.memory_usage(deep=True).sum())
    if mem_bytes < 1024:
        mem_fmt = f"{mem_bytes} B"
    elif mem_bytes < 1024 * 1024:
        mem_fmt = f"{mem_bytes / 1024:.1f} KB"
    else:
        mem_fmt = f"{mem_bytes / (1024 * 1024):.2f} MB"

    columns_summary = []
    numeric_summary = {}
    categorical_summary = {}
    outliers_summary = []
    quality_alerts = []

    numeric_cols = []
    categorical_cols = []

    for col in df.columns:
        s = df[col]
        non_null = int(s.notna().sum())
        null_count = int(s.isna().sum())
        null_pct = float(round(null_count / num_rows * 100, 2)) if num_rows > 0 else 0.0
        unique_count = int(s.nunique(dropna=True))
        unique_pct = float(round(unique_count / non_null * 100, 2)) if non_null > 0 else 0.0
        is_num = bool(pd.api.types.is_numeric_dtype(s))

        sample_vals = [str(x) for x in s.dropna().head(4).tolist()]

        columns_summary.append({
            "name": str(col),
            "dtype": str(s.dtype),
            "non_null": non_null,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_count,
            "unique_pct": unique_pct,
            "is_numeric": is_num,
            "sample_values": sample_vals
        })

        if null_pct > 30.0:
            quality_alerts.append({
                "type": "warning",
                "message": f"Column '{col}' has {null_pct}% missing values."
            })

        if unique_count == 1 and num_rows > 1:
            quality_alerts.append({
                "type": "danger",
                "message": f"Column '{col}' has only 1 unique constant value (zero variance)."
            })

        if is_num:
            numeric_cols.append(col)
            clean_s = pd.to_numeric(s, errors="coerce").dropna()
            if len(clean_s) > 0:
                q25 = float(clean_s.quantile(0.25))
                q75 = float(clean_s.quantile(0.75))
                iqr = float(q75 - q25)
                lower_b = float(q25 - 1.5 * iqr)
                upper_b = float(q75 + 1.5 * iqr)
                outliers = clean_s[(clean_s < lower_b) | (clean_s > upper_b)]
                outlier_cnt = int(len(outliers))
                outlier_pct = float(round(outlier_cnt / len(clean_s) * 100, 2))

                numeric_summary[str(col)] = {
                    "count": int(len(clean_s)),
                    "mean": float(round(clean_s.mean(), 4)),
                    "std": float(round(clean_s.std(), 4)) if len(clean_s) > 1 else 0.0,
                    "min": float(round(clean_s.min(), 4)),
                    "q25": float(round(q25, 4)),
                    "median": float(round(clean_s.median(), 4)),
                    "q75": float(round(q75, 4)),
                    "max": float(round(clean_s.max(), 4)),
                    "iqr": float(round(iqr, 4)),
                    "skew": float(round(clean_s.skew(), 4)) if len(clean_s) > 2 and clean_s.std() > 0 else 0.0,
                    "zeros_count": int((clean_s == 0).sum()),
                    "zeros_pct": float(round((clean_s == 0).sum() / len(clean_s) * 100, 2)),
                    "outliers_count": outlier_cnt,
                    "outliers_pct": outlier_pct,
                }

                outliers_summary.append({
                    "column": str(col),
                    "lower_bound": float(round(lower_b, 4)),
                    "upper_bound": float(round(upper_b, 4)),
                    "outliers_count": outlier_cnt,
                    "outliers_pct": outlier_pct
                })
        else:
            categorical_cols.append(col)
            str_s = s.dropna().astype(str)
            if len(str_s) > 0:
                vc = str_s.value_counts()
                top_val = str(vc.index[0])
                top_cnt = int(vc.iloc[0])
                top_p = float(round(top_cnt / len(str_s) * 100, 2))
                top_dist = [{"label": str(k), "count": int(v), "pct": float(round(v / len(str_s) * 100, 2))}
                            for k, v in vc.head(10).items()]
                categorical_summary[str(col)] = {
                    "count": int(len(str_s)),
                    "unique": int(str_s.nunique()),
                    "top_value": top_val,
                    "top_freq": top_cnt,
                    "top_pct": top_p,
                    "distribution": top_dist
                }

    for col in categorical_cols:
        uc = df[col].nunique(dropna=True)
        if uc > 50 and (uc / max(1, num_rows)) > 0.4:
            quality_alerts.append({
                "type": "info",
                "message": f"Categorical column '{col}' has high cardinality ({uc} unique values)."
            })

    if duplicate_rows > 0:
        quality_alerts.append({
            "type": "warning",
            "message": f"Dataset contains {duplicate_rows} duplicate rows ({duplicate_pct}%)."
        })

    # Correlation Matrix
    corr_data = {"columns": [], "matrix": [], "high_correlations": []}
    if len(numeric_cols) >= 2:
        num_df = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
        valid_cols = [c for c in numeric_cols if num_df[c].std() > 0]
        if len(valid_cols) >= 2:
            corr_matrix = num_df[valid_cols].corr().fillna(0.0).round(4)
            corr_data["columns"] = [str(c) for c in valid_cols]
            corr_data["matrix"] = [[float(val) for val in row] for row in corr_matrix.values.tolist()]

            for i in range(len(valid_cols)):
                for j in range(i + 1, len(valid_cols)):
                    val = float(corr_matrix.iloc[i, j])
                    if abs(val) >= 0.70:
                        corr_data["high_correlations"].append({
                            "col1": str(valid_cols[i]),
                            "col2": str(valid_cols[j]),
                            "correlation": val,
                            "type": "positive" if val > 0 else "negative"
                        })
            if corr_data["high_correlations"]:
                pairs_str = ", ".join([f"{p['col1']} & {p['col2']} (r={p['correlation']})" for p in corr_data["high_correlations"][:3]])
                quality_alerts.append({
                    "type": "info",
                    "message": f"Strong correlation (|r| >= 0.70) detected: {pairs_str}"
                })

    penalty = 0
    penalty += min(40, int(missing_pct * 1.5))
    penalty += min(20, int(duplicate_pct * 2))
    health_score = max(10, 100 - penalty)

    if not quality_alerts:
        quality_alerts.append({
            "type": "success",
            "message": "Dataset structure is healthy with no major anomalies detected."
        })

    return {
        "overview": {
            "num_rows": num_rows,
            "num_cols": num_cols,
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "missing_pct": missing_pct,
            "duplicate_rows": duplicate_rows,
            "duplicate_pct": duplicate_pct,
            "memory_bytes": mem_bytes,
            "memory_formatted": mem_fmt,
            "numeric_cols_count": len(numeric_cols),
            "categorical_cols_count": len(categorical_cols),
            "health_score": health_score,
            "quality_alerts": quality_alerts
        },
        "columns_summary": columns_summary,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "outliers_summary": outliers_summary,
        "correlation": corr_data
    }


def generate_eda_html_report(df: pd.DataFrame, eda: Dict[str, Any], dataset_name: str = "Uploaded Dataset") -> str:
    ov = eda["overview"]
    cols_sum = eda["columns_summary"]
    num_sum = eda["numeric_summary"]
    cat_sum = eda["categorical_summary"]
    corr = eda["correlation"]
    alerts = ov.get("quality_alerts", [])
    now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    health_score = ov["health_score"]
    health_color = "#10b981" if health_score >= 80 else ("#f59e0b" if health_score >= 60 else "#ef4444")

    # Alerts HTML
    alerts_html = ""
    for a in alerts:
        color = "#10b981" if a["type"] == "success" else ("#f59e0b" if a["type"] == "warning" else ("#ef4444" if a["type"] == "danger" else "#3b82f6"))
        bg = "#f0fdf4" if a["type"] == "success" else ("#fffbeb" if a["type"] == "warning" else ("#fef2f2" if a["type"] == "danger" else "#eff6ff"))
        icon = "✓" if a["type"] == "success" else ("⚠️" if a["type"] == "warning" else ("✕" if a["type"] == "danger" else "ℹ"))
        alerts_html += f"""
        <div style="display:flex; align-items:center; gap:12px; padding:12px 16px; margin-bottom:8px; border-radius:8px; background:{bg}; border-left:4px solid {color}; font-size:14px; color:#1e293b;">
            <span style="font-weight:700; color:{color};">{icon}</span>
            <span>{a['message']}</span>
        </div>
        """

    # Columns summary rows
    col_rows = ""
    for c in cols_sum:
        badge_bg = "#e0e7ff" if c["is_numeric"] else "#fef3c7"
        badge_color = "#4338ca" if c["is_numeric"] else "#b45309"
        samples = ", ".join([f"<code>{s}</code>" for s in c["sample_values"][:3]])
        bar_w = min(100, max(0, c["null_pct"]))
        col_rows += f"""
        <tr>
            <td style="font-weight:600; color:#0f172a;">{c['name']}</td>
            <td><span style="background:{badge_bg}; color:{badge_color}; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600;">{c['dtype']}</span></td>
            <td>{c['non_null']:,}</td>
            <td>
                <div style="display:flex; align-items:center; gap:8px;">
                    <div style="flex:1; height:6px; background:#e2e8f0; border-radius:3px; overflow:hidden;">
                        <div style="width:{bar_w}%; height:100%; background:#ef4444;"></div>
                    </div>
                    <span style="font-size:12px; color:{'#ef4444' if c['null_count'] > 0 else '#64748b'};">{c['null_count']} ({c['null_pct']}%)</span>
                </div>
            </td>
            <td>{c['unique_count']:,} ({c['unique_pct']}%)</td>
            <td style="font-size:12px; color:#64748b;">{samples if samples else '-'}</td>
        </tr>
        """

    # Numeric summary rows
    num_rows = ""
    for col_name, stats in num_sum.items():
        num_rows += f"""
        <tr>
            <td style="font-weight:600; color:#0f172a;">{col_name}</td>
            <td>{stats['count']:,}</td>
            <td>{stats['mean']:,}</td>
            <td>{stats['std']:,}</td>
            <td>{stats['min']:,}</td>
            <td>{stats['q25']:,}</td>
            <td>{stats['median']:,}</td>
            <td>{stats['q75']:,}</td>
            <td>{stats['max']:,}</td>
            <td>{stats['iqr']:,}</td>
            <td>{stats['skew']}</td>
            <td><span style="color:{'#ef4444' if stats['outliers_count'] > 0 else '#64748b'}; font-weight:{'600' if stats['outliers_count'] > 0 else '400'};">{stats['outliers_count']} ({stats['outliers_pct']}%)</span></td>
        </tr>
        """

    # Categorical summary rows
    cat_rows = ""
    for col_name, stats in cat_sum.items():
        dist_preview = ", ".join([f"{d['label']} ({d['count']})" for d in stats.get("distribution", [])[:3]])
        cat_rows += f"""
        <tr>
            <td style="font-weight:600; color:#0f172a;">{col_name}</td>
            <td>{stats['count']:,}</td>
            <td>{stats['unique']:,}</td>
            <td><strong>{stats['top_value']}</strong> ({stats['top_freq']} / {stats['top_pct']}%)</td>
            <td style="font-size:12px; color:#64748b;">{dist_preview}</td>
        </tr>
        """

    # Correlation Matrix Table
    corr_html = ""
    if corr["columns"]:
        corr_cols = corr["columns"]
        head_th = "".join([f"<th style='padding:8px 10px; font-size:12px;'>{c}</th>" for c in corr_cols])
        corr_table_rows = ""
        for i, row_col in enumerate(corr_cols):
            cells = f"<td style='font-weight:600; font-size:12px; padding:8px 10px; background:#f8fafc;'>{row_col}</td>"
            for j, val in enumerate(corr["matrix"][i]):
                if i == j:
                    bg = "#e2e8f0"
                    color = "#334155"
                elif val > 0:
                    alpha = min(1.0, val * 0.8 + 0.1)
                    bg = f"rgba(59, 130, 246, {alpha:.2f})"
                    color = "#ffffff" if alpha > 0.55 else "#1e3a8a"
                else:
                    alpha = min(1.0, abs(val) * 0.8 + 0.1)
                    bg = f"rgba(239, 68, 68, {alpha:.2f})"
                    color = "#ffffff" if alpha > 0.55 else "#7f1d1d"
                cells += f"<td style='background:{bg}; color:{color}; text-align:center; font-size:12px; padding:8px 10px; font-weight:600;'>{val:.3f}</td>"
            corr_table_rows += f"<tr>{cells}</tr>"

        high_pairs_html = ""
        for p in corr.get("high_correlations", []):
            color = "#2563eb" if p["type"] == "positive" else "#dc2626"
            high_pairs_html += f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; font-size:13px;">
                <span><strong>{p['col1']}</strong> & <strong>{p['col2']}</strong></span>
                <span style="font-weight:700; color:{color}; background:#ffffff; padding:2px 8px; border-radius:6px; border:1px solid #e2e8f0;">r = {p['correlation']}</span>
            </div>
            """

        corr_html = f"""
        <div style="overflow-x:auto; margin-bottom:20px;">
            <table class="report-table">
                <thead><tr><th>Feature</th>{head_th}</tr></thead>
                <tbody>{corr_table_rows}</tbody>
            </table>
        </div>
        """
        if high_pairs_html:
            corr_html += f"""
            <div style="margin-top:16px;">
                <h4 style="font-size:14px; margin-bottom:10px; color:#475569;">Highly Correlated Pairs (|r| &ge; 0.70):</h4>
                <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:10px;">
                    {high_pairs_html}
                </div>
            </div>
            """
    else:
        corr_html = "<p style='color:#64748b; font-style:italic;'>Not enough numeric features with variation to compute a correlation matrix.</p>"

    # Sample rows table
    sample_df = df.head(10)
    sample_th = "".join([f"<th>{c}</th>" for c in sample_df.columns])
    sample_rows = ""
    for _, r in sample_df.iterrows():
        tds = "".join([f"<td>{str(v) if pd.notna(v) else '<span style=\"color:#ef4444;\">NaN</span>'}</td>" for v in r])
        sample_rows += f"<tr>{tds}</tr>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auto EDA Report — {dataset_name}</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: #f1f5f9;
        color: #1e293b;
        line-height: 1.5;
        padding: 30px 20px;
    }}
    .container {{
        max-width: 1200px;
        margin: 0 auto;
    }}
    .header {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }}
    .header h1 {{ font-size: 26px; font-weight: 700; margin-bottom: 6px; }}
    .header p {{ color: #94a3b8; font-size: 14px; }}
    .badge {{
        background: rgba(255,255,255,0.12);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .cards-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }}
    .stat-card {{
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }}
    .stat-card .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin-bottom: 4px; }}
    .stat-card .value {{ font-size: 24px; font-weight: 700; color: #0f172a; }}
    .stat-card .sub {{ font-size: 12px; color: #94a3b8; margin-top: 4px; }}
    .section-card {{
        background: white;
        padding: 26px;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
    }}
    .section-title {{
        font-size: 18px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    table.report-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        text-align: left;
    }}
    table.report-table th {{
        background: #f8fafc;
        color: #475569;
        font-weight: 600;
        padding: 10px 12px;
        border-bottom: 2px solid #e2e8f0;
        white-space: nowrap;
    }}
    table.report-table td {{
        padding: 10px 12px;
        border-bottom: 1px solid #f1f5f9;
        white-space: nowrap;
    }}
    table.report-table tr:hover td {{
        background: #f8fafc;
    }}
    code {{
        background: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
    }}
    @media print {{
        body {{ background: white; padding: 0; }}
        .section-card {{ box-shadow: none; border: 1px solid #ccc; }}
        .header {{ background: #1e293b !important; -webkit-print-color-adjust: exact; }}
    }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <h1>📊 Automated Exploratory Data Analysis Report</h1>
            <p>Dataset: <strong>{dataset_name}</strong> &bull; Generated: {now_str}</p>
        </div>
        <div style="text-align:right;">
            <span class="badge">MLWorkbench Engine</span>
            <div style="margin-top:8px; font-size:12px; color:#cbd5e1;">Health Score: <strong style="color:{health_color}; font-size:16px;">{health_score}/100</strong></div>
        </div>
    </div>

    <!-- Metric Cards -->
    <div class="cards-grid">
        <div class="stat-card">
            <div class="label">Total Rows</div>
            <div class="value">{ov['num_rows']:,}</div>
            <div class="sub">{ov['duplicate_rows']} duplicates ({ov['duplicate_pct']}%)</div>
        </div>
        <div class="stat-card">
            <div class="label">Total Columns</div>
            <div class="value">{ov['num_cols']}</div>
            <div class="sub">{ov['numeric_cols_count']} Num &bull; {ov['categorical_cols_count']} Cat</div>
        </div>
        <div class="stat-card">
            <div class="label">Missing Cells</div>
            <div class="value" style="color:{'#ef4444' if ov['missing_cells'] > 0 else '#10b981'};">{ov['missing_pct']}%</div>
            <div class="sub">{ov['missing_cells']:,} empty cells</div>
        </div>
        <div class="stat-card">
            <div class="label">Memory Footprint</div>
            <div class="value">{ov['memory_formatted']}</div>
            <div class="sub">{ov['total_cells']:,} total data cells</div>
        </div>
        <div class="stat-card">
            <div class="label">Data Health</div>
            <div class="value" style="color:{health_color};">{health_score} / 100</div>
            <div class="sub">Anomaly & Quality Rating</div>
        </div>
    </div>

    <!-- Health Alerts -->
    <div class="section-card">
        <div class="section-title">🛡️ Data Health & Quality Alerts</div>
        {alerts_html}
    </div>

    <!-- Column Schema -->
    <div class="section-card">
        <div class="section-title">📋 Column Schema & Missing Values</div>
        <div style="overflow-x:auto;">
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Column Name</th>
                        <th>Type</th>
                        <th>Non-Null</th>
                        <th>Missing Values</th>
                        <th>Unique Values</th>
                        <th>Sample Values</th>
                    </tr>
                </thead>
                <tbody>
                    {col_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Numeric Summary -->
    {"<div class='section-card'><div class='section-title'>🔢 Numerical Features Summary</div><div style='overflow-x:auto;'><table class='report-table'><thead><tr><th>Feature</th><th>Count</th><th>Mean</th><th>Std</th><th>Min</th><th>25%</th><th>50% (Median)</th><th>75%</th><th>Max</th><th>IQR</th><th>Skewness</th><th>Outliers (IQR)</th></tr></thead><tbody>" + num_rows + "</tbody></table></div></div>" if num_rows else ""}

    <!-- Categorical Summary -->
    {"<div class='section-card'><div class='section-title'>🔤 Categorical Features Summary</div><div style='overflow-x:auto;'><table class='report-table'><thead><tr><th>Feature</th><th>Count</th><th>Unique</th><th>Top Mode (Freq / %)</th><th>Top Categories Sample</th></tr></thead><tbody>" + cat_rows + "</tbody></table></div></div>" if cat_rows else ""}

    <!-- Correlation Matrix -->
    <div class="section-card">
        <div class="section-title">🔗 Correlation Matrix & Multicollinearity</div>
        {corr_html}
    </div>

    <!-- Data Preview -->
    <div class="section-card">
        <div class="section-title">👁️ First 10 Rows Preview</div>
        <div style="overflow-x:auto;">
            <table class="report-table">
                <thead><tr>{sample_th}</tr></thead>
                <tbody>{sample_rows}</tbody>
            </table>
        </div>
    </div>

    <div style="text-align:center; font-size:12px; color:#94a3b8; margin-top:20px;">
        Generated automatically by MLWorkbench &bull; All calculations performed on raw CSV upload
    </div>
</div>
</body>
</html>
"""
    return html
