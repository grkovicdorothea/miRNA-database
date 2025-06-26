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

with st.sidebar.expander("core_mirna", expanded=False):
    st.markdown("- `merged_mirBase.csv` → `core_mirna_merged_mirbase`")
    st.markdown("- `miRstart_human_miRNA_information.csv` → `core_mirna_mirstart_human_mirna_information`")

with st.sidebar.expander("core_gene", expanded=False):
    st.markdown("- `miRstart_human_miRNA_TSS_information.csv` → `core_gene_mirstart_human_mirna_tss_information`")

with st.sidebar.expander("core_disease", expanded=False):
    st.markdown("- `HMDD.csv` → `core_disease_hmdd`")
    st.markdown("- `dbDEMC_low_throughput.csv` → `core_disease_dbdemc_low_throughput`")
    st.markdown("- `miRcancer.csv` → `core_disease_mircancer`")
    st.markdown("- `plasmiR.csv` → `core_disease_plasmir`")

with st.sidebar.expander("core_snp", expanded=False):
    st.markdown("- `miRNASNPv4_SNP_associations_multiCancer_celltype.csv` → `core_snp_mirnasnpv4_snp_associations_multicancer_celltype`")
    st.markdown("- `miRNASNPv4_pre-miRNA_variants.csv` → `core_snp_mirnasnpv4_pre_mirna_variants`")
    st.markdown("- `miRNet-snp-mir-hsa.csv` → `core_snp_mirnet_snp_mir_hsa`")
    st.markdown("- `miRNet-snpmirbs-hsa.csv` → `core_snp_mirnet_snpmirbs_hsa`")

with st.sidebar.expander("core_drug", expanded=False):
    st.markdown("- `miRNet-mir-mol-hsa.csv` → `core_drug_mirnet_mir_mol_hsa`")
    st.markdown("- `ncDR_Curated_DRmiRNA.csv` → `core_drug_ncdr_curated_drmirna`")
    st.markdown("- `ncDR_Predicted_DRmiRNA.csv` → `core_drug_ncdr_predicted_drmirna`")

with st.sidebar.expander("core_metadata", expanded=False):
    st.markdown("- `miRNA_similarity_scores_ALL.csv` → `core_metadata_mirna_similarity_scores_all`")

with st.sidebar.expander("relationships", expanded=False):
    st.markdown("- `miRNet-mir-tf-hsa.csv` → `relationships_mirnet_mir_tf_hsa`")
    st.markdown("- `miRNet-mir-epi-hsa.csv` → `relationships_mirnet_mir_epi_hsa`")
    st.markdown("- `miRNet-mir-lncRNA.csv` → `relationships_mirnet_mir_lncrna`")
    st.markdown("- `miRNet-mir-pseudogene.csv` → `relationships_mirnet_mir_pseudogene`")
    st.markdown("- `miRNet-mir-sncRNA.csv` → `relationships_mirnet_mir_sncrna`")

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
