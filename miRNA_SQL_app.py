import streamlit as st
import pandas as pd
import sqlite3
import requests
import os

# -----------------------
# Google Drive Downloader
# -----------------------
def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)

    # Handle confirmation token if present
    def get_confirm_token(resp):
        for key, value in resp.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    token = get_confirm_token(response)
    if token:
        response = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)

    # Download in chunks
    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

# -----------------------
# File setup
# -----------------------
file_id = "1i-IJd4m_7S02XQ9nJ15EMUx3JkEnrOl3"  # Your Google Drive file ID
db_path = "miRNA.db"

# Download if not already present
if not os.path.exists(db_path):
    with st.spinner("Downloading miRNA.db from Google Drive..."):
        download_file_from_google_drive(file_id, db_path)
        st.success("Database downloaded successfully!")

# -----------------------
# Streamlit UI
# -----------------------
st.title("🧬 miRNA SQL Explorer")
st.markdown("Enter an SQL query to explore the database:")

query = st.text_area("SQL Query", height=200, value="""
SELECT name FROM sqlite_master WHERE type='table';
""")

if st.button("Run Query"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()

        st.success("Query executed successfully!")
        st.dataframe(df)

        # Download as CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results", csv, "query_results.csv", "text/csv")

    except Exception as e:
        st.error(f"Error running query: {e}")
