import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="miRNA SQL Explorer", layout="wide")
st.title("miRNA SQL Explorer")

# Utility: convert Google Drive link to CSV download URL
def gdrive_to_url(link):
    if "drive.google.com" in link:
        file_id = link.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return link

# Google Drive mapping: {category: {table: url}}
gdrive_mapping = {
    "core_mirna": {
        "merged_mirBase": "https://drive.google.com/file/d/1dhzlyBHb6CEQGsBKWZsBDhAYxAxAt2nN/view?usp=drive_link",
        "miRstart_human_miRNA_information": "https://drive.google.com/file/d/1ephymfpOHvitTifL-HuFwndt5IvVCz7J/view?usp=drive_link",
        "miRstart_human_miRNA_TF_information": "https://drive.google.com/file/d/1ccq7DzsJ_HUHgfH2_h88-3iGmqW52t60/view?usp=drive_link",
        "miRstart_human_miRNA_TSS_information": "https://drive.google.com/file/d/1N_k7Mpgt2Oj9SiddnH41zQvXdXrVMQBQ/view?usp=drive_link"
    },
    "core_disease": {
        "dbDEMC_highthroughput": "https://drive.google.com/file/d/1Qh9ueE9tc7YgPIzQTgXE6haiqei8RFux/view?usp=drive_link",
        "dbDEMC_lowthroughput": "https://drive.google.com/file/d/1SaGFCy7p-RGVdS4c1kdZl3QK5TAFmwGQ/view?usp=drive_link",
        "HMDD": "https://drive.google.com/file/d/1nKzyvtSYa6p-pTD5MRhj56pivOcdllv1/view?usp=drive_link",
        "miRcancer": "https://drive.google.com/file/d/1dmaBgeBmjoIR6wlGCay-kxipXC-_vDji/view?usp=drive_link",
        "plasmiR": "https://drive.google.com/file/d/1QCv9LZx3luDJHqQjtnTItoZO3hBjcjI8/view?usp=drive_link",
        "miRnet_mir_epi_hsa": "https://drive.google.com/file/d/1LYWv7yrjDiraNjvYKeHS0H-V7fTEUBe5/view?usp=drive_link"
    },
    "core_drug": {
        "miRnet_mir_mol_hsa": "https://drive.google.com/file/d/13n94gfF2GRxskTBXfSbRA1d_ACey1Vin/view?usp=drive_link",
        "ncDR_curated_DRmiRNA": "https://drive.google.com/file/d/1JrvbQBLYFb09KnCV58q7q91rXzyG3Qjv/view?usp=drive_link",
        "ncDR_predicted_DRmiRNA": "https://drive.google.com/file/d/1_LBCoRNDl1wNSmPVuaRXIvb3AWc8WPgm/view?usp=drive_link"
    },
    "core_snp": {
        "miRNASNPv4_drug_SNP_associations_multiCancer": "https://drive.google.com/file/d/1SPzRmopBfPYPRoNOUIBwqj26IJAOgxg-/view?usp=drive_link",
        "miRNASNPv4_pre_miRNA_variants": "https://drive.google.com/file/d/1gxSz3ZBWuqvGtmeKu_vhqX4yramlqROK/view?usp=drive_link",
        "miRNASNPv4_SNP_associations_multiCancer_celltype": "https://drive.google.com/file/d/155Us9c37WmKGdi6J_1lQlwZw3yIDjbRE/view?usp=drive_link",
        "miRNet_snp_mir_hsa": "https://drive.google.com/file/d/1LPmEqGi_kVEc5aguKJp0HGSV8IXEJ7Ia/view?usp=drive_link",
        "miRNet_snpmirbs_hsa": "https://drive.google.com/file/d/19JsPnaan1uXPYzlm3SuRq8otNT_5vcWr/view?usp=drive_link"
    },
    "core_metadata": {
        "miRNA_similarity_scores_ALL": "https://drive.google.com/file/d/1gRasm8Xzxow38t3Se8Bbrw07ITfYinvW/view?usp=drive_link"
    },
    "relationships": {
        "miRNet_mir_tf_hsa": "https://drive.google.com/file/d/1VbxUDa8XA-SCplQ20rDlBdbKj7_FVThC/view?usp=drive_link",
        "miRNet_mir_circRNA": "https://drive.google.com/file/d/1hcGaxdZlygqSWQkoUeEWJCLK6YpxI0g2/view?usp=drive_link",
        "miRNet_mir_lncRNA": "https://drive.google.com/file/d/1vgvqxkRPQJOIPWynppAysBxB7U2W-Isp/view?usp=drive_link",
        "miRNet_mir_pseudogene": "https://drive.google.com/file/d/19ElJ3ejyJvqzGgwMLrhBKmh88wbiubXQ/view?usp=drive_link",
        "miRNet_mir_sncRNA": "https://drive.google.com/file/d/1hg46HM7b2ZuQppz5GxDgrqA4AxK02BTt/view?usp=drive_link"
    },
    "core_targets": {
        "miRTarBase_MTI_human": "https://drive.google.com/file/d/1sJs6lgKVRRI_WXJhdj_Tptotl34pKys_/view?usp=drive_link"
    }
}

db_path = "miRNA.db"
loaded_tables = []

# Build database if not exists
if not os.path.exists(db_path):
    st.info("Creating database...")
    conn = sqlite3.connect(db_path)

    for category, files in gdrive_mapping.items():
        for table_name, gdrive_link in files.items():
            try:
                csv_url = gdrive_to_url(gdrive_link)
                df = pd.read_csv(csv_url)

                # Standardize miRNA_ID column
                for col in df.columns:
                    if col.strip().lower() in ["mirna_id", "mirnaid"]:
                        df.rename(columns={col: "miRNA_ID"}, inplace=True)
                        break

                df.to_sql(f"{category}_{table_name}".lower(), conn, if_exists="replace", index=False)
                loaded_tables.append((table_name, f"{category}_{table_name}"))
                st.success(f"✅ Loaded: {category}_{table_name}")
            except Exception as e:
                st.error(f"❌ Error loading {table_name}: {e}")

    conn.commit()
    conn.close()
    st.success("🎉 Database created!")

# Sidebar Schema Browser
with st.sidebar:
    st.markdown("### Schema Browser")
    for category, files in gdrive_mapping.items():
        st.markdown(f"#### {category}")
        for table_name in files.keys():
            with st.expander(table_name):
                st.markdown("_Columns will appear after first DB build_")

# SQL Query Interface
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
    except Exception as e:
        st.error(f"❌ Error: {e}")
