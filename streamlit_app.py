import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIG ---
ADJECTIVES = [
    "dirty", "weathered", "scarred", "ancient",
    "playful", "proud", "timid", "mute",
    "abundant", "elegant", "stubborn", "heavy"
]
SAVE_DIR = "saved_labels"
os.makedirs(SAVE_DIR, exist_ok=True)

st.title("📌 Mongrel Adjective Annotator")

# --- UPLOAD IMAGE ---
uploaded_image = st.file_uploader("Upload a material image", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    file_name = uploaded_image.name

    # --- SELECT ADJECTIVES ---
    selected_adjectives = st.multiselect("Select adjectives that describe this material:", ADJECTIVES)

    adjective_values = {}
    if selected_adjectives:
        st.subheader("Assign intensity (–1 = low, +1 = high):")
        for adj in selected_adjectives:
            val = st.slider(f"{adj}", -1.0, 1.0, 0.0, 0.1)
            adjective_values[adj] = val

    # --- SAVE BUTTON ---
    if st.button("Save Annotation"):
        data = {
            "filename": file_name,
            "adjectives": adjective_values
        }
        json_name = os.path.splitext(file_name)[0] + ".json"
        save_path = os.path.join(SAVE_DIR, json_name)

        with open(save_path, "w") as f:
            json.dump(data, f, indent=4)

        st.success(f"Saved annotation to {save_path}")
        st.json(data)

import shutil
import zipfile
import io

# --- ZIP & DOWNLOAD ---
st.markdown("---")
st.subheader("📦 Download All JSON Annotations")

if st.button("Download All as ZIP"):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file_name in os.listdir(SAVE_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(SAVE_DIR, file_name)
                zip_file.write(file_path, arcname=file_name)

    zip_buffer.seek(0)
    st.download_button(
        label="📥 Click to Download ZIP",
        data=zip_buffer,
        file_name="material_annotations.zip",
        mime="application/zip"
    )

