import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os

# --- CONFIGURAZIONE ---
# Assicurati che la chiave sia tra le virgolette
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

# Usiamo il modello che abbiamo verificato funzionare
model = genai.GenerativeModel('gemini-2.0-flash')

# --- PROMPT OTTIMIZZATO ---
system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine fornita.
STRUTTURA RISPOSTA (Massimo 100 parole per l'audio):
1. Titolo e Autore (se chiari).
2. Analisi tecnica breve (luce, materia).
3. Perché è rilevante.

Tono: Caldo, narrativo, non robotico.
"""

st.title("🏛️ Art Critic AI (Audio)")

img_file = st.camera_input("Scatta una foto")

if img_file is not None:
    image = Image.open(img_file)
    
    with st.spinner('Analisi in corso...'):
        try:
            # 1. Chiediamo a Gemini
            response = model.generate_content([system_prompt, image])
            
            # 2. Assegniamo il testo a una variabile
            testo_critico = response.text
            
            # 3. Mostriamo il testo a schermo
            st.markdown("### 🧐 L'Esperto dice:")
            st.write(testo_critico)
            
            # 4. Generiamo l'audio SOLO se abbiamo il testo
            if testo_critico:
                tts = gTTS(text=testo_critico, lang='it')
                tts.save("spiegazione.mp3")
                st.audio("spiegazione.mp3")
            
        except ValueError:
            # Questo errore scatta se Gemini blocca l'immagine (es. nudo artistico)
            st.error("⚠️ L'IA ha bloccato la risposta per motivi di sicurezza (filtro contenuti). Prova con un'altra opera.")
            
        except Exception as e:
            # Altri errori generici
            st.error(f"Errore tecnico: {e}")