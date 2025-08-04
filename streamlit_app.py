import streamlit as st
import os
import json
from PIL import Image
from datetime import datetime

# Load adjectives from file
with open("adjectives.txt", "r") as f:
    adjectives = [line.strip() for line in f.readlines() if line.strip()]

st.title(" Mongrel Material  Adjective Annotator")

uploaded_file = st.file_uploader("Upload a material image (JPG or PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_column_width=True)

    st.subheader("Step 2: Select adjectives that describe this material")
    selected_adjectives = st.multiselect("Choose one or more poetic descriptors", adjectives)

    st.subheader("Optional notes or location")
    notes = st.text_area("Notes")

    if st.button(" Save Annotation"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.splitext(uploaded_file.name)[0]
        output_filename = f"{filename}_{timestamp}.json"
        output_path = os.path.join("saved_labels", output_filename)

        annotation = {
            "filename": uploaded_file.name,
            "adjectives": selected_adjectives,
            "notes": notes
        }

        os.makedirs("saved_labels", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(annotation, f, indent=2)

        st.success(f"Annotation saved to saved_labels/{output_filename}")
