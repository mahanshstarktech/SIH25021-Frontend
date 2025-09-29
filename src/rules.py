# src/rules.py
import csv
from typing import Optional, Dict, Any

# 1. Condition score mapping
CONDITION_SCORE = {
    "Low": 90,
    "Medium": 70,
    "High": 50,
    "Critical": 20
}

# 2. Predicted failure risk mapping
FAILURE_RISK = {
    "Low": "Low risk of failure within 12 months",
    "Medium": "Moderate risk of failure within 6 months",
    "High": "High risk of failure within 3 months",
    "Critical": "Immediate risk of failure; replacement required"
}

# 3. Suggested spare parts mapping
SUGGESTED_SKU = {
    "Crack": "BOLT-M10-A",
    "Rust": "NUT-M8-B",
    "Loose": "SCREW-M12-C"
}

# 4. Vendor alert check (read CSV)
VENDOR_CSV_PATH = "data/vendor_data.csv"

def check_vendor_alert(vendor: str, batch: str) -> Optional[str]:
    try:
        with open(VENDOR_CSV_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["vendor"] == vendor and row["batch"] == batch:
                    fail_rate = float(row["fail_rate"])
                    if fail_rate > 0.2:  # arbitrary threshold
                        return f"ALERT: {vendor} batch {batch} has {fail_rate*100:.0f}% higher failure rate than average"
        return None
    except FileNotFoundError:
        return None

def get_condition_score(severity: str) -> int:
    return CONDITION_SCORE.get(severity, 50)

def get_predicted_failure_risk(severity: str) -> str:
    return FAILURE_RISK.get(severity, "Unknown risk")

def get_suggested_sku(damage_type: str) -> str:
    return SUGGESTED_SKU.get(damage_type, "TBD")
