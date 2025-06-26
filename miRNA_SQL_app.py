import streamlit as st
import pandas as pd
import sqlite3
import os
import requests
import zipfile
from io import BytesIO

# -------------------------
# Helper: Download Drive Files
# -------------------------
def download_from_gdrive(file_id):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    resp = session.get(URL, params={'id': file_id}, stream=True)

    token = None
    for key, val in resp.cookies.items():
        if key.startswith('download_warning'):
            token = val
            break
    if token:
        resp = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)
    return resp.content

# -------------------------
# Folder-to-Drive mapping
# -------------------------
drive_folders = {
    "mirna_drug_interactions": "1m0DvNX6LqycrHFoxlLuM7VTz40ZpYDIW",
    "mirna_mrna_tf_interactions": "1iIub1GuyQYj1s8yrFrGXXN5SBtHwHq3x",
    "mirna_ncrnas_interactions": "1eLRsGhwzWCgx1-jsJ6nUTWeUvlLC9a4Y",
    "metrics": "1e36BwJyqrQT0Z8SIyIERy22uBCmkLJTZ",
    "mirna_disease_expression": "1aGsqj171C8ql-YAfRyCb9p-2XK3cEBHP",
    "reference_mirna": "1Zb6X6SLwYQtzkxW0E8Z92MHe-l5ip1eD",
    "mirna_snp": "1RT__ZP6dc_Wtb9EtcwlAT5GkySPKtUY8"
}

# -------------------------
# Step 1: Download & Extract CSV folders
# -------------------------
base = "data"
if not os.path.exists(base):
    os.makedirs(base)

for folder, gid in drive_folders.items():
    out_dir = os.path.join(base, folder)
    if not os.path.exists(out_dir):
        with st.spinner(f"Downloading {folder}..."):
            content = download_from_gdrive(gid)
            # Check if ZIP
            if content[:2] == b'PK':
                buf = BytesIO(content)
                with zipfile.ZipFile(buf) as z:
                    z.extractall(out_dir)
            else:
                st.error(f"Downloaded data for {folder} is not a zip!")
        st.success(f"{folder} ready!")

# -------------------------
# Step 2: Build SQLite DB
# -------------------------
db_path = "miRNA.db"
folders = list(drive_folders.keys())
if not os.path.exists(db_path):
    with st.spinner("Building miRNA.db from CSVs..."):
        conn = sqlite3.connect(db_path)
        joinables = []
        for folder in folders:
            fp = os.path.join(base, folder)
            for f in os.listdir(fp):
                if f.endswith(".csv"):
                    name = f.replace('.csv', '').replace('-', '_').lower()
                    tbl = f"{folder}_{name}"
                    try:
                        df = pd.read_csv(os.path.join(fp, f))
                        for c in df.columns:
                            if c.lower() in ['mirna_id', 'mirnaid']:
                                df.rename(columns={c: "miRNA_ID"}, inplace=True)
                                break
                        df.to_sql(tbl, conn, if_exists="replace", index=False)
                        if "miRNA_ID" in df.columns:
                            joinables.append(tbl)
                    except Exception as e:
                        st.warning(f"Failed to import {f}: {e}")
        conn.commit()
        conn.close()
        st.success("Database built!")

# -------------------------
# Step 3: Streamlit UI
# -------------------------
st.title("🧬 miRNA SQL Explorer")

query = st.text_area("Enter SQL query:", height=200,
                    value="SELECT name FROM sqlite_master WHERE type='table';")

if st.button("Run Query"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        st.success("✅ Query successful!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "result.csv", "text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
