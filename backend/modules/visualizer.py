import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

# ── Human-readable number formatter ─────────────────────────────
def fmt_num(n):
    """Convert 4970000 → '4.97M', 1300 → '1.3K', etc."""
    try:
        n = float(n)
        if abs(n) >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
        if abs(n) >= 1_000_000:     return f"{n/1_000_000:.1f}M"
        if abs(n) >= 1_000:         return f"{n/1_000:.1f}K"
        return f"{n:,.0f}"
    except Exception:
        return str(n)

def generate_charts(df):
    charts = []
    COLORS = ["#4C78A8","#F28E2B","#E15759","#76B7B2","#59A14F",
              "#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC"]

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()

    def finalize(fig, title: str, subtitle: str = "", chart_type: str = "other"):
        fig.update_layout(
            template="plotly_dark",
            title=dict(
                text=f"<b>{title}</b><br><sup style='color:#aaa'>{subtitle}</sup>" if subtitle else f"<b>{title}</b>",
                x=0.5, xanchor="center",
                font=dict(size=16, color="#ffffff")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(11,15,28,0.6)",
            margin=dict(l=150, r=50, b=80, t=100), # Increased left margin for horizontal labels
            font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#c9d1d9"),
            hoverlabel=dict(bgcolor="rgba(20,20,40,0.95)", font_size=13, font_color="#fff"),
            legend=dict(bgcolor="rgba(30,30,50,0.7)", borderwidth=0, font=dict(size=12)),
        )
        # Gridlines: light, subtle
        fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False,
                         tickfont=dict(size=12), title_font=dict(size=13))
        fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(size=12), title_font=dict(size=13))
        result = json.loads(fig.to_json())
        result["_chart_type"] = chart_type
        return result

    # ── Helper: format X axis ticks (since now horizontal) ──
    def fix_xaxis(fig):
        fig.update_xaxes(tickformat=",", exponentformat="none")
        return fig

    # ─────────────────────────────────────────────────────────────
    # 1. HORIZONTAL BAR CHART (for categorical × numeric)
    # ─────────────────────────────────────────────────────────────
    useful_cats = [c for c in cat_cols if 1 < df[c].nunique() <= 30]
    for cat_col in useful_cats[:3]:
        if numeric_cols:
            # Sum or count
            grouped = (df.groupby(cat_col)[numeric_cols[0]].sum()
                         .reset_index()
                         .sort_values(numeric_cols[0], ascending=True) # Ascending for horizontal (Plotly draws bottom-up)
                         .tail(10))
            grouped.columns = [cat_col, "Value"]

            # readable labels
            text_labels = [fmt_num(v) for v in grouped["Value"]]

            fig = go.Figure(go.Bar(
                y=grouped[cat_col],
                x=grouped["Value"],
                orientation='h',
                text=text_labels,
                textposition="outside",
                textfont=dict(size=12, color="#ffffff"),
                marker_color=COLORS[0],
                marker_line_width=0,
                hovertemplate=f"<b>%{{y}}</b><br>{numeric_cols[0]}: %{{text}}<extra></extra>",
            ))
            fix_xaxis(fig)
            fig.update_yaxes(title_text=cat_col.replace("_"," ").title())
            fig.update_xaxes(title_text=numeric_cols[0].replace("_"," ").title())
            charts.append(finalize(fig,
                f"Top 10 {cat_col.replace('_',' ').title()} by {numeric_cols[0].replace('_',' ').title()}",
                "Horizontal layout for better label readability",
                chart_type="categorical"))

        # Count chart
        counts = df[cat_col].value_counts().reset_index().tail(10).sort_values(cat_col, ascending=True)
        # Re-calc counts specifically to ensure top 10 are sorted correctly for horizontal
        counts = df[cat_col].value_counts().reset_index().head(10).sort_values('count', ascending=True)
        counts.columns = [cat_col, "Count"]
        text_labels = [fmt_num(v) for v in counts["Count"]]

        fig = go.Figure(go.Bar(
            y=counts[cat_col],
            x=counts["Count"],
            orientation='h',
            text=text_labels,
            textposition="outside",
            textfont=dict(size=12, color="#ffffff"),
            marker=dict(
                color=counts["Count"],
                colorscale="Blues",
                showscale=False,
                line_width=0,
            ),
            hovertemplate="<b>%{y}</b><br>Count: %{text}<extra></extra>",
        ))
        fix_xaxis(fig)
        fig.update_yaxes(title_text=cat_col.replace("_"," ").title())
        fig.update_xaxes(title_text="Number of Records")
        charts.append(finalize(fig,
            f"Distribution of {cat_col.replace('_',' ').title()}",
            "Frequency count per category (Top 10)",
            chart_type="categorical"))

    # ─────────────────────────────────────────────────────────────
    # 2. PIE / DONUT for low-cardinality categorical
    # ─────────────────────────────────────────────────────────────
    for col in cat_cols:
        if 2 <= df[col].nunique() <= 8:
            counts = df[col].value_counts().reset_index()
            counts.columns = [col, "Count"]
            fig = go.Figure(go.Pie(
                labels=counts[col],
                values=counts["Count"],
                hole=0.45,
                textinfo="label+percent",
                textfont=dict(size=13),
                marker=dict(colors=COLORS, line=dict(color="rgba(0,0,0,0)", width=2)),
                pull=[0.03] * len(counts),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
            ))
            charts.append(finalize(fig,
                f"Share of {col.replace('_',' ').title()}",
                "Each slice shows the percentage of total records",
                chart_type="categorical"))
            break

    # ─────────────────────────────────────────────────────────────
    # 3. HISTOGRAM for numeric columns
    # ─────────────────────────────────────────────────────────────
    for col in numeric_cols[:3]:
        if df[col].nunique() < 2:
            continue
        mean_v   = df[col].mean()
        median_v = df[col].median()
        fig = px.histogram(df, x=col, nbins=30,
                           color_discrete_sequence=[COLORS[0]])
        # Fix xaxis for histogram as it stays horizontal on X
        fig.update_xaxes(tickformat=",", exponentformat="none")
        fig.add_vline(x=mean_v,   line_dash="dash", line_color="#ffd200",
                      annotation_text=f"Mean: {fmt_num(mean_v)}",
                      annotation_position="top right",
                      annotation_font=dict(size=11, color="#ffd200"))
        fig.add_vline(x=median_v, line_dash="dot",  line_color="#38ef7d",
                      annotation_text=f"Median: {fmt_num(median_v)}",
                      annotation_position="top left",
                      annotation_font=dict(size=11, color="#38ef7d"))
        fig.update_xaxes(title_text=col.replace("_"," ").title())
        fig.update_yaxes(title_text="Frequency")
        charts.append(finalize(fig,
            f"How {col.replace('_',' ').title()} is Distributed",
            "Bars show how many records fall in each value range",
            chart_type="distribution"))

    # ─────────────────────────────────────────────────────────────
    # 4. BOX PLOT for outlier detection
    # ─────────────────────────────────────────────────────────────
    if numeric_cols:
        cols_for_box = numeric_cols[:4]
        fig = go.Figure()
        for i, col in enumerate(cols_for_box):
            fig.add_trace(go.Box(
                x=df[col], # Changed to X for horizontal box plots
                name=col.replace("_"," ").title(),
                marker_color=COLORS[i % len(COLORS)],
                boxmean=True,
                hovertemplate="<b>%{y}</b><br>Value: %{x}<extra></extra>",
            ))
        fix_xaxis(fig)
        charts.append(finalize(fig,
            "Outlier & Range Overview",
            "Horizontal box plots for clearer range comparison",
            chart_type="distribution"))

    # ─────────────────────────────────────────────────────────────
    # 5. HORIZONTAL STACKED BAR (categorical × second categorical)
    # ─────────────────────────────────────────────────────────────
    if len(useful_cats) >= 2 and numeric_cols:
        xc, cc = useful_cats[0], useful_cats[1]
        if df[xc].nunique() <= 15 and df[cc].nunique() <= 6:
            grouped = (df.groupby([xc, cc])[numeric_cols[0]].sum()
                         .reset_index()
                         .sort_values(numeric_cols[0], ascending=True))
            top_x = df[xc].value_counts().head(8).index
            grouped = grouped[grouped[xc].isin(top_x)]
            
            fig = px.bar(grouped, y=xc, x=numeric_cols[0], color=cc,
                         orientation='h',
                         barmode="group",
                         color_discrete_sequence=COLORS,
                         labels={xc: xc.replace("_"," ").title(),
                                 numeric_cols[0]: numeric_cols[0].replace("_"," ").title(),
                                 cc: cc.replace("_"," ").title()})
            fix_xaxis(fig)
            charts.append(finalize(fig,
                f"{numeric_cols[0].replace('_',' ').title()} by {xc.replace('_',' ').title()} & {cc.replace('_',' ').title()}",
                "Grouped horizontal bars for multi-variable comparison",
                chart_type="categorical"))

    # ─────────────────────────────────────────────────────────────
    # 6. CORRELATION HEATMAP
    # ─────────────────────────────────────────────────────────────
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().round(2)
        fig = px.imshow(corr, text_auto=True,
                        color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        # Heatmap labels remain same
        charts.append(finalize(fig,
            "Correlation Between Numeric Columns",
            "Blue = positive link, Red = negative link",
            chart_type="relationship"))

    # ─────────────────────────────────────────────────────────────
    # 7. SCATTER PLOT with trendline
    # ─────────────────────────────────────────────────────────────
    if len(numeric_cols) >= 2:
        try:
            import statsmodels  # noqa
            tl = "ols"
        except ImportError:
            tl = None

        for i in range(min(2, len(numeric_cols) - 1)):
            x_sc, y_sc = numeric_cols[i], numeric_cols[i + 1]
            kwargs = dict(x=x_sc, y=y_sc, opacity=0.65,
                          color_discrete_sequence=[COLORS[4]],
                          labels={x_sc: x_sc.replace("_"," ").title(),
                                  y_sc: y_sc.replace("_"," ").title()})
            if tl:
                kwargs["trendline"] = tl
                kwargs["trendline_color_override"] = "#ffd200"
            fig = px.scatter(df, **kwargs)
            # Fix axes for scatter
            fig.update_xaxes(tickformat=",", exponentformat="none")
            fig.update_yaxes(tickformat=",", exponentformat="none")
            charts.append(finalize(fig,
                f"{x_sc.replace('_',' ').title()} vs {y_sc.replace('_',' ').title()}",
                "Scatter plot showing relationship with trendline",
                chart_type="relationship"))

    # ─────────────────────────────────────────────────────────────
    # 8. LINE / TIME-SERIES
    # ─────────────────────────────────────────────────────────────
    for col in cat_cols + numeric_cols:
        if any(k in col.lower() for k in ("year","date","month","time","period")):
            try:
                tmp = df.copy()
                if df[col].dtype == "object":
                    tmp[col] = pd.to_datetime(df[col], errors="coerce")
                if not tmp[col].isnull().all() and numeric_cols:
                    target = numeric_cols[0]
                    trend  = tmp.sort_values(col).groupby(col)[target].mean().reset_index()
                    fig = go.Figure(go.Scatter(
                        x=trend[col], y=trend[target],
                        mode="lines+markers",
                        line=dict(color=COLORS[5], width=2),
                        marker=dict(size=7, color=COLORS[5]),
                        hovertemplate="<b>%{x}</b><br>Avg: %{y:,.0f}<extra></extra>",
                    ))
                    fig.update_yaxes(tickformat=",", exponentformat="none")
                    fig.update_xaxes(title_text=col.replace("_"," ").title())
                    fig.update_yaxes(title_text=f"Avg {target.replace('_',' ').title()}")
                    charts.append(finalize(fig,
                        f"Trend Over Time: {target.replace('_',' ').title()}",
                        f"Average of {target} grouped by {col}",
                        chart_type="relationship"))
            except Exception:
                pass

    return charts[:20]