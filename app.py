import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from pillow_heif import register_heif_opener
import io

# 1. FIX FORMATI CELLULARE
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

# --- GESTIONE DELLA MEMORIA (SESSION STATE) ---
# Se non esiste una memoria per l'analisi, la creiamo
if 'analisi_fatta' not in st.session_state:
    st.session_state['analisi_fatta'] = None
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None

# --- MENU ---
st.info("💡 Consiglio su Mobile: Usa 'Carica Foto' -> 'Scatta' per salvare la foto in galleria.")
opzione = st.radio("Modalità:", ["Carica Foto (Consigliata)", "Webcam"])
img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta ora")
else:
    # Accetta tutto
    img_file = st.file_uploader("Premi qui", type=['png', 'jpg', 'jpeg', 'heic', 'webp'])

# --- LOGICA BLINDATA ---
if img_file is not None:
    # Appena arriva un file, proviamo a elaborarlo
    try:
        image = Image.open(img_file)
        image = image.convert('RGB')
        image.thumbnail((1024, 1024))
        
        st.image(image, caption="Opera pronta", use_container_width=True)
        
        # Bottone per analizzare
        if st.button("✨ Analizza Opera"):
            with st.spinner('Analisi in corso...'):
                try:
                    # Chiamata AI
                    response = model.generate_content([system_prompt, image])
                    st.session_state['analisi_fatta'] = response.text
                    
                    # Generazione Audio
                    if response.text:
                        tts = gTTS(text=response.text, lang='it')
                        # Salviamo in un buffer di memoria invece che su file (più stabile su mobile)
                        mp3_fp = io.BytesIO()
                        tts.write_to_fp(mp3_fp)
                        st.session_state['audio_fatto'] = mp3_fp
                        
                except Exception as e:
                    st.error(f"Errore Gemini: {e}")

    except Exception as e:
        st.error(f"Errore lettura file: {e}")

# --- MOSTRA I RISULTATI DALLA MEMORIA ---
# Questo blocco è fuori dagli IF, così se la pagina si ricarica, i risultati restano!
if st.session_state['analisi_fatta']:
    st.markdown("### 🎙️ Risultato:")
    st.write(st.session_state['analisi_fatta'])
    
    if st.session_state['audio_fatto']:
        st.audio(st.session_state['audio_fatto'], format='audio/mp3')
        
    # Tasto per ricominciare
    if st.button("🔄 Nuova Analisi"):
        st.session_state['analisi_fatta'] = None
        st.session_state['audio_fatto'] = None
        st.rerun()
