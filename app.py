import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import io
import gc

# 1. SETUP PAGINA (Layout "Wide" per massimizzare la fotocamera)
st.set_page_config(page_title="Art AI Live", page_icon="📷", layout="wide")

# --- CONFIGURAZIONE ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API Key!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# --- MOTORE: GEMINI 2.0 FLASH (Il più veloce in assoluto) ---
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei una guida museale esperta. 
Analizza l'opera inquadrata.
Risposta breve per audio (max 50 parole).
1. Titolo/Autore (se riconosciuti).
2. Un dettaglio tecnico affascinante.
Tono: Coinvolgente, veloce.
"""

st.title("📷 Art Critic (Live 2.0)")
st.caption("💡 Suggerimento: Gira il telefono in orizzontale ↔️ per inquadrare meglio il quadro.")

# --- MEMORIA DI SESSIONE ---
# Serve per ricordare l'ultima foto fatta e non rianalizzarla se la pagina fa refresh
if 'last_photo_id' not in st.session_state:
    st.session_state['last_photo_id'] = None
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None

# --- FOTOCAMERA ---
# label_visibility="collapsed
