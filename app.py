# app.py
import streamlit as st
import requests
from PIL import Image
import io
import time

st.set_page_config(page_title="Text → Image (mini DALL·E)", layout="wide")
st.title("🎨 Text → Image (mini DALL·E)")
st.markdown("Enter a prompt and generate an image (model runs on Hugging Face Inference API).")

# --- CONFIG: change model_id if you prefer another text-to-image model ---
MODEL_ID = "stabilityai/stable-diffusion-2-1" # <- change to any text-to-image model ID if you want

# read HF token from Streamlit secrets
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    HF_TOKEN = None

if HF_TOKEN is None:
    st.warning("No Hugging Face token found. Add HF_TOKEN in Streamlit Secrets (Manage app → Secrets).")
    st.stop()

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt: str):
    payload = {"inputs": prompt}
    # Long timeout because image generation may take time
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    if resp.status_code == 200:
        return Image.open(io.BytesIO(resp.content))
    # helpful debug messages
    try:
        err = resp.json()
    except Exception:
        err = resp.text
    st.error(f"Generation failed — status {resp.status_code}. Response: {err}")
    return None

# UI
prompt = st.text_area("Describe the image (example: 'A cute cat astronaut, digital art')", height=120)
col1, col2 = st.columns([1,3])
with col1:
    generate_btn = st.button("Generate image")

with col2:
    st.info("Tip: be specific (styles, colors, camera, mood). Example: 'A cinematic portrait of a samurai, dramatic lighting, 35mm film'")

if generate_btn:
    if not prompt.strip():
        st.warning("Type a prompt first.")
    else:
        with st.spinner("Generating image — this can take 20–60 seconds..."):
            img = generate_image(prompt)
            if img:
                st.image(img, use_column_width=True)
                # download button
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                st.download_button("Download image (PNG)", data=byte_im, file_name="generated.png", mime="image/png")
