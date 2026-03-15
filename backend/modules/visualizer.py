import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

def generate_charts(df):
    charts = []
    
    # Configuration for all charts
    CHART_WIDTH = 800
    CHART_HEIGHT = 500
    THEME = "plotly_dark"
    
    # 0. Intelligent Column Filtering
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    # Skip ID-like columns (high cardinality)
    useful_cats = [col for col in cat_cols if 1 < df[col].nunique() < 20]
    
    def apply_layout(fig, title):
        fig.update_layout(
            width=CHART_WIDTH,
            height=CHART_HEIGHT,
            title=dict(text=title, x=0.5, xanchor='center'),
            template=THEME,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, b=80, t=80)
        )
        return fig

    # 1. Histograms & Box Plots for Numeric Data
    for col in numeric_cols[:2]: # Top 2 numeric columns
        # Histogram
        fig_hist = px.histogram(df, x=col, title=f"Distribution of {col}", 
                               color_discrete_sequence=['#539bf5'], marginal="rug")
        charts.append(json.loads(apply_layout(fig_hist, f"Distribution Analysis: {col}").to_json()))
        
        # Box Plot
        fig_box = px.box(df, y=col, title=f"Statistical Range: {col}", 
                        color_discrete_sequence=['#79c0ff'])
        charts.append(json.loads(apply_layout(fig_box, f"Outlier & Range Analysis: {col}").to_json()))

    # 2. Scatter Plot (if at least 2 numeric columns exist)
    if len(numeric_cols) >= 2:
        fig_scatter = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                               title=f"Relationship: {numeric_cols[0]} vs {numeric_cols[1]}",
                               color_discrete_sequence=['#d2a8ff'], opacity=0.7)
        charts.append(json.loads(apply_layout(fig_scatter, "Bivariate Analysis (Scatter Plot)").to_json()))

    # 3. Bar charts for Categorical Data
    for col in useful_cats[:1]:
        val_counts = df[col].value_counts().reset_index().head(10)
        val_counts.columns = [col, 'Count']
        fig_bar = px.bar(val_counts, x=col, y='Count', 
                        title=f"Top 10 Categories in {col}", 
                        color='Count', color_continuous_scale='Blues')
        charts.append(json.loads(apply_layout(fig_bar, f"Category Frequency: {col}").to_json()))

    # 4. Pie Chart
    for col in cat_cols:
        if 2 <= df[col].nunique() <= 8:
            fig_pie = px.pie(df, names=col, title=f"Proportional Breakdown: {col}", 
                           hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            charts.append(json.loads(apply_layout(fig_pie, f"Composition Analysis: {col}").to_json()))
            break

    # 5. Correlation Heatmap
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        fig_heatmap = px.imshow(corr_matrix, text_auto=True, 
                               title="Feature Correlation Heatmap",
                               color_continuous_scale="RdBu_r", origin="lower")
        charts.append(json.loads(apply_layout(fig_heatmap, "Correlation Matrix (Heatmap)").to_json()))

    return charts