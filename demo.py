import pandas as pd
df = pd.DataFrame({
    "name": ["Ashif", None, "John"],
    "age": [25, 30, None]
})
print(df.isnull())
print(df.isna())