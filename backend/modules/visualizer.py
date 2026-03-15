import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

def generate_charts(df):
    charts = []
    
    # Dashboard Config
    CHART_WIDTH = 750
    CHART_HEIGHT = 450
    THEME = "plotly_dark"
    COLORS = px.colors.qualitative.G10
    
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    def finalize(fig, title):
        fig.update_layout(
            template=THEME,
            title=dict(text=title, x=0.5, xanchor='center', font=dict(size=18)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, b=60, t=80),
            hovermode="x unified"
        )
        return json.loads(fig.to_json())

    # 1. Distribution Pair (Top Numeric)
    for col in numeric_cols[:4]:
        if df[col].nunique() > 1:
            # Histogram with Density
            fig = px.histogram(df, x=col, marginal="box", color_discrete_sequence=[COLORS[0]])
            charts.append(finalize(fig, f"Distribution: {col}"))
            
            # Violin Plot
            fig = px.violin(df, y=col, box=True, points="all", color_discrete_sequence=[COLORS[1]])
            charts.append(finalize(fig, f"Detail Analysis: {col}"))

    # 2. Categorical Breakdown
    for col in [c for c in cat_cols if 1 < df[c].nunique() < 15][:3]:
        # Bar Chart
        counts = df[col].value_counts().reset_index().head(10)
        counts.columns = [col, 'Value']
        fig = px.bar(counts, x=col, y='Value', color=col, color_discrete_sequence=COLORS)
        charts.append(finalize(fig, f"Category Comparison: {col}"))
        
        # Pie Chart
        if df[col].nunique() <= 8:
            fig = px.pie(df, names=col, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            charts.append(finalize(fig, f"Population Split: {col}"))

    # 3. Relationship (Scatter + Heatmap)
    if len(numeric_cols) >= 2:
        # Correlation Heatmap
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r")
        charts.append(finalize(fig, "Statistical Correlation Matrix"))
        
        # Bivariate Scatters – try OLS trendline, fall back to none
        try:
            import statsmodels  # noqa: F401
            trendline = "ols"
        except ImportError:
            trendline = None

        for i in range(min(2, len(numeric_cols) - 1)):
            kwargs = dict(x=numeric_cols[i], y=numeric_cols[i + 1],
                          color_discrete_sequence=[COLORS[2]])
            if trendline:
                kwargs['trendline'] = trendline
                kwargs['trendline_color_override'] = 'red'
            fig = px.scatter(df, **kwargs)
            charts.append(finalize(fig, f"Relational: {numeric_cols[i]} vs {numeric_cols[i+1]}"))


    # 4. Sequential/Trend Analysis (If date-like exists)
    for col in cat_cols + numeric_cols:
        if "year" in col.lower() or "date" in col.lower() or "month" in col.lower():
            try:
                temp_df = df.copy()
                if df[col].dtype == 'object':
                    temp_df[col] = pd.to_datetime(df[col], errors='coerce')
                
                if not temp_df[col].isnull().all():
                    temp_df = temp_df.sort_values(by=col)
                    # Aggregated trend
                    if numeric_cols:
                        trend = temp_df.groupby(col)[numeric_cols[0]].mean().reset_index()
                        fig = px.line(trend, x=col, y=numeric_cols[0], markers=True)
                        charts.append(finalize(fig, f"Time Series Trend: {numeric_cols[0]} over {col}"))
            except:
                pass

    return charts[:20] # Limit to 20 best graphs