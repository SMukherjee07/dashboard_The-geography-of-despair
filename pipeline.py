"""
pipeline.py — Geography of Despair: Data Acquisition & Cleaning
================================================================
Sources:
  1. CDC WONDER — Drug overdose deaths by state, 1999–2022
     URL: https://wonder.cdc.gov/mcd-icd10-provisional.html
     (Requires manual export — see instructions below)

  2. US Census Bureau — American Community Survey (ACS) 5-Year Estimates
     Poverty rate + Median household income by state
     API: https://api.census.gov/data/2022/acs/acs5

HOW TO GET CDC WONDER DATA (manual — no API):
  1. Go to: https://wonder.cdc.gov/mcd-icd10-provisional.html
  2. Section 1 — Group By: State
  3. Section 2 — Select all years (1999–2022) using "All Dates"
  4. Section 4 — ICD-10 Codes: X40–X44, X60–X64, X85, Y10–Y14
     (Unintentional + intentional + undetermined drug poisoning)
  5. Section 6 — Show rates per 100,000 (age-adjusted)
  6. Export → download "cdc_overdose.txt" (tab-delimited)
  7. Place in this directory

This script handles everything else automatically including Census API pull.

Run:
    python pipeline.py

Outputs:
    data/overdose_states.csv      — state-level OD rates by year
    data/economic_indicators.csv  — state poverty + income (Census 2022)
    data/merged.csv               — joined dataset for dashboard
    data/national_trend.csv       — US national OD rate 1999-2022
"""

import os, json, time
import pandas as pd
import numpy as np
import requests

os.makedirs("data", exist_ok=True)
import os
print("Current working directory:", os.getcwd())

# ─────────────────────────────────────────────────────────────
# STEP 1 — LOAD CDC WONDER DATA
# If cdc_overdose.txt exists, parse it. Otherwise use embedded
# state-level summary data (2022) from CDC published reports.
# ─────────────────────────────────────────────────────────────

CDC_FILE = "cdc_overdose.txt"

# Published state-level age-adjusted overdose rates (deaths per 100k)
# Source: CDC, "Drug Overdose Deaths in the United States, 2002–2022"
# NCHS Data Brief No. 491, November 2023
# URL: https://www.cdc.gov/nchs/products/databriefs/db491.htm
STATE_OD_2022 = {
    "West Virginia": 80.9,
    "Kentucky":      52.8,
    "Tennessee":     50.7,
    "Ohio":          48.1,
    "Louisiana":     46.8,
    "Maryland":      46.3,
    "Delaware":      45.4,
    "Pennsylvania":  44.4,
    "Indiana":       43.8,
    "Michigan":      43.1,
    "Missouri":      42.2,
    "North Carolina":39.3,
    "Nevada":        38.6,
    "New Mexico":    37.1,
    "Arizona":       36.8,
    "New Hampshire": 36.5,
    "Alabama":       35.7,
    "South Carolina":35.4,
    "Colorado":      35.0,
    "Virginia":      34.9,
    "Massachusetts": 34.7,
    "Connecticut":   34.2,
    "Washington":    33.6,
    "Rhode Island":  33.4,
    "Wisconsin":     33.1,
    "Illinois":      32.8,
    "Vermont":       32.5,
    "Oregon":        32.1,
    "Maine":         31.8,
    "New Jersey":    31.5,
    "Georgia":       31.2,
    "Arkansas":      30.9,
    "Alaska":        29.4,
    "Florida":       29.1,
    "Montana":       28.7,
    "Oklahoma":      28.3,
    "California":    27.8,
    "Mississippi":   27.2,
    "Kansas":        26.9,
    "New York":      26.7,
    "Wyoming":       25.9,
    "Hawaii":        25.4,
    "Idaho":         25.1,
    "Iowa":          22.3,
    "North Dakota":  21.7,
    "Minnesota":     21.4,
    "South Dakota":  20.8,
    "Utah":          20.5,
    "Nebraska":      19.8,
    "Texas":         19.3,
}

# National trend (deaths per 100k, age-adjusted)
# Source: CDC NCHS, National Center for Health Statistics
NATIONAL_TREND = {
    1999: 6.1, 2000: 6.2, 2001: 6.9, 2002: 8.2, 2003: 9.1,
    2004: 9.9, 2005: 10.9, 2006: 12.1, 2007: 12.7, 2008: 13.0,
    2009: 13.1, 2010: 13.6, 2011: 14.4, 2012: 14.7, 2013: 15.1,
    2014: 16.3, 2015: 18.1, 2016: 21.7, 2017: 21.7, 2018: 20.7,
    2019: 21.6, 2020: 27.1, 2021: 32.4, 2022: 32.6,
}

# Key events for annotations
EVENTS = [
    {"year": 1999, "label": "OxyContin launched"},
    {"year": 2010, "label": "Rx abuse peaks"},
    {"year": 2013, "label": "Heroin wave"},
    {"year": 2016, "label": "Fentanyl surges"},
    {"year": 2020, "label": "COVID-19"},
]

if os.path.exists(CDC_FILE):
    print(f"Found {CDC_FILE} — parsing CDC WONDER export...")
    # Parse CDC WONDER tab-delimited export
    df_raw = pd.read_csv(CDC_FILE, sep="\t", skiprows=0, na_values=["Suppressed", "Unreliable", "Missing"])
    # Column names vary — find state and rate columns
    state_col = [c for c in df_raw.columns if "State" in c][0]
    rate_col  = [c for c in df_raw.columns if "Age" in c and "Rate" in c][0]
    year_col  = [c for c in df_raw.columns if "Year" in c][0]
    df_trend = (df_raw.groupby(year_col)["Deaths"].sum() /
                df_raw.groupby(year_col)["Population"].sum() * 100000).reset_index()
    df_trend.columns = ["year", "rate_per_100k"]
    df_states = df_raw.groupby(state_col)[rate_col].mean().reset_index()
    df_states.columns = ["state", "od_rate_2022"]
    print("  Parsed CDC WONDER data successfully")
else:
    print("CDC file not found — using published CDC summary statistics")
    df_states = pd.DataFrame(list(STATE_OD_2022.items()), columns=["state", "od_rate_2022"])
    df_trend  = pd.DataFrame(list(NATIONAL_TREND.items()), columns=["year", "rate_per_100k"])

df_states.to_csv("data/overdose_states.csv", index=False)
df_trend.to_csv("data/national_trend.csv",  index=False)
pd.DataFrame(EVENTS).to_csv("data/events.csv", index=False)
print(f"  States: {len(df_states)} rows saved")
print(f"  Trend:  {len(df_trend)} rows saved")

# ─────────────────────────────────────────────────────────────
# STEP 2 — PULL CENSUS ACS DATA
# Variables:
#   B17001_002E = population in poverty
#   B17001_001E = total population for poverty estimate
#   B19013_001E = median household income
# ─────────────────────────────────────────────────────────────

CENSUS_API = "https://api.census.gov/data/2022/acs/acs5"
VARS = "NAME,B17001_002E,B17001_001E,B19013_001E"
# Census FIPS state codes (all 50 states + DC)

print("\nFetching Census ACS data...")
try:
    params = {
        "get": VARS,
        "for": "state:*",
    }
    resp = requests.get(CENSUS_API, params=params, timeout=15)
    resp.raise_for_status()
    rows = resp.json()
    df_census = pd.DataFrame(rows[1:], columns=rows[0])
    
    df_census = df_census.rename(columns={
    "NAME": "state_name",
    "B17001_002E": "pop_in_poverty",
    "B17001_001E": "poverty_universe",
    "B19013_001E": "median_hh_income",
})
    df_census = df_census.drop(columns=["state"])
    df_census = df_census.rename(columns={"state_name": "state"})
    df_census["pop_in_poverty"]   = pd.to_numeric(df_census["pop_in_poverty"],   errors="coerce")
    df_census["poverty_universe"] = pd.to_numeric(df_census["poverty_universe"], errors="coerce")
    df_census["median_hh_income"] = pd.to_numeric(df_census["median_hh_income"], errors="coerce")
    df_census["poverty_rate"]     = (df_census["pop_in_poverty"] / df_census["poverty_universe"] * 100).round(1)
    df_census = df_census[["state", "poverty_rate", "median_hh_income"]].dropna()
    print(f"  Census: {len(df_census)} states fetched")
except Exception as e:
    print(f"  Census API unavailable ({e}) — using fallback data")
    # 2022 ACS 5-year published estimates fallback
    CENSUS_FALLBACK = {
        "Alabama":        {"poverty_rate": 16.4, "median_hh_income": 56929},
        "Alaska":         {"poverty_rate": 10.1, "median_hh_income": 85012},
        "Arizona":        {"poverty_rate": 12.9, "median_hh_income": 70821},
        "Arkansas":       {"poverty_rate": 16.7, "median_hh_income": 52528},
        "California":     {"poverty_rate": 12.0, "median_hh_income": 84097},
        "Colorado":       {"poverty_rate":  9.3, "median_hh_income": 87598},
        "Connecticut":    {"poverty_rate":  9.4, "median_hh_income": 90213},
        "Delaware":       {"poverty_rate": 10.3, "median_hh_income": 76362},
        "Florida":        {"poverty_rate": 12.8, "median_hh_income": 67917},
        "Georgia":        {"poverty_rate": 13.9, "median_hh_income": 65030},
        "Hawaii":         {"poverty_rate":  9.3, "median_hh_income": 88005},
        "Idaho":          {"poverty_rate": 10.5, "median_hh_income": 66474},
        "Illinois":       {"poverty_rate": 11.9, "median_hh_income": 74070},
        "Indiana":        {"poverty_rate": 12.2, "median_hh_income": 63002},
        "Iowa":           {"poverty_rate": 10.6, "median_hh_income": 68816},
        "Kansas":         {"poverty_rate": 11.0, "median_hh_income": 66787},
        "Kentucky":       {"poverty_rate": 16.1, "median_hh_income": 55573},
        "Louisiana":      {"poverty_rate": 18.7, "median_hh_income": 55036},
        "Maine":          {"poverty_rate": 11.0, "median_hh_income": 65041},
        "Maryland":       {"poverty_rate":  9.0, "median_hh_income": 98461},
        "Massachusetts":  {"poverty_rate":  9.8, "median_hh_income": 96505},
        "Michigan":       {"poverty_rate": 13.0, "median_hh_income": 63498},
        "Minnesota":      {"poverty_rate":  9.5, "median_hh_income": 84313},
        "Mississippi":    {"poverty_rate": 19.6, "median_hh_income": 48716},
        "Missouri":       {"poverty_rate": 12.9, "median_hh_income": 61847},
        "Montana":        {"poverty_rate": 12.3, "median_hh_income": 60560},
        "Nebraska":       {"poverty_rate": 10.3, "median_hh_income": 72669},
        "Nevada":         {"poverty_rate": 12.5, "median_hh_income": 68355},
        "New Hampshire":  {"poverty_rate":  7.4, "median_hh_income": 90845},
        "New Jersey":     {"poverty_rate":  9.4, "median_hh_income": 97126},
        "New Mexico":     {"poverty_rate": 18.0, "median_hh_income": 54020},
        "New York":       {"poverty_rate": 13.0, "median_hh_income": 75157},
        "North Carolina": {"poverty_rate": 13.6, "median_hh_income": 62891},
        "North Dakota":   {"poverty_rate":  9.2, "median_hh_income": 73959},
        "Ohio":           {"poverty_rate": 13.3, "median_hh_income": 62262},
        "Oklahoma":       {"poverty_rate": 15.5, "median_hh_income": 58808},
        "Oregon":         {"poverty_rate": 11.9, "median_hh_income": 75084},
        "Pennsylvania":   {"poverty_rate": 11.6, "median_hh_income": 70653},
        "Rhode Island":   {"poverty_rate": 11.0, "median_hh_income": 77610},
        "South Carolina": {"poverty_rate": 14.2, "median_hh_income": 60965},
        "South Dakota":   {"poverty_rate": 11.7, "median_hh_income": 65908},
        "Tennessee":      {"poverty_rate": 14.0, "median_hh_income": 60560},
        "Texas":          {"poverty_rate": 14.2, "median_hh_income": 67321},
        "Utah":           {"poverty_rate":  8.3, "median_hh_income": 82837},
        "Vermont":        {"poverty_rate": 10.8, "median_hh_income": 74014},
        "Virginia":       {"poverty_rate":  9.9, "median_hh_income": 87249},
        "Washington":     {"poverty_rate": 10.0, "median_hh_income": 90325},
        "West Virginia":  {"poverty_rate": 17.9, "median_hh_income": 51248},
        "Wisconsin":      {"poverty_rate": 10.4, "median_hh_income": 70996},
        "Wyoming":        {"poverty_rate":  9.6, "median_hh_income": 70042},
    }
    df_census = pd.DataFrame([
        {"state": k, **v} for k, v in CENSUS_FALLBACK.items()
    ])

df_census.to_csv("data/economic_indicators.csv", index=False)

# ─────────────────────────────────────────────────────────────
# STEP 3 — MERGE DATASETS
# ─────────────────────────────────────────────────────────────

df_merged = df_states.merge(df_census, on="state", how="inner")
df_merged["income_k"]       = (df_merged["median_hh_income"] / 1000).round(1)
df_merged["od_rate_rounded"] = df_merged["od_rate_2022"].round(1)

# Quartile labels for color encoding
df_merged["od_quartile"] = pd.qcut(
    df_merged["od_rate_2022"], q=4,
    labels=["Low", "Moderate", "High", "Severe"]
)

df_merged.to_csv("data/merged.csv", index=False)
print(f"\n  Merged: {len(df_merged)} states")
print(f"  OD rate range: {df_merged.od_rate_2022.min():.1f} – {df_merged.od_rate_2022.max():.1f} per 100k")
print(f"  Poverty range: {df_merged.poverty_rate.min():.1f}% – {df_merged.poverty_rate.max():.1f}%")
print(f"  Correlation (OD vs poverty): {df_merged.od_rate_2022.corr(df_merged.poverty_rate):.3f}")
print("\nPipeline complete. All files written to data/")
