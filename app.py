import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os

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
2. Dettaglio tecnico: pennellata, luci, colori
3. Significato.
4. Aneddoti e curiosità
"""

st.title("🏛️ Art Critic AI (Mobile Fix)")

# --- MENU ---
opzione = st.radio("Modalità:", ["Carica/Scatta", "Webcam"])

img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta ora")
else:
    # 1. MODIFICA FONDAMENTALE: Abbiamo tolto "type=['jpg']"
    # Ora accetta tutto, anche HEIC se il telefono lo converte, o altri formati.
    img_file = st.file_uploader("Premi qui per Foto", accept_multiple_files=False)

# --- DEBUG & ELABORAZIONE ---
if img_file is not None:
    # Feedback visivo immediato
    st.success("File ricevuto! Elaborazione in corso...")
    
    try:
        # 2. MODIFICA FONDAMENTALE: Apriamo e RIDIMENSIONIAMO subito
        image = Image.open(img_file)
        
        # Ridimensiona l'immagine (max 1024px) per renderla leggera e veloce
        image.thumbnail((1024, 1024)) 
        
        st.image(image, caption="Immagine pronta", use_container_width=True)
        
        # Bottone Analisi
        if st.button("✨ Analizza Ora"):
            with st.spinner('Il critico sta pensando...'):
                
                # Chiamata AI
                response = model.generate_content([system_prompt, image])
                testo = response.text
                
                st.markdown("### 🎙️ Risultato:")
                st.write(testo)
                
                if testo:
                    tts = gTTS(text=testo, lang='it')
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                    
    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
else:
    if opzione != "Webcam":
        st.info("👆 Carica una foto per iniziare")
