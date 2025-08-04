import streamlit as st
import os
import json
from PIL import Image
from datetime import datetime
import zipfile
import io

# Load adjectives
ADJECTIVE_FILE = "adjectives.txt"
SAVED_DIR = "saved_labels"

# Ensure saved_labels directory exists
os.makedirs(SAVED_DIR, exist_ok=True)

# Try loading adjectives
try:
    with open(ADJECTIVE_FILE, "r") as f:
        adjectives = [line.strip() for line in f.readlines() if line.strip()]
except FileNotFoundError:
    adjectives = []

# App title
st.set_page_config(page_title="Mongrel Assemblies Adjective Annotator")
st.title("🐾 Mongrel Adjective Annotator")

# Tabs
tab1, tab2 = st.tabs(["📤 Annotate Image", "📁 View & Download Saved"])

with tab1:
    uploaded_file = st.file_uploader("Upload a material image (JPG or PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded image", use_column_width=True)

        st.subheader("Step 2: Select adjectives that describe this material")
        selected_adjectives = st.multiselect("Choose one or more poetic descriptors", adjectives)

        st.subheader("Optional notes or location")
        notes = st.text_area("Notes")

        if st.button("💾 Save Annotation"):
            base_name = os.path.splitext(uploaded_file.name)[0]
            output_filename = f"{base_name}.json"
            output_path = os.path.join(SAVED_DIR, output_filename)

            annotation = {
                "filename": uploaded_file.name,
                "adjectives": selected_adjectives,
                "notes": notes
            }

            with open(output_path, "w") as f:
                json.dump(annotation, f, indent=2)

            st.success(f"Annotation saved to {output_filename}")

with tab2:
    st.subheader("Saved Annotations")

    json_files = [f for f in os.listdir(SAVED_DIR) if f.endswith(".json")]

    if not json_files:
        st.info("No annotations found.")
    else:
        for file in sorted(json_files):
            with open(os.path.join(SAVED_DIR, file), "r") as f:
                data = json.load(f)
            st.markdown(f"**{file}**")
            st.write(data)

        # Download all as ZIP
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zipf:
            for file in json_files:
                file_path = os.path.join(SAVED_DIR, file)
                zipf.write(file_path, arcname=file)
        buffer.seek(0)

        st.download_button(
            label="📦 Download All Annotations (.zip)",
            data=buffer,
            file_name="mongrel_annotations.zip",
            mime="application/zip"
        )

