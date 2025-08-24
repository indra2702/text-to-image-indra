import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Text → Image Generator", layout="wide")
st.title("🎨 Text → Image (mini DALL·E)")
st.markdown("Enter a prompt and generate an image (powered by Hugging Face API).")

MODEL_ID = "runwayml/stable-diffusion-v1-5"

try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    HF_TOKEN = None

if not HF_TOKEN:
    st.warning("No Hugging Face token found. Add HF_TOKEN in Streamlit Secrets.")
    st.stop()

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt: str):
    payload = {"inputs": prompt}
    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    if resp.status_code == 200:
        return Image.open(io.BytesIO(resp.content))
    else:
        st.error(f"Error {resp.status_code}: {resp.text}")
        return None

prompt = st.text_area("Describe the image:", height=120)
if st.button("Generate"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Generating... (30–60s)"):
            img = generate_image(prompt)
            if img:
                st.image(img, use_column_width=True)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("Download image", buf.getvalue(), "image.png", "image/png")
