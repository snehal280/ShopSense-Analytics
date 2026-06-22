"""
================================================================================
Script  : data_cleaning.py
Project : E-Commerce Customer Analysis
Author  : Your Name
Date    : 2024

Purpose :
    Load the raw UCI Online Retail II dataset, perform thorough data cleaning,
    validate data quality, and save a cleaned version ready for analysis.

Dataset :
    UCI Online Retail II
    URL: https://archive.ics.uci.edu/ml/datasets/Online+Retail+II
    File: online_retail_II.xlsx  (place in data/raw/)

How to run:
    python scripts/data_cleaning.py
================================================================================
"""

import pandas as pd          # For DataFrames and data manipulation
import numpy as np           # For numerical operations
import os                    # For file path handling
from tabulate import tabulate  # For pretty-printing summary tables

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: CONFIGURATION — File paths
# ─────────────────────────────────────────────────────────────────────────────
# __file__ is the path of the current script.
# os.path.dirname gets its folder. We navigate up one level to the project root.
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH   = os.path.join(BASE_DIR, "data", "raw", "online_retail_II.xlsx")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_transactions.csv")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
def load_data(filepath: str) -> pd.DataFrame:
    """
    Load the UCI Online Retail II Excel file.

    The dataset has two sheets (Year 2009-2010 and Year 2010-2011).
    We concatenate both into a single DataFrame for a full two-year view.

    Parameters:
        filepath (str): Path to the Excel file.

    Returns:
        pd.DataFrame: Combined raw dataset.
    """
    print("=" * 65)
    print("  STEP 1: LOADING DATA")
    print("=" * 65)

    print(f"\n📂 Reading file: {filepath}")
    print("   (This may take 30–60 seconds — the file has 1M+ rows)\n")

    # Read both sheets; sheet_name=None returns a dict {sheet_name: DataFrame}
    sheets = pd.read_excel(filepath, sheet_name=None, engine="openpyxl")

    # List all sheets found
    sheet_names = list(sheets.keys())
    print(f"   Sheets found: {sheet_names}")

    # Concatenate all sheets into one big DataFrame
    # ignore_index=True resets the row numbers so they are continuous
    df = pd.concat(sheets.values(), ignore_index=True)

    print(f"\n✅ Data loaded successfully!")
    print(f"   Total rows   : {len(df):,}")
    print(f"   Total columns: {df.shape[1]}")
    print(f"\n   Columns: {list(df.columns)}\n")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: DATA QUALITY ASSESSMENT
# ─────────────────────────────────────────────────────────────────────────────
def assess_quality(df: pd.DataFrame) -> None:
    """
    Print a full data quality report:
      - Shape (rows × columns)
      - Data types per column
      - Missing value counts
      - Duplicate row count
      - Sample of the data

    Parameters:
        df (pd.DataFrame): The raw dataset.
    """
    print("=" * 65)
    print("  STEP 2: DATA QUALITY ASSESSMENT")
    print("=" * 65)

    # Shape
    print(f"\n📊 Dataset shape: {df.shape[0]:,} rows × {df.shape[1]} columns\n")

    # Data types
    print("📋 Column data types:")
    dtype_table = [[col, str(dtype)] for col, dtype in df.dtypes.items()]
    print(tabulate(dtype_table, headers=["Column", "Type"], tablefmt="pretty"))

    # Missing values
    print("\n❓ Missing values per column:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "Missing Count": missing,
        "Missing %": missing_pct
    })
    print(tabulate(missing_df, headers="keys", tablefmt="pretty"))

    # Duplicates
    dup_count = df.duplicated().sum()
    print(f"\n🔁 Duplicate rows: {dup_count:,}")

    # Sample
    print("\n🔍 First 5 rows of raw data:")
    print(df.head(5).to_string())
    print()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: DATA CLEANING
# ─────────────────────────────────────────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning transformations to produce an analysis-ready dataset.

    Cleaning steps:
      1. Remove duplicate rows
      2. Drop rows with missing CustomerID (we need it for segmentation)
      3. Remove cancelled orders (InvoiceNo starts with 'C')
      4. Remove rows with Quantity <= 0  (returns or data errors)
      5. Remove rows with UnitPrice <= 0 (free items or errors)
      6. Remove test/placeholder entries (StockCode anomalies)
      7. Fix data types (InvoiceDate → datetime, CustomerID → int)
      8. Standardise text columns (strip whitespace, upper-case Country)

    Parameters:
        df (pd.DataFrame): Raw dataset.

    Returns:
        pd.DataFrame: Cleaned dataset.
    """
    print("=" * 65)
    print("  STEP 3: DATA CLEANING")
    print("=" * 65)

    initial_rows = len(df)
    print(f"\n📌 Starting rows: {initial_rows:,}\n")

    # ── 4.1 Remove duplicate rows ─────────────────────────────────────────────
    # Duplicate rows are exact copies — keeping the first occurrence is safest.
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"✅ [1/7] Removed {removed:,} duplicate rows")

    # ── 4.2 Drop rows with missing CustomerID ─────────────────────────────────
    # Without a CustomerID, we cannot link transactions to customers.
    # Dropping these is standard practice in customer-level analysis.
    before = len(df)
    df = df.dropna(subset=["Customer ID"])
    removed = before - len(df)
    print(f"✅ [2/7] Removed {removed:,} rows with missing Customer ID")

    # ── 4.3 Remove cancelled orders ───────────────────────────────────────────
    # Cancelled invoices start with the letter 'C' (e.g., C536379).
    # These represent refunded transactions — not actual purchases.
    # ~.str.startswith('C') means "NOT starting with C"
    before = len(df)
    df = df[~df["Invoice"].astype(str).str.startswith("C")]
    removed = before - len(df)
    print(f"✅ [3/7] Removed {removed:,} cancelled orders (Invoice starts with 'C')")

    # ── 4.4 Remove rows with non-positive Quantity ────────────────────────────
    # Quantity of 0 or negative means a return or data error — not a real sale.
    before = len(df)
    df = df[df["Quantity"] > 0]
    removed = before - len(df)
    print(f"✅ [4/7] Removed {removed:,} rows with Quantity ≤ 0")

    # ── 4.5 Remove rows with non-positive Price ───────────────────────────────
    # Price of 0 means a free item (often a test/sample). Negative = error.
    before = len(df)
    df = df[df["Price"] > 0]
    removed = before - len(df)
    print(f"✅ [5/7] Removed {removed:,} rows with Price ≤ 0")

    # ── 4.6 Remove test / non-standard StockCodes ─────────────────────────────
    # Some rows have placeholder StockCodes like 'POST', 'D', 'DOT', 'M', 'BANK CHARGES'.
    # These are not real products.
    NON_PRODUCT_CODES = ["POST", "D", "DOT", "M", "BANK CHARGES",
                         "PADS", "C2", "AMAZONFEE"]
    before = len(df)
    df = df[~df["StockCode"].astype(str).str.upper().isin(NON_PRODUCT_CODES)]
    removed = before - len(df)
    print(f"✅ [6/7] Removed {removed:,} rows with test/non-product StockCodes")

    # ── 4.7 Fix data types ────────────────────────────────────────────────────
    # InvoiceDate is read as a generic object; parse it as an actual datetime.
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # CustomerID should be an integer (pandas may read it as float due to NaNs).
    # We already dropped NaN CustomerIDs above, so this is safe.
    df["Customer ID"] = df["Customer ID"].astype(int)

    # Rename columns for convenience (remove the space)
    df = df.rename(columns={"Customer ID": "CustomerID", "Invoice": "InvoiceNo"})

    print(f"✅ [7/7] Fixed data types and renamed columns")

    # ── 4.8 Standardise text ──────────────────────────────────────────────────
    # Strip leading/trailing whitespace from string columns.
    df["Description"] = df["Description"].str.strip()
    df["Country"]     = df["Country"].str.strip().str.title()

    # ── Summary ───────────────────────────────────────────────────────────────
    final_rows  = len(df)
    total_removed = initial_rows - final_rows
    print(f"\n📋 Cleaning Summary:")
    print(f"   Original rows  : {initial_rows:,}")
    print(f"   Rows removed   : {total_removed:,} ({total_removed/initial_rows*100:.1f}%)")
    print(f"   Final rows     : {final_rows:,}\n")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: ADD BASIC DERIVED COLUMNS
# ─────────────────────────────────────────────────────────────────────────────
def add_basic_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a few simple derived columns used across all subsequent scripts.

    Columns added:
        TotalPrice   : Quantity × Price (revenue per line item)
        Year         : Year extracted from InvoiceDate
        Month        : Month number extracted from InvoiceDate
        YearMonth    : Period string like "2010-12" for monthly aggregations
        DayOfWeek    : 0=Monday … 6=Sunday

    Parameters:
        df (pd.DataFrame): Cleaned dataset.

    Returns:
        pd.DataFrame: Dataset with new columns appended.
    """
    print("=" * 65)
    print("  STEP 4: ADDING BASE COLUMNS")
    print("=" * 65)

    # Revenue per transaction line
    # Business meaning: how much money did this single line item generate?
    df["TotalPrice"] = df["Quantity"] * df["Price"]
    print("✅ Added: TotalPrice = Quantity × Price")

    # Time-based columns — useful for trend analysis
    df["Year"]      = df["InvoiceDate"].dt.year
    df["Month"]     = df["InvoiceDate"].dt.month
    df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["DayOfWeek"] = df["InvoiceDate"].dt.dayofweek   # 0 = Monday
    df["Hour"]      = df["InvoiceDate"].dt.hour
    print("✅ Added: Year, Month, YearMonth, DayOfWeek, Hour")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: SAVE CLEANED DATA
# ─────────────────────────────────────────────────────────────────────────────
def save_data(df: pd.DataFrame, filepath: str) -> None:
    """
    Save the cleaned DataFrame to a CSV file.
    CSV is preferred over Excel for speed and compatibility.

    Parameters:
        df       (pd.DataFrame): Cleaned dataset.
        filepath (str)         : Where to save the CSV.
    """
    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # index=False means don't write the row numbers (0, 1, 2...) into the file
    df.to_csv(filepath, index=False)
    print(f"\n💾 Cleaned data saved to: {filepath}")
    print(f"   Rows: {len(df):,}  |  Columns: {df.shape[1]}\n")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Run every step in sequence
    df_raw     = load_data(RAW_PATH)       # Step 1 – Load
    assess_quality(df_raw)                 # Step 2 – Quality check
    df_cleaned = clean_data(df_raw)        # Step 3 – Clean
    df_cleaned = add_basic_columns(df_cleaned)  # Step 4 – Add columns
    save_data(df_cleaned, CLEAN_PATH)      # Step 5 – Save

    print("=" * 65)
    print("  ✅ DATA CLEANING COMPLETE")
    print("=" * 65)
    print(f"\n  Next step → Run: python scripts/feature_engineering.py\n")
