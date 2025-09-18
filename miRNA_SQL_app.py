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
    st.markdown("### Tables")

    # ---- core_mirna ----
    st.markdown("#### core_mirna")

    with st.expander("merged_mirBase"):
        st.markdown("""
        - miRNA_ID
        - miRBase_acc
        - miRNA_sequence
        - miRNA_type
        """)

    with st.expander("miRstart_human_miRNA_information"):
        st.markdown("""
        - miRNA_ID
        - miRNA_location
        - PCG
        - PCG_embl
        - lncRNA_embl
        - Intragenic/Intergenic
        - PCG_exon/intron
        - lncRNA_exon/intron
        """)

    with st.expander("miRstart_human_miRNA_TF_information"):
        st.markdown("""
        - miRNA_ID
        - TF_ID
        - TF_gene
        - TF_entrez
        - TF_embl
        - Binding_site_location
        - Binding_score
        """)

    with st.expander("miRstart_human_miRNA_TSS_information"):
        st.markdown("""
        - miRNA_ID
        - miRBase_acc
        - TSS_position
        - TSS_score
        - TSS_CAGE
        - TSS_tag
        - TSS_DNase
        - TSS_H3K4me3
        - TSS_Pol II
        """)

    # ---- core_disease ----
    st.markdown("#### core_disease")

    with st.expander("dbDEMC_high_throughput"):
        st.markdown("""
        - miRNA_ID
        - ExperimentSourceInfo
        - Cell_line
        - logFC
        - Tvalue(LIMMA)
        - Pvalue
        - FDR
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("dbDEMC_low_throughput"):
        st.markdown("""
        - miRNA_ID
        - Cell_line
        - miRNA_expression
        - ExperimentSourceInfo
        - PMID
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("HMDD"):
        st.markdown("""
        - PMID
        - miRNA_ID
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("miRcancer"):
        st.markdown("""
        - miRNA_ID
        - miRNA_expression
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("plasmiR"):
        st.markdown("""
        - miRNA_ID
        - miRBase_acc
        - precursor_miRNA_id
        - PMID
        - diagnostic_marker
        - prognostic_marker
        - tested_prognostic_outcome
        - Biomarker_sample_type
        - miRNA_expression
        - Cell_line
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("miRNet-mir-epi-hsa"):
        st.markdown("""
        - miRNet_id
        - miRBase_acc
        - miRNA_ID
        - epi_regulator
        - epi_modification
        - miRNA_expression
        - PMID
        - epi_target
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    # ---- core_snp ----
    st.markdown("#### core_snp")

    with st.expander("miRNASNPv4_drug_SNP_associations_multiCancer"):
        st.markdown("""
        - Drug
        - CID
        - SNP_id
        - SNP_ref
        - SNP_alt
        - SNP_gene
        - SNP_location
        - SNP_effect
        - PMID
        """)

    with st.expander("miRNASNPv4_pre-miRNA_variants"):
        st.markdown("""
        - SNP_location
        - dbSNP_id
        - SNP_ref
        - SNP_alt
        - miRNA_ID
        - deltaG
        - miRNA_domain
        """)

    with st.expander("miRNASNPv4_SNP_associations_multiCancer_celltype"):
        st.markdown("""
        - Cell_line
        - Immune_cell_abundance
        - beta
        - Pvalue
        - FDR
        - SNP_ref
        - SNP_alt
        - SNP_Source
        - SNP_location
        - dbSNP_id
        - SNP_gene
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("miRNet-snp-mir-hsa"):
        st.markdown("""
        - miRNet_id
        - SNP_location
        - dbSNP_id
        - mature_miRNA_id
        - mature_miRBase_acc
        - miRNA_ID
        - miRBase_acc
        - miRNA_domain
        - SNP_High_Confidence
        - SNP_Robust_FANTOM5
        - Conserved_ADmiRE
        - AF_Percentile_gnomAD
        - Phastcons_100way
        """)

    with st.expander("miRNet-snpMIRBS-hsa"):
        st.markdown("""
        - miRNet_id
        - miRNA_ID
        - miRBase_acc
        - SNP_id
        - SNP_ref
        - SNP_alt
        - Binding_site
        - Binding_affinity
        - Prediction_score
        """)

    # ---- core_drug ----
    st.markdown("#### core_drug")

    with st.expander("miRNet-mir-mol-hsa"):
        st.markdown("""
        - miRNet_id
        - miRBase_acc
        - miRNA_ID
        - Drug
        - CID
        - SMILES
        - Cell_line
        - PMID
        - miRNA_expression
        """)

    with st.expander("ncDR_Curated_DRmiRNA"):
        st.markdown("""
        - PMID
        - miRNA_ID
        - miRBase_acc
        - Drug
        - CID
        - SMILES
        - miRNA_expression
        - Drug_effect
        - Target_gene
        - Regulation
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("ncDR_Predicted_DRmiRNA"):
        st.markdown("""
        - NSC_ID
        - Drug
        - CID
        - SMILES
        - miRNA_ID
        - miRBase_acc
        - Pvalue
        - Qvalue
        - logFC
        - miRNA_expression
        - Drug_effect_size
        - Drug_effect
        """)

    # ---- core_metadata ----
    st.markdown("#### core_metadata")

    with st.expander("miRNA_similarity_scores_ALL"):
        st.markdown("""
        - miRNA_ID
        - mesh_similarity
        - doid_similarity
        """)

    # ---- core_targets ----
    st.markdown("#### core_targets")

    with st.expander("miRTarBase_miRNA-target_interactions_human"):
        st.markdown("""
        - miRNA_ID
        - Target_gene
        - Target_entrez
        - Target_embl
        - Experiment
        - PMID
        - Support_type
        """)

    # ---- relationships ----
    st.markdown("#### relationships")

    with st.expander("miRNet-mir-circRNA"):
        st.markdown("""
        - miRNet_ID
        - miRBase_acc
        - miRNA_ID
        - circRNA_gene
        - circRNA_entrez
        - circRNA_embl
        """)

    with st.expander("miRNet-mir-lncRNA"):
        st.markdown("""
        - miRNet_ID
        - miRBase_acc
        - miRNA_ID
        - lncRNA_gene
        - lncRNA_entrez
        - lncRNA_embl
        """)

    with st.expander("miRNet-mir-pseudogene"):
        st.markdown("""
        - miRNet_ID
        - miRBase_acc
        - miRNA_ID
        - pseudogene
        - pseudogene_entrez
        - pseudogene_embl
        """)

    with st.expander("miRNet-mir-sncRNA"):
        st.markdown("""
        - miRNet_ID
        - miRBase_acc
        - miRNA_ID
        - snc_gene
        - snc_entrez
        - snc_embl
        """)

    with st.expander("miRNet-mir-tf-hsa"):
        st.markdown("""
        - miRNet_id
        - miRBase_acc
        - miRNA_ID
        - TF_gene
        - TF_gene_entrez
        - TF_gene_embl
        - TF_action_type
        - PMID
        """)


    # ---- core_metadata ----
    st.markdown("#### core_metadata")

    with st.expander("miRNA_similarity_scores_ALL"):
        st.markdown("""
        - miRNA_ID
        - mesh_similarity
        - doid_similarity
        """)

    # ---- relationships ----
    st.markdown("#### relationships")

    with st.expander("miRNet-mir-tf-hsa"):
        st.markdown("""
        - miRNet_id
        - miRBase_acc
        - miRNA_ID
        - TF_gene
        - TF_gene_entrez
        - TF_gene_embl
        - TF_action_type
        - PMID
        """)

    with st.expander("miRNet-mir-epi-hsa"):
        st.markdown("""
        - miRNet_id
        - miRBase_acc
        - miRNA_ID
        - epi_regulator
        - epi_modification
        - miRNA_expression
        - PMID
        - epi_target
        - Disease
        - Disease_MESH_ID
        - Disease_DOID_ID
        - Disease_categories
        - Disease_main_type
        - Disease_sub_type
        """)

    with st.expander("miRNet-mir-lncRNA"):
        st.markdown("""
        - miRNet_ID
        - miRBase_acc
        - miRNA_ID
        - lncRNA_gene
        - lncRNA_entrez
        - lncRNA_embl
        """)

    with st.expander("miRNet-mir-pseudogene"):
        st.markdown("""
        - miRNet_ID
        - miRBase_acc
        - miRNA_ID
        - pseudogene
        - pseudogene_entrez
        - pseudogene_embl
        """)

    with st.expander("miRNet-mir-sncRNA"):
        st.markdown("""
        - miRNet_ID
        - miRBase_acc
        - miRNA_ID
        - snc_gene
        - snc_entrez
        - snc_embl
        """)

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
