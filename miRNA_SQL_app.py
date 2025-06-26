import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="miRNA SQL Explorer", layout="wide")
st.title("miRNA SQL Explorer")

# ---------- File Mapping ----------
csv_mapping = {
    "core_mirna": ["merged_mirBase.csv", "miRstart_human_miRNA_information.csv"],
    "core_gene": ["miRstart_human_miRNA_TSS_information.csv"],
    "core_disease": ["HMDD.csv", "dbDEMC_low_throughput.csv", "miRcancer.csv", "plasmiR.csv"],
    "core_snp": ["miRNASNPv4_SNP_associations_multiCancer_celltype.csv", "miRNASNPv4_pre-miRNA_variants.csv", "miRNet-snp-mir-hsa.csv", "MiRNet-snpmirbs-hsa.csv"],
    "core_drug": ["miRNet-mir-mol-hsa.csv", "ncDR_Curated_DRmiRNA.csv", "ncDR_Predicted_DRmiRNA.csv"],
    "core_metadata": ["miRNA_similarity_scores_ALL.csv"],
    "relationships": ["miRNet-mir-tf-hsa.csv", "miRNet-mir-epi-hsa.csv", "miRNet-mir-lncRNA.csv", "miRNet-mir-pseudogene.csv", "miRNet-mir-sncRNA.csv"]
}

db_path = "miRNA.db"
loaded_tables = []

# ---------- Database Build ----------
if not os.path.exists(db_path):
    st.info("Creating database from CSV files...")
    conn = sqlite3.connect(db_path)

    for category, files in csv_mapping.items():
        for filename in files:
            table_name = f"{category}_{filename.replace('.csv', '').replace('-', '_')}".lower()
            try:
                df = pd.read_csv(filename)
                # Standardize miRNA_ID column
                for col in df.columns:
                    if col.strip().lower() in ["mirna_id", "mirnaid"]:
                        df.rename(columns={col: "miRNA_ID"}, inplace=True)
                        break
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                loaded_tables.append((filename, table_name))
                st.success(f"✅ Loaded: {table_name}")
            except Exception as e:
                st.error(f"❌ Error loading {filename}: {e}")
    conn.commit()
    conn.close()
    st.success("🎉 Database created!")

# ---------- Sidebar: CSV to Table Mapping ----------
st.sidebar.markdown("### 📦 CSV → SQL Table Mapping")

# Organize tables by category
grouped = {}
for csv_name, table_name in loaded_tables:
    category = table_name.split("_")[0]  # e.g., "core"
    group = table_name.split("_")[1]     # e.g., "mirna"
    full_group = f"{category}_{group}"
    grouped.setdefault(full_group, []).append((csv_name, table_name))

# Show each group in expandable dropdown
for group, items in sorted(grouped.items()):
    with st.sidebar.expander(group, expanded=False):
        for csv, table in sorted(items):
            st.markdown(f"- `{csv}` → `{table}`")

# ---------- SQL Query Interface ----------
st.markdown("### Run SQL Query")

query = st.text_area(
    "Enter SQL query below:",
    value="SELECT name FROM sqlite_master WHERE type='table';",
    height=200
)

if st.button("Run Query"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        st.success("✅ Query successful!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "query_results.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ Error: {e}")
