import streamlit as st
import sqlite3
import pandas as pd

# Set the path to your SQLite database
DB_PATH = "/Users/dorotheagrkovic/Desktop/miRNA Database/miRNA.db"

# App title
st.title("miRNA SQL Explorer")

# SQL query input
query = st.text_area("Enter your SQL query below:", height=200)

# Run the query
if st.button("Run Query"):
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Display results
        st.success("Query executed successfully!")
        st.dataframe(df)

        # Optionally download the results
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", csv,
                           "query_results.csv", "text/csv")

    except Exception as e:
        st.error(f"Error running query: {e}")
