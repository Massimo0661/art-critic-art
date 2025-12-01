import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from pillow_heif import register_heif_opener
import io

# 1. FIX FORMATI
register_heif_opener()

# --- CONFIGURAZIONE ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API Key!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine.
Sii sintetico (max 80 parole).
1. Autore/Titolo/Anno (se noti).
2. Tecnica/Stile/Luce/Colore.
3. Significato breve.
4. Aneddoti e curiosità.
"""

st.title("🏛️ Art Critic AI by MartaG")

# --- GESTIONE MEMORIA & RESET ---
# Creiamo una "chiave" univoca per il caricatore di file
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0

if 'analisi_fatta' not in st.session_state:
    st.session_state['analisi_fatta'] = None
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None

# --- MENU ---
opzione = st.radio("Modalità:", ["Carica Foto", "Webcam"])
img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta ora")
else:
    # NOTA: key=... serve per poter resettare questo campo col bottone in fondo
    img_file = st.file_uploader(
        "Premi qui", 
        type=['png', 'jpg', 'jpeg', 'heic', 'webp'], 
        key=f"uploader_{st.session_state['uploader_key']}"
    )

# --- ELABORAZIONE ---
if img_file is not None:
    try:
        image = Image.open(img_file)
        image = image.convert('RGB')
        image.thumbnail((1024, 1024))
        
        st.image(image, caption="Opera pronta", use_container_width=True)
        
        if st.button("✨ Analizza Opera"):
            with st.spinner('Analisi in corso...'):
                try:
                    # Chiamata AI
                    response = model.generate_content([system_prompt, image])
                    testo_originale = response.text
                    
                    # Salviamo il risultato scritto (con grassetti belli da vedere)
                    st.session_state['analisi_fatta'] = testo_originale
                    
                    # PULIZIA PER AUDIO: Rimuoviamo * e # per la voce
                    testo_pulito = testo_originale.replace("*", "").replace("#", "")
                    
                    if testo_pulito:
                        tts = gTTS(text=testo_pulito, lang='it')
                        mp3_fp = io.BytesIO()
                        tts.write_to_fp(mp3_fp)
                        st.session_state['audio_fatto'] = mp3_fp
                        
                except Exception as e:
                    st.error(f"Errore Gemini: {e}")

    except Exception as e:
        st.error(f"Errore file: {e}")

# --- RISULTATI ---
if st.session_state['analisi_fatta']:
    st.markdown("### 🎙️ Risultato:")
    st.write(st.session_state['analisi_fatta'])
    
    if st.session_state['audio_fatto']:
        st.audio(st.session_state['audio_fatto'], format='audio/mp3')
        
    st.divider() # Una linea divisoria elegante
    
    # TASTO RESET VERO
    if st.button("🔄 Nuova Analisi (Resetta Tutto)"):
        # 1. Cancelliamo i risultati
        st.session_state['analisi_fatta'] = None
        st.session_state['audio_fatto'] = None
        # 2. Incrementiamo la chiave per forzare lo svuotamento del caricatore foto
        st.session_state['uploader_key'] += 1
        # 3. Ricarichiamo la pagina
        st.rerun()
