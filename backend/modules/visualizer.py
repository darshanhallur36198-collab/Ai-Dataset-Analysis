import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

def generate_charts(df):
    charts = []
    
    # 0. Intelligent Column Filtering
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    # Identify and skip ID-like columns (high cardinality categorical)
    useful_cats = [col for col in cat_cols if df[col].nunique() > 1 and df[col].nunique() < 20]
    id_like_cats = [col for col in cat_cols if df[col].nunique() >= 20]
    
    # 1. Premium 3D Scatter Plot (if we have at least 3 numeric columns)
    if len(numeric_cols) >= 3:
        fig = px.scatter_3d(
            df, 
            x=numeric_cols[0], 
            y=numeric_cols[1], 
            z=numeric_cols[2],
            color=numeric_cols[0],
            template="plotly_dark",
            title=f"3D Insight: {numeric_cols[0]}, {numeric_cols[1]}, {numeric_cols[2]}",
            opacity=0.8,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        charts.append(json.loads(fig.to_json()))

    # 2. Histograms for Numeric Data (Filter columns with only 1 value)
    plotted_nums = 0
    for col in numeric_cols:
        if df[col].nunique() > 1 and plotted_nums < 2:
            fig = px.histogram(df, x=col, template="plotly_dark", 
                               title=f"Distribution Analysis: {col}", 
                               color_discrete_sequence=['#539bf5'],
                               marginal="box") # Added box plot for clarity
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            charts.append(json.loads(fig.to_json()))
            plotted_nums += 1

    # 3. Bar charts for Categorical Data (Limit to top 10 categories for clarity)
    plotted_cats = 0
    for col in useful_cats:
        if plotted_cats < 1:
            val_counts = df[col].value_counts().reset_index().head(10)
            val_counts.columns = [col, 'Count']
            fig = px.bar(val_counts, x=col, y='Count', template="plotly_dark", 
                         title=f"Top Categories: {col}", 
                         color=col,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            charts.append(json.loads(fig.to_json()))
            plotted_cats += 1

    # 4. Pie Chart for low cardinality data
    for col in cat_cols:
        if 2 <= df[col].nunique() <= 6:
            fig = px.pie(df, names=col, title=f"Proportion: {col}", 
                         template="plotly_dark",
                         hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            charts.append(json.loads(fig.to_json()))
            break # Just one pie chart

    return charts