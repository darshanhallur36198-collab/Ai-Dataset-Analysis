def dataset_statistics(df):
    stats = {}
    stats["rows"] = df.shape[0]
    stats["columns"] = df.shape[1]
    stats["summary"] = df.describe().to_dict()
    stats["missing"] = df.isnull().sum().to_dict()
    stats["insights"] = generate_narrative_insights(df)
    return stats

def generate_narrative_insights(df):
    insights = []
    
    # Row/Col insights
    insights.append(f"Your dataset contains {df.shape[0]} records across {df.shape[1]} variables.")
    
    # Missing data insights
    missing = df.isnull().sum()
    total_missing = missing.sum()
    if total_missing > 0:
        top_missing_col = missing.idxmax()
        insights.append(f"AI Detected {total_missing} missing values. The column '{top_missing_col}' has the most gaps.")
    else:
        insights.append("Data Health: Perfect! No missing values detected.")
        
    # Correlation insights
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty and len(numeric_df.columns) > 1:
        corr = numeric_df.corr().stack().reset_index()
        corr.columns = ['v1', 'v2', 'val']
        high_corr = corr[corr['v1'] != corr['v2']].sort_values(by='val', ascending=False).head(1)
        if not high_corr.empty:
            row = high_corr.iloc[0]
            insights.append(f"Strong Pattern: '{row['v1']}' and '{row['v2']}' show a strong positive relationship ({round(row['val'], 2)}).")

    # Outreach insight
    cat_cols = df.select_dtypes(include=['object']).columns
    if not cat_cols.empty:
        top_cat = df[cat_cols[0]].mode()[0]
        insights.append(f"Trend: The most frequent category in '{cat_cols[0]}' is '{top_cat}'.")

    return insights