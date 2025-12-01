import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os

# --- CONFIGURAZIONE ---
# La chiave viene presa dai Secrets di Streamlit
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- PROMPT ---
system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine fornita.
STRUTTURA RISPOSTA (Massimo 100 parole per l'audio):
1. Titolo e Autore (se chiari).
2. Analisi tecnica breve (luce, materia).
4. Stile pittorico
5. Perché è rilevante.
6. Aneddoti e curiosità

Tono: Caldo, narrativo, non robotico.
"""

# --- INTERFACCIA ---
st.title("🏛️ Art Critic AI")

# MENU DI SCELTA (Radio Button)
opzione = st.radio("Scegli modalità:", ["Carica/Scatta (Alta Qualità)", "Webcam (Rapida)"])

img_file = None

# LOGICA DI SCELTA
if opzione == "Webcam (Rapida)":
    # Opzione 1: Webcam del browser
    img_file = st.camera_input("Scatta ora")
else:
    # Opzione 2: Fotocamera nativa o Galleria
    img_file = st.file_uploader("Carica o Scatta", type=['jpg', 'jpeg', 'png'])

# --- ELABORAZIONE (Questa riga deve essere attaccata al margine sinistro!) ---
if img_file is not None:
    image = Image.open(img_file)
    
    # Mostra l'immagine se caricata da file (la webcam la mostra già da sola)
    if opzione != "Webcam (Rapida)":
        st.image(image, caption="Opera caricata", use_container_width=True)
    
    with st.spinner('Il critico sta osservando...'):
        try:
            # 1. Chiediamo a Gemini
            response = model.generate_content([system_prompt, image])
            testo_critico = response.text
            
            # 2. Mostriamo il testo
            st.markdown("### 🧐 L'Esperto dice:")
            st.write(testo_critico)
            
            # 3. Generiamo l'audio
            if testo_critico:
                tts = gTTS(text=testo_critico, lang='it')
                tts.save("spiegazione.mp3")
                st.audio("spiegazione.mp3")
            
        except ValueError:
            st.error("⚠️ Immagine bloccata dai filtri di sicurezza.")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
