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
    
    # 1. Broad Dataset Health
    rows, cols = df.shape
    missing_pct = (df.isnull().sum().sum() / (rows * cols)) * 100
    insights.append(f"AI Audit: Analyzed {rows} records across {cols} features. Data completeness is {100 - round(missing_pct, 2)}%.")
    
    # 2. Key Pattern Detection (Correlations)
    num_df = df.select_dtypes(include=['number'])
    if len(num_df.columns) >= 2:
        corr = num_df.corr().stack().reset_index()
        corr.columns = ['v1', 'v2', 'val']
        strong = corr[(corr['v1'] != corr['v2']) & (corr['val'].abs() > 0.6)].sort_values(by='val', ascending=False)
        if not strong.empty:
            row = strong.iloc[0]
            sentiment = "positive" if row['val'] > 0 else "inverse"
            insights.append(f"Strategic Insight: A significant {sentiment} correlation ({round(row['val'], 2)}) found between '{row['v1']}' and '{row['v2']}'.")

    # 3. Categorical Dominance
    cat_df = df.select_dtypes(exclude=['number'])
    if not cat_df.empty:
        top_cat_col = cat_df.columns[0]
        mode_val = df[top_cat_col].mode()[0]
        mode_pct = (df[top_cat_col] == mode_val).mean() * 100
        insights.append(f"Market Concentration: '{mode_val}' is the dominant value in {top_cat_col}, representing {round(mode_pct, 1)}% of the dataset.")

    # 4. Outlier Awareness
    if not num_df.empty:
        # Detect if any col has high skewness / outliers
        for col in num_df.columns[:2]:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]
            if not outliers.empty:
                insights.append(f"Volatility Alert: Column '{col}' contains {len(outliers)} statistical outliers. These might warrant further inspection.")

    # 5. Recommendation
    insights.append("Recommendation: Use the 'Predictive Insights' panel below to see how these patterns translate into forecasting models.")

    return insights