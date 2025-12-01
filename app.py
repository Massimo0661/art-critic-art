import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os

# --- NUOVO: Gestione Formato HEIC (iPhone/Android) ---
from pillow_heif import register_heif_opener
register_heif_opener() # <-- Questo comando insegna a Pillow a leggere gli HEIC

# --- CONFIGURAZIONE ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine fornita.
Sii sintetico (max 80 parole).
1. Cosa è (Autore/Titolo).
2. Dettaglio tecnico.
3. Significato.
"""

st.title("🏛️ Art Critic AI (HEIC Fix)")

# --- MENU ---
opzione = st.radio("Modalità:", ["Carica/Scatta", "Webcam"])
img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta ora")
else:
    img_file = st.file_uploader("Premi qui per Foto", accept_multiple_files=False)

# --- DEBUG & ELABORAZIONE ---
if img_file is not None:
    st.success("File ricevuto! Elaborazione in corso...")
    
    try:
        # ORA QUESTO FUNZIONERÀ ANCHE CON HEIC GRAZIE ALLA MODIFICA IN ALTO
        image = Image.open(img_file)
        
        # Ridimensiona
        image.thumbnail((1024, 1024)) 
        
        st.image(image, caption="Immagine pronta", use_container_width=True)
        
        # Bottone Analisi
        if st.button("✨ Analizza Ora"):
            with st.spinner('Il critico sta pensando...'):
                response = model.generate_content([system_prompt, image])
                testo = response.text
                st.markdown("### 🎙️ Risultato:")
                st.write(testo)
                if testo:
                    tts = gTTS(text=testo, lang='it')
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                    
    except Exception as e:
        # Se fallisce ancora, l'errore ci dirà esattamente perché
        st.error(f"Errore critico nella lettura: {e}")
else:
    if opzione != "Webcam":
        st.info("👆 Carica una foto per iniziare")
