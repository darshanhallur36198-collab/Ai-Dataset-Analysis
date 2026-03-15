import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

# ── Chart tag types (used by frontend "filter" buttons) ──────────
# Each chart dict carries a "chart_type" field.

def generate_charts(df):
    charts = []

    COLORS = px.colors.qualitative.G10

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()

    def finalize(fig, title: str, subtitle: str = "", chart_type: str = "other"):
        """Apply standard layout and return JSON-serialisable dict."""
        full_title = f"<b>{title}</b><br><span style='font-size:12px;color:#8b95a9'>{subtitle}</span>" if subtitle else f"<b>{title}</b>"
        fig.update_layout(
            # Theme is intentionally left as 'plotly_dark' here;
            # the frontend overrides it at render-time using the Settings value.
            template="plotly_dark",
            title=dict(
                text=full_title,
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="#ffffff")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=60, r=40, b=70, t=90),
            font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#c9d1d9"),
            legend=dict(
                bgcolor="rgba(30,30,50,0.6)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(size=12)
            ),
            hoverlabel=dict(
                bgcolor="rgba(20,20,40,0.9)",
                font_size=13,
                font_color="#ffffff"
            ),
        )
        result = json.loads(fig.to_json())
        result["_chart_type"] = chart_type   # tag for frontend filtering
        return result

    # ── 1. Histogram + Box (per numeric column) ──────────────────
    for col in numeric_cols[:4]:
        if df[col].nunique() < 2:
            continue
        mean_val = df[col].mean()
        median_val = df[col].median()
        fig = px.histogram(
            df, x=col,
            marginal="box",
            color_discrete_sequence=[COLORS[0]],
            labels={col: col.replace("_", " ").title()}
        )
        fig.update_xaxes(title_text=col.replace("_", " ").title(), title_font_size=13)
        fig.update_yaxes(title_text="Count", title_font_size=13)
        # Mean / median lines
        fig.add_vline(x=mean_val,   line_dash="dash",  line_color="#ffd200", annotation_text=f"Mean: {mean_val:.1f}",   annotation_position="top right")
        fig.add_vline(x=median_val, line_dash="dot",   line_color="#38ef7d", annotation_text=f"Median: {median_val:.1f}", annotation_position="top left")
        charts.append(finalize(fig, f"Distribution of {col.replace('_', ' ').title()}",
                                f"Histogram with box plot. Mean={mean_val:.2f} | Median={median_val:.2f}",
                                chart_type="distribution"))

    # ── 2. Box Plot (outlier view) ───────────────────────────────
    for col in numeric_cols[:3]:
        if df[col].nunique() < 2:
            continue
        fig = px.box(
            df, y=col,
            color_discrete_sequence=[COLORS[3]],
            points="outliers",
            labels={col: col.replace("_", " ").title()}
        )
        fig.update_yaxes(title_text=col.replace("_", " ").title(), title_font_size=13)
        charts.append(finalize(fig, f"Outlier Analysis: {col.replace('_', ' ').title()}",
                                "Box plot showing median, IQR, and outlier points",
                                chart_type="distribution"))

    # ── 3. Bar charts for categorical columns ────────────────────
    for col in [c for c in cat_cols if 1 < df[c].nunique() <= 20][:3]:
        counts = df[col].value_counts().reset_index().head(10)
        counts.columns = [col, "Count"]
        fig = px.bar(
            counts, x=col, y="Count",
            color="Count",
            color_continuous_scale="Viridis",
            labels={col: col.replace("_", " ").title(), "Count": "Number of Records"},
            text="Count"
        )
        fig.update_traces(textposition="outside", textfont_size=11)
        fig.update_xaxes(title_text=col.replace("_", " ").title(), title_font_size=13, tickangle=-30)
        fig.update_yaxes(title_text="Count", title_font_size=13)
        charts.append(finalize(fig, f"Top Categories in {col.replace('_', ' ').title()}",
                                "Frequency of each category (Top 10 shown)",
                                chart_type="categorical"))

    # ── 4. Pie / Donut for low-cardinality categoricals ──────────
    for col in cat_cols:
        if 2 <= df[col].nunique() <= 8:
            fig = px.pie(
                df, names=col,
                hole=0.42,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={col: col.replace("_", " ").title()}
            )
            fig.update_traces(
                textinfo="label+percent",
                textfont_size=13,
                pull=[0.03] * df[col].nunique()
            )
            charts.append(finalize(fig, f"Proportions: {col.replace('_', ' ').title()}",
                                   "Each slice = share of the total dataset",
                                   chart_type="categorical"))
            break

    # ── 5. Correlation Heatmap ───────────────────────────────────
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().round(2)
        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            labels=dict(color="Correlation")
        )
        fig.update_xaxes(tickangle=-30, title_font_size=13)
        fig.update_yaxes(title_font_size=13)
        charts.append(finalize(fig, "Correlation Heatmap",
                                "Values close to ±1 = strong relationship. Blue = positive, Red = negative",
                                chart_type="relationship"))

    # ── 6. Scatter Plot with trendline ───────────────────────────
    if len(numeric_cols) >= 2:
        try:
            import statsmodels  # noqa: F401
            trendline = "ols"
        except ImportError:
            trendline = None

        for i in range(min(3, len(numeric_cols) - 1)):
            x_col = numeric_cols[i]
            y_col = numeric_cols[i + 1]
            kwargs = dict(
                x=x_col, y=y_col,
                color_discrete_sequence=[COLORS[2]],
                opacity=0.75,
                labels={x_col: x_col.replace("_", " ").title(),
                        y_col: y_col.replace("_", " ").title()}
            )
            if trendline:
                kwargs["trendline"] = trendline
                kwargs["trendline_color_override"] = "#ffd200"
            fig = px.scatter(df, **kwargs)
            fig.update_xaxes(title_text=x_col.replace("_", " ").title(), title_font_size=13)
            fig.update_yaxes(title_text=y_col.replace("_", " ").title(), title_font_size=13)
            charts.append(finalize(fig,
                                   f"{x_col.replace('_', ' ').title()} vs {y_col.replace('_', ' ').title()}",
                                   "Scatter plot — yellow line = trend (OLS regression)" if trendline else "Scatter plot showing relationship between two variables",
                                   chart_type="relationship"))

    # ── 7. Time-series / trend line ─────────────────────────────
    for col in cat_cols + numeric_cols:
        if any(k in col.lower() for k in ("year", "date", "month", "time", "period")):
            try:
                temp_df = df.copy()
                if df[col].dtype == "object":
                    temp_df[col] = pd.to_datetime(df[col], errors="coerce")
                if not temp_df[col].isnull().all() and numeric_cols:
                    target = numeric_cols[0]
                    trend = temp_df.sort_values(col).groupby(col)[target].mean().reset_index()
                    fig = px.line(
                        trend, x=col, y=target, markers=True,
                        color_discrete_sequence=[COLORS[4]],
                        labels={col: col.replace("_", " ").title(),
                                target: target.replace("_", " ").title()}
                    )
                    fig.update_xaxes(title_text=col.replace("_", " ").title(), title_font_size=13)
                    fig.update_yaxes(title_text=f"Avg {target.replace('_', ' ').title()}", title_font_size=13)
                    charts.append(finalize(fig,
                                           f"Trend Over Time: {target.replace('_', ' ').title()}",
                                           f"Average {target} grouped by {col} — shows time-based patterns",
                                           chart_type="relationship"))
            except Exception:
                pass

    return charts[:20]