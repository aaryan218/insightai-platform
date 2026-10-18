import streamlit as st
import pandas as pd
import requests
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MLWorkbench — Interactive Machine Learning Training & Prediction Platform",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "dataset" not in st.session_state:
    st.session_state.dataset = None

if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = None

if "dataset_bytes" not in st.session_state:
    st.session_state.dataset_bytes = None

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "📤 Upload Dataset"

if "trained" not in st.session_state:
    st.session_state.trained = False

if "trained_model" not in st.session_state:
    st.session_state.trained_model = None

if "features" not in st.session_state:
    st.session_state.features = []

if "label" not in st.session_state:
    st.session_state.label = None

if "metrics" not in st.session_state:
    st.session_state.metrics = {}

if "eda_cache" not in st.session_state:
    st.session_state.eda_cache = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/login",
            json={
                "username": username,
                "password": password,
            },
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            return True, "Login successful"
        return False, response.json().get("detail", "Login failed")
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to FastAPI. Make sure uvicorn is running."
    except Exception as e:
        return False, str(e)


def add_tokens(amount):
    try:
        response = requests.post(
            f"{API_URL}/add_tokens",
            headers=auth_headers(),
            json={
                "username": st.session_state.username,
                "credit_card": "1111-2222-3333-4444",
                "amount": amount,
            },
            timeout=10,
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get("detail", "Could not add tokens")
    except Exception as e:
        return False, str(e)


def get_tokens():
    try:
        response = requests.get(
            f"{API_URL}/tokens/{st.session_state.username}",
            headers=auth_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()["tokens"]
        return None
    except Exception:
        return None


def _prepare_files_dict(file_source, default_name="dataset.csv"):
    if hasattr(file_source, "name") and hasattr(file_source, "seek"):
        file_source.seek(0)
        content = file_source.getvalue() if hasattr(file_source, "getvalue") else file_source.read()
        return {"file": (file_source.name, content, "text/csv")}
    elif isinstance(file_source, (bytes, bytearray)):
        return {"file": (default_name, io.BytesIO(file_source), "text/csv")}
    return None


def train_model(file_source, model_name, features, label, filename="dataset.csv"):
    try:
        files = _prepare_files_dict(file_source, filename)
        if not files:
            return False, "No file provided"

        data = {
            "model_name": model_name,
            "features": ",".join(features),
            "label": label,
        }
        response = requests.post(
            f"{API_URL}/train",
            headers=auth_headers(),
            files=files,
            data=data,
            timeout=120,
        )
        if response.status_code == 200:
            return True, response.json()

        try:
            detail = response.json().get("detail", "Training failed")
        except Exception:
            detail = response.text
        return False, detail
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to FastAPI."
    except Exception as e:
        return False, str(e)


def make_prediction(model_name, values):
    try:
        response = requests.post(
            f"{API_URL}/predict/{model_name}",
            headers=auth_headers(),
            json=values,
            timeout=30,
        )
        if response.status_code == 200:
            return True, response.json()
        try:
            detail = response.json().get("detail", "Prediction failed")
        except Exception:
            detail = response.text
        return False, detail
    except Exception as e:
        return False, str(e)


def get_models():
    try:
        response = requests.get(
            f"{API_URL}/models",
            headers=auth_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("models", [])
        return []
    except Exception:
        return []


def get_eda(file_source, filename="dataset.csv"):
    try:
        files = _prepare_files_dict(file_source, filename)
        if not files:
            return False, "No file provided"

        response = requests.post(
            f"{API_URL}/eda",
            headers=auth_headers(),
            files=files,
            timeout=60,
        )
        if response.status_code == 200:
            return True, response.json()
        try:
            detail = response.json().get("detail", "EDA failed")
        except Exception:
            detail = response.text
        return False, detail
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to FastAPI."
    except Exception as e:
        return False, str(e)


def get_eda_report_bytes(file_source, filename="dataset.csv"):
    try:
        files = _prepare_files_dict(file_source, filename)
        if not files:
            return False, None

        response = requests.post(
            f"{API_URL}/eda/report",
            headers=auth_headers(),
            files=files,
            timeout=60,
        )
        if response.status_code == 200:
            return True, response.content
        return False, None
    except Exception:
        return False, None


# ============================================================
# SIDEBAR (LOGIN, NAVIGATION & WALLET)
# ============================================================

with st.sidebar:
    st.header("🔐 Authentication")

    if st.session_state.token:
        st.success(f"Logged in as `{st.session_state.username}`")

        tokens = get_tokens()
        if tokens is not None:
            st.metric("Available Tokens", tokens)

        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.trained = False
            st.rerun()

        st.divider()

        # Navigation selector
        st.header("🧭 Navigation")
        nav_options = [
            "📤 Upload Dataset",
            "📊 Auto EDA",
            "🤖 Model Training & Prediction",
        ]
        cur_idx = nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0
        selected_nav = st.radio(
            "Go to page:",
            nav_options,
            index=cur_idx,
            key="nav_radio_selector",
        )
        if selected_nav != st.session_state.current_page:
            st.session_state.current_page = selected_nav
            st.rerun()

        if st.session_state.dataset_name:
            st.caption(f"📁 Active Dataset: **{st.session_state.dataset_name}**")

        st.divider()

        with st.expander("💳 Demo Token Wallet"):
            st.write("Training costs 1 token, predicting costs 5 tokens.")
            token_amount = st.number_input(
                "Tokens to add",
                min_value=1,
                max_value=1000,
                value=20,
                step=1,
            )
            if st.button("Add Demo Tokens"):
                success, result = add_tokens(token_amount)
                if success:
                    st.success(f"Tokens added. Balance: {result['tokens']}")
                    st.rerun()
                else:
                    st.error(result)

    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            success, message = login(username, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

        st.info("Use the account you created through the FastAPI API.")


# ============================================================
# REQUIRE LOGIN
# ============================================================

if not st.session_state.token:
    st.title("🤖 MLWorkbench")
    st.warning("Please log in from the sidebar to access the platform.")
    st.stop()


# ============================================================
# PAGE 1: UPLOAD DATASET
# ============================================================

def render_upload_page():
    st.title("📤 Dataset Upload Portal")
    st.write(
        "Upload a tabular CSV dataset below. "
        "As soon as you upload, you will be **automatically redirected to the Auto EDA page** "
        "where the complete data health, descriptive statistics, distributions, and correlation heatmap will be generated."
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file to begin",
        type=["csv"],
        key="main_csv_uploader"
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
            st.session_state.dataset = df
            st.session_state.dataset_name = uploaded_file.name
            st.session_state.dataset_bytes = file_bytes

            # Auto-redirection when a new file is uploaded
            if st.session_state.last_uploaded_name != uploaded_file.name:
                st.session_state.last_uploaded_name = uploaded_file.name
                st.session_state.current_page = "📊 Auto EDA"
                st.success(f"✅ Successfully uploaded '{uploaded_file.name}'! Redirecting to Auto EDA...")
                st.rerun()

        except Exception as e:
            st.error(f"Could not parse CSV file: {e}")

    if st.session_state.dataset is not None:
        st.divider()
        st.subheader("📁 Currently Active Dataset")
        df_active = st.session_state.dataset
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Filename", st.session_state.dataset_name)
        with c2:
            st.metric("Total Rows", f"{len(df_active):,}")
        with c3:
            st.metric("Total Columns", len(df_active.columns))

        st.write("Your dataset is ready. Jump directly to any section below:")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("📊 View Full Auto EDA", type="primary", use_container_width=True):
                st.session_state.current_page = "📊 Auto EDA"
                st.rerun()
        with col_b2:
            if st.button("🤖 Proceed to Model Training", use_container_width=True):
                st.session_state.current_page = "🤖 Model Training & Prediction"
                st.rerun()


# ============================================================
# PAGE 2: AUTO EDA STUDIO
# ============================================================

def render_eda_page():
    if st.session_state.dataset is None:
        st.warning("⚠️ No dataset has been uploaded yet.")
        if st.button("📤 Go to Upload Page", type="primary"):
            st.session_state.current_page = "📤 Upload Dataset"
            st.rerun()
        return

    df = st.session_state.dataset
    filename = st.session_state.dataset_name or "dataset.csv"
    file_bytes = st.session_state.dataset_bytes

    # Cache retrieval
    cache_key = f"{filename}_{len(file_bytes) if file_bytes else len(df)}"
    if cache_key not in st.session_state.eda_cache:
        with st.spinner("🤖 Running Automated Exploratory Data Analysis (EDA)..."):
            success_eda, res_eda = get_eda(file_bytes, filename=filename)
            if success_eda:
                st.session_state.eda_cache[cache_key] = res_eda
            else:
                try:
                    from bl import compute_eda
                    st.session_state.eda_cache[cache_key] = compute_eda(df)
                except Exception:
                    st.session_state.eda_cache[cache_key] = None

    eda = st.session_state.eda_cache.get(cache_key)
    if not eda:
        try:
            from bl import compute_eda
            eda = compute_eda(df)
            st.session_state.eda_cache[cache_key] = eda
        except Exception as e:
            st.error(f"Failed to compute EDA: {e}")
            return

    # Top Header & Quick Actions
    col_title, col_actions = st.columns([3, 1])
    with col_title:
        st.title("📊 Automated Exploratory Data Analysis (Auto EDA)")
        st.caption(f"Comprehensive profiling and diagnostics for **{filename}**")

    with col_actions:
        # Download HTML report
        report_bytes = None
        success_rep, rep_content = get_eda_report_bytes(file_bytes, filename=filename)
        if success_rep and rep_content:
            report_bytes = rep_content
        elif eda:
            try:
                from bl import generate_eda_html_report
                report_bytes = generate_eda_html_report(df, eda, dataset_name=filename).encode("utf-8")
            except Exception:
                report_bytes = None

        if report_bytes:
            st.download_button(
                label="📥 Download HTML Report",
                data=report_bytes,
                file_name=f"eda_report_{filename}.html",
                mime="text/html",
                help="Download an offline, self-contained interactive HTML profiling report",
                use_container_width=True,
            )

        if st.button("📤 Upload Another Dataset", use_container_width=True):
            st.session_state.current_page = "📤 Upload Dataset"
            st.rerun()

    ov = eda["overview"]
    cols_sum = eda["columns_summary"]
    num_sum = eda["numeric_summary"]
    cat_sum = eda["categorical_summary"]
    out_sum = eda["outliers_summary"]
    corr = eda["correlation"]
    health_score = ov["health_score"]

    eda_tab1, eda_tab2, eda_tab3, eda_tab4, eda_tab5 = st.tabs([
        "📋 Overview & Health",
        "🔢 Descriptive Statistics",
        "📊 Visual Distributions",
        "🔗 Correlations & Multicollinearity",
        "⚠️ Outliers & Target Profiling",
    ])

    # ---------------- TAB 1: OVERVIEW & HEALTH ----------------
    with eda_tab1:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total Rows", f"{ov['num_rows']:,}")
        with c2:
            st.metric("Total Columns", f"{ov['num_cols']}", f"{ov['numeric_cols_count']} Num | {ov['categorical_cols_count']} Cat")
        with c3:
            st.metric("Missing Cells", f"{ov['missing_pct']}%", f"{ov['missing_cells']:,} empty")
        with c4:
            st.metric("Duplicate Rows", f"{ov['duplicate_pct']}%", f"{ov['duplicate_rows']:,} rows")
        with c5:
            st.metric("Memory", f"{ov['memory_formatted']}", f"{ov['total_cells']:,} cells")

        # Health score card
        if health_score >= 80:
            st.success(f"💚 **Dataset Quality Health Score: {health_score} / 100** — Excellent data health with minimal anomalies detected.")
        elif health_score >= 60:
            st.warning(f"💛 **Dataset Quality Health Score: {health_score} / 100** — Moderate quality. Please inspect the warnings below.")
        else:
            st.error(f"❤️ **Dataset Quality Health Score: {health_score} / 100** — Multiple data quality warnings detected.")

        # Quality alerts
        with st.expander("🛡️ Quality & Hygiene Alerts", expanded=True):
            for alert in ov.get("quality_alerts", []):
                atype = alert.get("type", "info")
                msg = alert.get("message", "")
                if atype == "success":
                    st.success(f"✓ {msg}")
                elif atype == "warning":
                    st.warning(f"⚠️ {msg}")
                elif atype == "danger":
                    st.error(f"✕ {msg}")
                else:
                    st.info(f"ℹ️ {msg}")

        # Interactive Data Preview
        with st.expander("👁️ Interactive Dataset Preview", expanded=True):
            prev_col1, prev_col2 = st.columns([1, 2])
            with prev_col1:
                view_mode = st.radio("View Mode", ["Head", "Tail", "Sample"], horizontal=True)
            with prev_col2:
                row_count = st.slider(
                    "Rows to display",
                    min_value=5,
                    max_value=min(100, max(5, len(df))),
                    value=min(15, len(df)),
                    step=5,
                )

            if view_mode == "Head":
                preview_data = df.head(row_count)
            elif view_mode == "Tail":
                preview_data = df.tail(row_count)
            else:
                preview_data = df.sample(min(row_count, len(df)), random_state=42)

            st.dataframe(preview_data, use_container_width=True)

        # Column Schema & Metadata Table
        with st.expander("📋 Column Schema & Missing Values Breakdown", expanded=False):
            schema_rows = []
            for c in cols_sum:
                schema_rows.append({
                    "Column Name": c["name"],
                    "Data Type": c["dtype"],
                    "Type Category": "Numeric" if c["is_numeric"] else "Categorical/Text",
                    "Non-Null Count": f"{c['non_null']:,}",
                    "Missing Count": f"{c['null_count']:,}",
                    "Missing %": f"{c['null_pct']}%",
                    "Unique Values": f"{c['unique_count']:,}",
                    "Unique %": f"{c['unique_pct']}%",
                    "Sample Values": ", ".join(c["sample_values"][:3]) if c["sample_values"] else "-",
                })
            st.dataframe(pd.DataFrame(schema_rows), use_container_width=True)

    # ---------------- TAB 2: DESCRIPTIVE STATISTICS ----------------
    with eda_tab2:
        if num_sum:
            st.subheader("🔢 Numerical Variables Summary")
            num_rows = []
            for col_name, stats in num_sum.items():
                num_rows.append({
                    "Feature": col_name,
                    "Count": stats["count"],
                    "Mean": stats["mean"],
                    "Std Dev": stats["std"],
                    "Min": stats["min"],
                    "25% (Q1)": stats["q25"],
                    "50% (Median)": stats["median"],
                    "75% (Q3)": stats["q75"],
                    "Max": stats["max"],
                    "IQR": stats["iqr"],
                    "Skewness": stats["skew"],
                    "Zeros %": f"{stats['zeros_pct']}%",
                    "Outliers": f"{stats['outliers_count']} ({stats['outliers_pct']}%)",
                })
            st.dataframe(pd.DataFrame(num_rows), use_container_width=True)
        else:
            st.info("No numeric features found for numerical summary.")

        if cat_sum:
            st.subheader("🔤 Categorical Variables Summary")
            cat_rows = []
            for col_name, stats in cat_sum.items():
                cat_rows.append({
                    "Feature": col_name,
                    "Count": stats["count"],
                    "Unique Categories": stats["unique"],
                    "Top Category (Mode)": stats["top_value"],
                    "Top Frequency": stats["top_freq"],
                    "Top %": f"{stats['top_pct']}%",
                })
            st.dataframe(pd.DataFrame(cat_rows), use_container_width=True)
        else:
            st.info("No categorical features found.")

    # ---------------- TAB 3: VISUAL DISTRIBUTIONS ----------------
    with eda_tab3:
        st.subheader("📈 Feature Distribution Explorer")
        inspect_col = st.selectbox(
            "Select a feature to explore its distribution:",
            df.columns.tolist(),
            key="eda_inspect_col"
        )

        is_num = bool(pd.api.types.is_numeric_dtype(df[inspect_col]))
        if is_num:
            col_chart, col_stats = st.columns([2, 1])
            clean_series = pd.to_numeric(df[inspect_col], errors="coerce").dropna()

            with col_chart:
                if len(clean_series) > 0:
                    fig, (ax_h, ax_b) = plt.subplots(
                        2, 1, figsize=(7, 4.8), sharex=True,
                        gridspec_kw={"height_ratios": [3, 1]}
                    )
                    bins_cnt = min(25, max(5, int(len(clean_series)**0.5)))
                    ax_h.hist(
                        clean_series, bins=bins_cnt,
                        color="#3b82f6", edgecolor="white", alpha=0.85
                    )
                    mean_val = float(clean_series.mean())
                    median_val = float(clean_series.median())
                    ax_h.axvline(mean_val, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Mean: {mean_val:,.2f}")
                    ax_h.axvline(median_val, color="#10b981", linestyle=":", linewidth=2, label=f"Median: {median_val:,.2f}")
                    ax_h.set_ylabel("Frequency", fontsize=10)
                    ax_h.legend(loc="upper right", fontsize=9)
                    ax_h.grid(axis="y", linestyle="--", alpha=0.4)
                    ax_h.set_title(f"Distribution of '{inspect_col}'", fontsize=12, fontweight="bold")

                    ax_b.boxplot(
                        clean_series, vert=False, patch_artist=True,
                        boxprops=dict(facecolor="#93c5fd", color="#1d4ed8"),
                        medianprops=dict(color="#b91c1c", linewidth=2)
                    )
                    ax_b.set_yticks([])
                    ax_b.set_xlabel(inspect_col, fontsize=10)
                    ax_b.grid(axis="x", linestyle="--", alpha=0.4)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

            with col_stats:
                if inspect_col in num_sum:
                    ns = num_sum[inspect_col]
                    st.markdown(f"**Feature:** `{inspect_col}`")
                    st.metric("Mean", f"{ns['mean']:,}")
                    st.metric("Median (50%)", f"{ns['median']:,}")
                    st.metric("Std Dev", f"{ns['std']:,}")
                    st.metric("Min — Max", f"{ns['min']:,} — {ns['max']:,}")

                    skew_val = ns["skew"]
                    if skew_val > 1.0:
                        skew_desc = "Highly right-skewed (positive tail)"
                    elif skew_val < -1.0:
                        skew_desc = "Highly left-skewed (negative tail)"
                    elif abs(skew_val) <= 0.5:
                        skew_desc = "Approximately symmetric"
                    else:
                        skew_desc = "Moderately skewed"
                    st.caption(f"**Skewness:** {skew_val} ({skew_desc})")
        else:
            cat_s = df[inspect_col].dropna().astype(str)
            vc = cat_s.value_counts().head(10)
            if not vc.empty:
                fig, ax = plt.subplots(figsize=(7, 4))
                ax.barh(vc.index[::-1].astype(str), vc.values[::-1], color="#8b5cf6", edgecolor="white", alpha=0.85)
                ax.set_xlabel("Count", fontsize=10)
                ax.set_title(f"Top Categories in '{inspect_col}'", fontsize=12, fontweight="bold")
                ax.grid(axis="x", linestyle="--", alpha=0.4)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No values found in this column.")

        # Missing values bar chart
        st.write("")
        st.subheader("⚠️ Missing Values Visualizer")
        missing_s = df.isna().sum()
        missing_s = missing_s[missing_s > 0]
        if len(missing_s) > 0:
            missing_pcts = (missing_s / len(df) * 100).round(2)
            fig, ax = plt.subplots(figsize=(7, max(3, len(missing_s) * 0.4)))
            ax.barh(missing_pcts.index[::-1], missing_pcts.values[::-1], color="#ef4444", alpha=0.8)
            ax.set_xlabel("Missing Percentage (%)", fontsize=10)
            ax.set_title("Missing Values % by Column", fontsize=12, fontweight="bold")
            ax.grid(axis="x", linestyle="--", alpha=0.4)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.success("🎉 Zero missing values detected across all columns!")

    # ---------------- TAB 4: CORRELATIONS & MULTICOLLINEARITY ----------------
    with eda_tab4:
        st.subheader("🔗 Feature Correlation Matrix")
        if corr["columns"] and len(corr["columns"]) >= 2:
            corr_cols = corr["columns"]
            corr_df = pd.DataFrame(corr["matrix"], index=corr_cols, columns=corr_cols)

            fig, ax = plt.subplots(figsize=(max(6, len(corr_cols) * 0.9), max(4.5, len(corr_cols) * 0.75)))
            cax = ax.matshow(corr_df.values, cmap="coolwarm", vmin=-1, vmax=1)
            fig.colorbar(cax, shrink=0.8)

            ax.set_xticks(range(len(corr_cols)))
            ax.set_yticks(range(len(corr_cols)))
            ax.set_xticklabels(corr_cols, rotation=45, ha="left", fontsize=9)
            ax.set_yticklabels(corr_cols, fontsize=9)

            for i in range(len(corr_cols)):
                for j in range(len(corr_cols)):
                    val = corr_df.iloc[i, j]
                    text_color = "white" if abs(val) > 0.55 else "black"
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=8, fontweight="bold")

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            with st.expander("📋 View Numeric Correlation Matrix Table"):
                st.dataframe(corr_df.style.background_gradient(cmap="coolwarm", vmin=-1, vmax=1).format("{:.3f}"), use_container_width=True)

            high_corrs = corr.get("high_correlations", [])
            if high_corrs:
                st.warning("⚠️ **Strong Multicollinearity Detected (|r| >= 0.70):**")
                hc_rows = []
                for p in high_corrs:
                    hc_rows.append({
                        "Feature 1": p["col1"],
                        "Feature 2": p["col2"],
                        "Correlation (r)": p["correlation"],
                        "Type": "Positive" if p["correlation"] > 0 else "Negative",
                        "Recommendation": "Consider dropping one feature if using Linear/Logistic regression to avoid multicollinearity."
                    })
                st.dataframe(pd.DataFrame(hc_rows), use_container_width=True)
            else:
                st.info("No strong multicollinearity (|r| >= 0.70) detected among numeric features.")
        else:
            st.info("At least 2 numeric columns with non-zero variance are required to compute a correlation matrix.")

    # ---------------- TAB 5: OUTLIERS & TARGET PROFILING ----------------
    with eda_tab5:
        st.subheader("⚠️ Outliers Detection (IQR Method)")
        if out_sum:
            out_rows = []
            for o in out_sum:
                out_rows.append({
                    "Feature": o["column"],
                    "Lower Bound (Q1 - 1.5*IQR)": o["lower_bound"],
                    "Upper Bound (Q3 + 1.5*IQR)": o["upper_bound"],
                    "Outliers Count": o["outliers_count"],
                    "Outliers %": f"{o['outliers_pct']}%",
                    "Status": "⚠️ Outliers Present" if o["outliers_count"] > 0 else "✓ Clean"
                })
            st.dataframe(pd.DataFrame(out_rows), use_container_width=True)
        else:
            st.info("No numeric features to evaluate for outliers.")

        st.write("")
        st.subheader("🎯 Candidate Target/Label Profiler")
        st.caption("Quickly preview the distribution of the variable you plan to predict.")
        target_cand = st.selectbox(
            "Select column to preview as candidate Target/Label:",
            df.columns.tolist(),
            index=len(df.columns) - 1,
            key="eda_target_cand"
        )

        cand_is_num = bool(pd.api.types.is_numeric_dtype(df[target_cand]))
        if cand_is_num and df[target_cand].nunique() > 10:
            st.write(f"**Target Type:** Continuous Numerical &bull; **Suggested Task:** `Regression` (Linear, Random Forest, SVR, XGBoost)")
            c_s = pd.to_numeric(df[target_cand], errors="coerce").dropna()
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.hist(c_s, bins=min(20, max(5, int(len(c_s)**0.5))), color="#059669", edgecolor="white", alpha=0.85)
            ax.set_title(f"Target Distribution: '{target_cand}'", fontsize=11, fontweight="bold")
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.write(f"**Target Type:** Categorical / Discrete ({df[target_cand].nunique()} classes) &bull; **Suggested Task:** `Classification` (Logistic Regression)")
            c_s = df[target_cand].dropna().astype(str)
            vc = c_s.value_counts()
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(vc.index.astype(str), vc.values, color="#d97706", edgecolor="white", alpha=0.85)
            ax.set_title(f"Class Balance: '{target_cand}'", fontsize=11, fontweight="bold")
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    # Bottom Next Step Action Card
    st.divider()
    cta_col1, cta_col2 = st.columns([3, 1])
    with cta_col1:
        st.subheader("🚀 Ready to Train a Model?")
        st.write("Now that you have explored your data, configure and train machine learning models.")
    with cta_col2:
        if st.button("➡️ Proceed to Model Training", type="primary", use_container_width=True):
            st.session_state.current_page = "🤖 Model Training & Prediction"
            st.rerun()


# ============================================================
# PAGE 3: MODEL TRAINING & PREDICTION
# ============================================================

def render_training_prediction_page():
    if st.session_state.dataset is None:
        st.warning("⚠️ No dataset uploaded yet. Please upload a dataset first.")
        if st.button("📤 Go to Upload Page", type="primary"):
            st.session_state.current_page = "📤 Upload Dataset"
            st.rerun()
        return

    df = st.session_state.dataset
    filename = st.session_state.dataset_name or "dataset.csv"
    file_bytes = st.session_state.dataset_bytes

    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.title("🤖 Model Training & Real-Time Predictions")
        st.caption(f"Active Dataset: **{filename}** ({len(df):,} rows, {len(df.columns)} columns)")
    with top_c2:
        if st.button("⬅️ Back to Auto EDA", use_container_width=True):
            st.session_state.current_page = "📊 Auto EDA"
            st.rerun()

    # Step 2: Configure Model
    st.header("1️⃣ Configure Machine Learning Model")

    available_models = ["linear", "random_forest", "svr"]
    try:
        import xgboost
        available_models.append("xgboost")
    except ImportError:
        pass

    model_name = st.selectbox(
        "Select Model",
        available_models,
        format_func=lambda x: {
            "linear": "Linear Regression",
            "random_forest": "Random Forest",
            "svr": "Support Vector Regression",
            "xgboost": "XGBoost",
        }.get(x, x),
    )

    columns = df.columns.tolist()
    label = st.selectbox("Select Target / Label", columns, index=len(columns) - 1)
    feature_options = [col for col in columns if col != label]
    features = st.multiselect("Select Input Features", feature_options, default=feature_options)

    if not features:
        st.warning("Select at least one feature.")
        return

    st.write(f"**Model:** `{model_name}` &bull; **Target:** `{label}` &bull; **Features:** `{', '.join(features)}`")

    # Train button
    if st.button("🚀 Train Model", type="primary", use_container_width=True):
        with st.spinner("Training model on backend..."):
            success, result = train_model(
                file_bytes if file_bytes else df.to_csv(index=False).encode("utf-8"),
                model_name,
                features,
                label,
                filename=filename,
            )

        if success:
            st.session_state.trained = True
            st.session_state.trained_model = model_name
            st.session_state.features = features
            st.session_state.label = label
            st.session_state.metrics = result.get("metrics", {})
            st.success("Model trained successfully!")
        else:
            st.error(f"Training failed: {result}")

    # Model Performance
    if st.session_state.trained:
        st.divider()
        st.header("2️⃣ Model Performance")
        metrics = st.session_state.metrics
        if metrics:
            metric_columns = st.columns(len(metrics))
            for col, (name, value) in zip(metric_columns, metrics.items()):
                with col:
                    st.metric(name, round(float(value), 4))

        st.caption(
            "Note: these metrics are calculated on the training data by the backend. "
            "They are not a proper hold-out/test-set evaluation."
        )

        # Live Prediction
        st.divider()
        st.header("3️⃣ Test Your Model (Live Prediction)")
        st.write("Enter values for the selected features and get real-time predictions from your trained model.")

        prediction_values = {}
        input_columns = st.columns(min(3, len(st.session_state.features)))

        for index, feature in enumerate(st.session_state.features):
            with input_columns[index % len(input_columns)]:
                numeric_series = pd.to_numeric(df[feature], errors="coerce")
                if numeric_series.notna().any():
                    median_value = float(numeric_series.median())
                    prediction_values[feature] = st.number_input(feature, value=median_value)
                else:
                    st.error(f"Feature '{feature}' must contain numeric values for prediction.")

        st.write("")
        if st.button("🔮 Generate Prediction", type="primary", use_container_width=True):
            with st.spinner("Generating prediction..."):
                success, result = make_prediction(st.session_state.trained_model, prediction_values)

            if success:
                prediction = result["prediction"]
                st.success("Prediction generated!")
                st.metric("Predicted Value", prediction)
            else:
                st.error(f"Prediction failed: {result}")

    # Trained Model History
    st.divider()
    st.header("4️⃣ Your Trained Models")
    models = get_models()
    if models:
        model_df = pd.DataFrame(models)
        st.dataframe(model_df, use_container_width=True)
    else:
        st.info("No trained models recorded yet.")


# ============================================================
# MAIN ROUTER
# ============================================================

if st.session_state.current_page == "📤 Upload Dataset":
    render_upload_page()
elif st.session_state.current_page == "📊 Auto EDA":
    render_eda_page()
elif st.session_state.current_page == "🤖 Model Training & Prediction":
    render_training_prediction_page()
else:
    render_upload_page()
