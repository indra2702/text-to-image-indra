# app.py
import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Text → Image (mini DALL·E)", layout="wide")
st.title("🎨 Text → Image (mini DALL·E)")
st.markdown("Enter a prompt and generate an image (model runs on Hugging Face Inference API).")

# Use the Stability model (public)
MODEL_ID = "stabilityai/stable-diffusion-2-1"

# Read Hugging Face token from Streamlit Secrets
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    HF_TOKEN = None

if not HF_TOKEN:
    st.warning("No Hugging Face token found. Add HF_TOKEN in Streamlit Secrets (Manage app → Secrets).")
    st.stop()

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt: str):
    payload = {"inputs": prompt}
    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    except Exception as e:
        st.error(f"Network error when calling model: {e}")
        return None

    if resp.status_code == 200:
        return Image.open(io.BytesIO(resp.content))
    else:
        # show helpful error message
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        st.error(f"Generation failed — status {resp.status_code}. Response: {err}")
        return None

prompt = st.text_area("Describe the image (example: 'A cozy tea shop at night, warm lights')", height=120)
col1, col2 = st.columns([1,3])
with col1:
    if st.button("Generate image"):
        if not prompt.strip():
            st.warning("Type a prompt first.")
        else:
            with st.spinner("Generating image — this can take 20–60 seconds..."):
                img = generate_image(prompt)
                if img:
                    st.image(img, use_column_width=True)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("Download image (PNG)", data=buf.getvalue(), file_name="generated.png", mime="image/png")
with col2:
    st.info("Tip: be specific (styles, camera, mood). Example: 'Cinematic portrait of a samurai, dramatic lighting, 35mm film'")
