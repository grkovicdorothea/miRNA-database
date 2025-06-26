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
with st.sidebar:
    st.markdown("### Core Tables")
    st.markdown("#### core_mirna")
    with st.expander("merged_mirBase"):
        st.markdown("\n- miRNA_ID\n- miRBase_acc\n- miRNA_sequence\n- miRNA_type")
    with st.expander("miRstart_human_miRNA_information"):
        st.markdown("\n- miRNA_ID\n- miRNA_location\n- PCG\n- PCG_embl\n- lncRNA_embl\n- Intragenic/Intergenic\n- PCG_exon/intron\n- lncRNA_exon/intron")
    st.markdown("#### core_gene")
    with st.expander("miRstart_human_miRNA_TSS_information"):
        st.markdown("\n- miRNA_ID\n- miRBase_acc\n- TSS_position\n- TSS_score\n- TSS_CAGE\n- TSS_tag\n- TSS_DNase\n- TSS_H3K4me3\n- TSS_Pol II")
    st.markdown("#### core_disease")
    with st.expander("HMDD"):
        st.markdown("\n- PMID\n- miRNA_ID\n- Disease\n- Disease_MESH_ID\n- Disease_DOID_ID\n- Disease_categories\n- Disease_main_type\n- Disease_sub_type")
    with st.expander("dbDEMC_low_throughput"):
        st.markdown("\n- miRNA_ID\n- Cell_line\n- miRNA_expression\n- ExperimentSourceInfo\n- PMID\n- Disease\n- Disease_MESH_ID\n- Disease_DOID_ID\n- Disease_categories\n- Disease_main_type\n- Disease_sub_type")
    with st.expander("miRcancer"):
        st.markdown("\n- miRNA_ID\n- miRNA_expression\n- Disease\n- Disease_MESH_ID\n- Disease_DOID_ID\n- Disease_categories\n- Disease_main_type\n- Disease_sub_type")
    with st.expander("plasmiR"):
        st.markdown("\n- miRNA_ID\n- miRBase_acc\n- precursor_miRNA_id\n- PMID\n- diagnostic_marker\n- prognostic_marker\n- tested_prognostic_outcome\n- Biomarker_sample_type\n- miRNA_expression\n- Cell_line\n- Disease\n- Disease_MESH_ID\n- Disease_DOID_ID\n- Disease_categories\n- Disease_main_type\n- Disease_sub_type")
    st.markdown("#### core_snp")
    with st.expander("miRNASNPv4_SNP_associations_multiCancer_celltype"):
        st.markdown("\n- Cell_line\n- Immune_cell_abundance\n- beta\n- Pvalue\n- FDR\n- SNP_ref\n- SNP_alt\n- SNP_Source\n- SNP_location\n- dbSNP_id\n- SNP_gene\n- Disease\n- Disease_MESH_ID\n- Disease_DOID_ID\n- Disease_categories\n- Disease_main_type\n- Disease_sub_type")
    with st.expander("miRNASNPv4_pre-miRNA_variants"):
        st.markdown("\n- SNP_location\n- dbSNP_id\n- SNP_ref\n- SNP_alt\n- miRNA_ID\n- deltaG\n- miRNA_domain")
    with st.expander("miRNet-snp-mir-hsa"):
        st.markdown("\n- miRNet_id\n- SNP_location\n- dbSNP_id\n- mature_miRNA_id\n- mature_miRBase_acc\n- miRNA_ID\n- miRBase_acc\n- miRNA_domain\n- SNP_High_Confidence\n- SNP_Robust_FANTOM5\n- Conserved_ADmiRE\n- AF_Percentile_gnomAD\n- Phastcons_100way")
    with st.expander("MiRNet-snpmirbs-hsa"):
        st.markdown("- _No columns found_")
    st.markdown("#### core_drug")
    with st.expander("miRNet-mir-mol-hsa"):
        st.markdown("\n- miRNet_id\n- miRBase_acc\n- miRNA_ID\n- Drug\n- CID\n- SMILES\n- Cell_line\n- PMID\n- miRNA_expression")
    with st.expander("ncDR_Curated_DRmiRNA"):
        st.markdown("\n- PMID\n- miRNA_ID\n- miRBase_acc\n- Drug\n- CID\n- SMILES\n- miRNA_expression\n- Drug_effect\n- Target_gene\n- Regulation\n- Disease\n- Disease_MESH_ID\n- Disease_DOID_ID\n- Disease_categories\n- Disease_main_type\n- Disease_sub_type")
    with st.expander("ncDR_Predicted_DRmiRNA"):
        st.markdown("\n- NSC_ID\n- Drug\n- CID\n- SMILES\n- miRNA_ID\n- miRBase_acc\n- Pvalue\n- Qvalue\n- logFC\n- miRNA_expression\n- Drug_effect_size\n- Drug_effect")
    st.markdown("#### core_metadata")
    with st.expander("miRNA_similarity_scores_ALL"):
        st.markdown("\n- miRNA_ID\n- mesh_similarity\n- doid_similarity")
    st.markdown("#### relationships")
    with st.expander("miRNet-mir-tf-hsa"):
        st.markdown("\n- miRNet_id\n- miRBase_acc\n- miRNA_ID\n- TF_gene\n- TF_gene_entrez\n- TF_gene_embl\n- TF_action_type\n- PMID")
    with st.expander("miRNet-mir-epi-hsa"):
        st.markdown("\n- miRNet_id\n- miRBase_acc\n- miRNA_ID\n- epi_regulator\n- epi_modification\n- miRNA_expression\n- PMID\n- epi_target\n- Disease\n- Disease_MESH_ID\n- Disease_DOID_ID\n- Disease_categories\n- Disease_main_type\n- Disease_sub_type")
    with st.expander("miRNet-mir-lncRNA"):
        st.markdown("\n- miRNet_ID\n- miRBase_acc\n- miRNA_ID\n- lncRNA_gene \n- lncRNA_entrez\n- lncRNA_embl")
    with st.expander("miRNet-mir-pseudogene"):
        st.markdown("\n- miRNet_ID\n- miRBase_acc\n- miRNA_ID\n- pseudogene\n- pseudogene_entrez\n- pseudogene_embl")
    with st.expander("miRNet-mir-sncRNA"):
        st.markdown("\n- miRNet_ID\n- miRBase_acc\n- miRNA_ID\n- snc_gene\n- snc_entrez\n- snc_embl")
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
