import streamlit as st
import pandas as pd
import sqlite3
import os

st.title("🧬 miRNA SQL Explorer")

# Group files by category
csv_mapping = {
    "core_mirna": ["merged_mirBase.csv", "miRstart_human_miRNA_information.csv"],
    "core_gene": ["miRstart_human_miRNA_TSS_information.csv"],
    "core_disease": ["HMDD.csv", "dbDEMC_low_throughput.csv", "miRcancer.csv", "plasmiR.csv"],
    "core_snp": ["miRNASNPv4_SNP_associations_multiCancer_celltype.csv", "miRNASNPv4_pre-miRNA_variants.csv", "miRNet-snp-mir-hsa.csv", "miRNet-snpmirbs-hsa.csv"],
    "core_drug": ["miRNet-mir-mol-hsa.csv", "ncDR_Curated_DRmiRNA.csv", "ncDR_Predicted_DRmiRNA.csv"],
    "core_metadata": ["miRNA_similarity_scores_ALL.csv"],
    "relationships": ["miRNet-mir-tf-hsa.csv", "miRNet-mir-epi-hsa.csv", "miRNet-mir-lncRNA.csv", "miRNet-mir-pseudogene.csv", "miRNet-mir-sncRNA.csv"]
}

db_path = "miRNA.db"

# -------------------------
# Step 1: Build SQLite DB
# -------------------------
if not os.path.exists(db_path):
    st.info("⏳ Creating database from CSV files...")
    conn = sqlite3.connect(db_path)
    for category, files in csv_mapping.items():
        for filename in files:
            table_name = f"{category}_{filename.replace('.csv', '').replace('-', '_')}".lower()
            try:
                df = pd.read_csv(filename)
                for col in df.columns:
                    if col.strip().lower() in ["mirna_id", "mirnaid"]:
                        df.rename(columns={col: "miRNA_ID"}, inplace=True)
                        break
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                st.success(f"✅ Loaded: {table_name}")
            except Exception as e:
                st.error(f"❌ Error loading {filename}: {e}")
    conn.commit()
    conn.close()
    st.success("🎉 Database created!")

# -------------------------
# Step 2: SQL Query Interface
# -------------------------
st.markdown("### 🔎 Enter your SQL query:")
query = st.text_area("SQL Query", value="SELECT name FROM sqlite_master WHERE type='table';", height=200)

if st.button("Run Query"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        st.success("✅ Query successful!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download results", csv, "query_results.csv", "text/csv")
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
