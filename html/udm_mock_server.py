from fastapi import FastAPI, HTTPException
import pandas as pd

# Load your dataset (CSV generated earlier)
df = pd.read_csv("udm_clone_fittings.csv")

app = FastAPI(title="UDM Clone API")

@app.get("/fittings")
def get_all_fittings():
    return df.to_dict(orient="records")

@app.get("/fittings/{rid}")
def get_fitting(rid: str):
    row = df[df["rid"] == rid]
    if row.empty:
        raise HTTPException(status_code=404, detail="Fitting not found")
    return row.to_dict(orient="records")[0]
