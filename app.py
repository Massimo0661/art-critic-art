import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from pillow_heif import register_heif_opener
import io
import time

# 1. ABILITIAMO I FORMATI IPHONE (HEIC)
register_heif_opener()

# --- CONFIGURAZIONE ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API Key!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# --- MOTORE: TORNIAMO AL 2.0 CHE FUNZIONAVA ---
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine.
Sii sintetico (max 80 parole).
1. Autore/Titolo/anno (se noti).
2. Tecnica/Stile/Luce/Colori.
3. Significato breve.
4. Aneddoti e curiosità (se noti).
"""

st.title("🏛️ Art Critic AI by MartaG")

# --- MENU ---
opzione = st.radio("Modalità:", ["Carica Foto", "Webcam"])
img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta ora")
else:
    # Blocchiamo i video, accettiamo solo immagini
    img_file = st.file_uploader(
        "Scegli dalla Galleria", 
        type=['png', 'jpg', 'jpeg', 'heic', 'webp'], 
        accept_multiple_files=False
    )

# --- ELABORAZIONE ---
if img_file is not None:
    st.success("Immagine ricevuta. Analisi...")
    
    try:
        # Apriamo l'immagine
        image = Image.open(img_file)
        
        # Conversione forzata in RGB
        image = image.convert('RGB')
        
        # Ridimensioniamo (Importante per velocità e memoria)
        image.thumbnail((1024, 1024))
        
        st.image(image, caption="Opera acquisita", use_container_width=True)
        
        # Bottone manuale
        if st.button("✨ Analizza Opera"):
            with st.spinner('La critica sta osservando...'):
                
                try:
                    # Chiamata a Gemini
                    response = model.generate_content([system_prompt, image])
                    testo = response.text
                    
                    st.markdown("### 🎙️ Risultato:")
                    st.write(testo)
                    
                    # Audio
                    if testo:
                        tts = gTTS(text=testo, lang='it')
                        tts.save("audio.mp3")
                        st.audio("audio.mp3")

                except Exception as e:
                    # GESTIONE ERRORI
                    errore_str = str(e)
                    # Se Gemini 2.0 è stanco, lo diciamo in modo gentile
                    if "429" in errore_str or "Resource" in errore_str:
                        st.warning("⏳ Troppe richieste veloci! Il modello gratuito ha bisogno di una pausa. Aspetta 1 minuto.")
                    else:
                        st.error(f"Errore nell'analisi: {e}")
                    
    except Exception as e:
        st.error(f"Errore caricamento file (forse è un video?): {e}")

