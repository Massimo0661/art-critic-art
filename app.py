import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from pillow_heif import register_heif_opener
import io
import gc

# 1. SETUP: TOLTO "layout=wide" PER COMPATIBILITÀ ANDROID
register_heif_opener()
st.set_page_config(page_title="Art AI by MartaG", page_icon="📷") # Default layout (Centered)

# --- CONFIGURAZIONE ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API Key!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
# Usiamo Gemini 2.0 per la velocità
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei una guida museale. Analizza l'opera.
Risposta breve per audio (max 150 parole).
1. Titolo/Autore/Anno.
2. Dettaglio tecnico.
3. Analisi materica
4. Analisi tecnica pittorica: pennellata, luci e colori
5. Aneddoti e curiosità
Tono: Coinvolgente.
"""

st.title("📷 Art Critic by MartaG")

# --- MEMORIA ---
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None
if 'last_input' not in st.session_state:
    st.session_state['last_input'] = None

# --- FUNZIONE DI ANALISI UNICA ---
def analizza_immagine(image_input, source_type):
    # Se è una nuova foto, procediamo
    if image_input and image_input.name != st.session_state['last_input']:
        st.session_state['last_input'] = image_input.name
        st.session_state['audio_fatto'] = None
        
        with st.status("🧠 Analisi in corso...", expanded=True) as status:
            try:
                img = Image.open(image_input)
                # Se arriva da file nativo, convertiamo per sicurezza
                if source_type == "file":
                    img = img.convert('RGB')
                    img.thumbnail((1024, 1024))
                
                # AI
                st.write("👀 Guardo l'opera...")
                response = model.generate_content([system_prompt, img])
                
                # Audio
                st.write("🗣️ Preparo la voce...")
                clean_text = response.text.replace("*", "").replace("#", "")
                if clean_text:
                    tts = gTTS(text=clean_text, lang='it')
                    mp3_fp = io.BytesIO()
                    tts.write_to_fp(mp3_fp)
                    st.session_state['audio_fatto'] = mp3_fp
                
                status.update(label="Fatto!", state="complete", expanded=False)
                gc.collect()
                
            except Exception as e:
                st.error(f"Errore: {e}")
                status.update(label="Errore", state="error")

# --- INTERFACCIA DOPPIA (LIVE + NATIVA) ---

st.write("### Opzione 1: Live Cam")
# 1. PROVIAMO A MOSTRARE LA LIVE CAM
cam_input = st.camera_input("Scatta Live", label_visibility="collapsed")

if cam_input:
    analizza_immagine(cam_input, "live")

st.divider()

st.write("### Opzione 2: Fotocamera Nativa")
st.caption("Se l'Opzione 1 non appare, usa questo pulsante:")

# 2. PULSANTE DI RISERVA (Diretto alla fotocamera)
file_input = st.file_uploader("📸 APRI FOTOCAMERA", type=['jpg','png','jpeg','heic'], label_visibility="collapsed")

if file_input:
    analizza_immagine(file_input, "file")

# --- RISULTATO ---
if st.session_state['audio_fatto']:
    st.success("Ascolta la guida:")
    st.audio(st.session_state['audio_fatto'], format='audio/mp3', autoplay=True)


