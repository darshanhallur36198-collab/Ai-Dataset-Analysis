from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import pandas as pd

def auto_train_model(df):
    target_col = df.columns[-1]  # Assume last column is target for simplicity

    # Only train if target is numeric and we have other numeric columns to use as features
    if not pd.api.types.is_numeric_dtype(df[target_col]):
        return {"error": "Target column is not numeric. Classification not yet implemented."}

    # Grab only numeric features, drop the target
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    
    if target_col not in numeric_df.columns or len(numeric_df.columns) < 2:
         return {"error": "Not enough numeric features to train a model."}

    X = numeric_df.drop(columns=[target_col])
    y = numeric_df[target_col]

    # Combine X and y to drop rows with NaN in either
    temp_df = pd.concat([X, y], axis=1).dropna()
    
    if temp_df.empty:
        return {"error": "Dataset became empty after dropping rows with missing target values."}
        
    X = temp_df.drop(columns=[target_col])
    y = temp_df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    score = r2_score(y_test, predictions)
    import math

    safe_score = round(score, 4)
    if math.isnan(safe_score) or math.isinf(safe_score):
        safe_score = None

    return {
        "target_column": target_col,
        "model_type": "RandomForestRegressor",
        "r2_score": safe_score,
        "features_used": list(X.columns)
    }
