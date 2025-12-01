import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os

# --- CONFIGURAZIONE ---
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine fornita.
STRUTTURA RISPOSTA (Massimo 100 parole per l'audio):
1. Titolo e Autore (se chiari).
2. Analisi tecnica breve.
3. Analisi della luce e del colore
4. Perché è rilevante.
5. Aneddoti e curiosità
Tono: Caldo, narrativo.
"""

st.title("🏛️ Art Critic AI")

# MENU SCELTA
opzione = st.radio("Modalità:", ["Carica/Scatta (Alta Qualità)", "Webcam (Rapida)"])

img_file = None

if opzione == "Webcam (Rapida)":
    img_file = st.camera_input("Scatta ora")
else:
    # Qui accettiamo file da galleria o fotocamera nativa
    img_file = st.file_uploader("Carica foto", type=['jpg', 'jpeg', 'png'])

# --- ELABORAZIONE ---
if img_file is not None:
    # 1. Carichiamo l'immagine
    image = Image.open(img_file)
    
    # Mostriamo SUBITO l'immagine per confermare che l'upload è finito
    st.image(image, caption="Immagine acquisita", use_container_width=True)
    
    # 2. Bottone per far partire l'AI (Così hai il controllo totale)
    if st.button("✨ Analizza Opera"):
        
        with st.spinner('Analisi in corso... attendi la voce...'):
            try:
                # Chiamata AI
                response = model.generate_content([system_prompt, image])
                testo_critico = response.text
                
                # Testo
                st.markdown("### 🧐 L'Esperto dice:")
                st.write(testo_critico)
                
                # Audio
                if testo_critico:
                    tts = gTTS(text=testo_critico, lang='it')
                    tts.save("spiegazione.mp3")
                    st.audio("spiegazione.mp3")
                
            except Exception as e:
                st.error(f"Errore: {e}")
