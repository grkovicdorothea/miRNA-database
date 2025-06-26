import streamlit as st
import pandas as pd
import sqlite3
import requests

# --- Google Drive download function ---
def download_file_from_google_drive(file_id, destination):
    URL = "https://drive.google.com/uc?export=download"

    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

# --- Define file location ---
file_id = "1i-IJd4m_7S02XQ9nJ15EMUx3JkEnrOl3"
db_path = "miRNA.db"

# --- Download once (if not already downloaded) ---
if not os.path.exists(db_path):
    with st.spinner("Downloading database..."):
        download_file_from_google_drive(file_id, db_path)
        st.success("Database downloaded!")

# --- Streamlit UI ---
st.title("miRNA SQL Explorer")

query = st.text_area("Enter your SQL query below:", height=200)

if st.button("Run Query"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        st.success("Query executed successfully!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download results", csv, "query_results.csv", "text/csv")

    except Exception as e:
        st.error(f"Error running query: {e}")
