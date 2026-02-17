import sys
import numpy
import pandas as pd
from prophet import Prophet

print(f"Python version: {sys.version}")

# Train a dummy Prophet model
df = pd.DataFrame({'ds': pd.date_range('2023-01-01', periods=10), 'y': range(10)})
m = Prophet()
m.fit(df)
print("Prophet model trained.")

try:
    import xgboost
    print(f"XGBoost version: {xgboost.__version__}")
    print(f"XGBoost version: {xgboost.__version__}")
    print("XGBoost imported successfully!")
except ImportError as e:
    print(f"Failed to import xgboost: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
