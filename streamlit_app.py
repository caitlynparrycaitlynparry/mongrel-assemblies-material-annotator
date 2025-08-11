import streamlit as st
import json
import os
import io
import zipfile
from datetime import datetime

# --- CONFIG ---
ADJECTIVES = [
    "dirty", "weathered", "scarred", "ancient",
    "playful", "proud", "timid", "sad",
    "abundant", "elegant", "light", "heavy"
]
SAVE_DIR = "saved_labels"
os.makedirs(SAVE_DIR, exist_ok=True)

st.set_page_config(page_title="Mongrel Adjective Annotator", layout="centered")
st.title("📌 Mongrel Adjective Annotator")

# ---------- Helpers for FLAT export ----------
def clamp(v: float, lo: float = -1.0, hi: float = 1.0) -> float:
    try:
        v = float(v)
    except Exception:
        return 0.0
    return max(lo, min(hi, v))

def filename_stem(path_or_name: str) -> str:
    """Return filename without extension."""
    base = os.path.basename(path_or_name or "").strip()
    stem, _ = os.path.splitext(base)
    return stem or "unknown"

def flatten_record(record: dict, *, do_lower: bool = True, do_clamp: bool = True, round_ndp: int = 4) -> dict:
    """
    Accepts either your nested shape:
      {"filename":"m003.jpg","adjectives":{"Weathered":0.3,"Dirty":0.1}}
    or already-flat:
      {"weathered":0.3,"dirty":0.1}
    Returns flat dict of lowercased keys (optional), clamped & rounded values.
    """
    if not isinstance(record, dict):
        return {}
    # Prefer nested 'adjectives' if present; else treat the record as already flat
    source = record.get("adjectives") if isinstance(record.get("adjectives"), dict) else record
    flat = {}
    for k, v in source.items():
        if k is None:
            continue
        key = str(k).strip()
        if do_lower:
            key = key.lower()
        val = clamp(v) if do_clamp else float(v)
        if round_ndp is not None and isinstance(round_ndp, int):
            val = round(val, round_ndp)
        flat[key] = val
    return flat

def load_saved_records(dir_path: str) -> list[tuple[str, dict]]:
    """
    Load all .json files in SAVE_DIR.
    Returns list of tuples: (json_filename, parsed_dict)
    Skips unreadable files gracefully.
    """
    out = []
    for fn in sorted(os.listdir(dir_path)):
        if not fn.lower().endswith(".json"):
            continue
        fp = os.path.join(dir_path, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            out.append((fn, data))
        except Exception as e:
            st.warning(f"⚠ Skipped '{fn}': {e}")
    return out

# ---------- Upload & annotate (nested save) ----------
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

    # --- SAVE BUTTON (nested structure) ---
    if st.button("💾 Save Annotation"):
        data = {
            "filename": file_name,
            "adjectives": adjective_values
        }
        json_name = filename_stem(file_name) + ".json"
        save_path = os.path.join(SAVE_DIR, json_name)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        st.success(f"Saved annotation to {save_path}")
        st.json(data)

st.markdown("---")
st.subheader("📦 Download All JSON Annotations (nested, as saved)")

if st.button("Download All (ZIP, nested)"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_name in os.listdir(SAVE_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(SAVE_DIR, file_name)
                zip_file.write(file_path, arcname=file_name)
    zip_buffer.seek(0)
    st.download_button(
        label="📥 Click to Download ZIP (nested)",
        data=zip_buffer,
        file_name="material_annotations_nested.zip",
        mime="application/zip"
    )

# ---------- FLAT EXPORT FOR UNITY ----------
st.markdown("---")
st.subheader("🧰 Export FLAT JSON for Unity (per-material files)")

col_a, col_b, col_c = st.columns(3)
with col_a:
    do_lower = st.checkbox("lowercase keys", value=True)
with col_b:
    do_clamp = st.checkbox("clamp to [-1,1]", value=True)
with col_c:
    round_ndp = st.number_input("round decimals", min_value=0, max_value=6, value=4, step=1)

records = load_saved_records(SAVE_DIR)
st.caption(f"Found {len(records)} saved file(s) in '{SAVE_DIR}'")

if st.button("👀 Preview first 3 (flat)"):
    preview_count = min(3, len(records))
    if preview_count == 0:
        st.info("No saved JSON files yet.")
    for i in range(preview_count):
        json_filename, data = records[i]
        name_from_record = filename_stem(data.get("filename", "")) if isinstance(data, dict) else ""
        out_name = name_from_record or filename_stem(json_filename)
        flat = flatten_record(data, do_lower=do_lower, do_clamp=do_clamp, round_ndp=round_ndp)
        st.code(json.dumps(flat, indent=2, ensure_ascii=False), language="json")
        st.caption(f"→ would export as: `{out_name}.json`")

# ZIP all flat files
if st.button("📥 Download All as ZIP (flat)"):
    if not records:
        st.warning("No saved JSON files to export.")
    else:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
            for json_filename, data in records:
                # choose output name: prefer record['filename'] stem, fall back to json file stem
                name_from_record = ""
                if isinstance(data, dict):
                    name_from_record = filename_stem(data.get("filename", ""))
                out_name = name_from_record or filename_stem(json_filename)
                flat = flatten_record(data, do_lower=do_lower, do_clamp=do_clamp, round_ndp=round_ndp)
                z.writestr(f"{out_name}.json", json.dumps(flat, ensure_ascii=False))
        zip_buf.seek(0)
        st.download_button(
            label="Download ZIP (flat for Unity)",
            data=zip_buf,
            file_name="adjectives_flat_json.zip",
            mime="application/zip"
        )

# Optional: individual downloads (expand to avoid clutter)
with st.expander("Download individually (flat)"):
    if not records:
       
