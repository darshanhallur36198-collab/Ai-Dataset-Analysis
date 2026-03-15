import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

def generate_charts(df):
    charts = []
    
    # 1. Premium 3D Scatter Plot (if we have at least 3 numeric columns)
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    if len(numeric_cols) >= 3:
        fig = px.scatter_3d(
            df, 
            x=numeric_cols[0], 
            y=numeric_cols[1], 
            z=numeric_cols[2],
            color=numeric_cols[0],
            template="plotly_dark",
            title=f"3D Relationship: {numeric_cols[0]} vs {numeric_cols[1]} vs {numeric_cols[2]}",
            opacity=0.8,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        charts.append(json.loads(fig.to_json()))

    # 2. Histograms for Numeric Data
    for col in numeric_cols[:2]:
        fig = px.histogram(df, x=col, template="plotly_dark", title=f"Distribution of {col}", color_discrete_sequence=['#539bf5'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        charts.append(json.loads(fig.to_json()))

    # 3. Bar charts for Categorical Data
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols[:1]:
        val_counts = df[col].value_counts().reset_index()
        val_counts.columns = [col, 'Count']
        fig = px.bar(val_counts, x=col, y='Count', template="plotly_dark", title=f"Frequency of {col}", color_discrete_sequence=['#d2a8ff'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        charts.append(json.loads(fig.to_json()))

    return charts