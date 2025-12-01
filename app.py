import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from pillow_heif import register_heif_opener
import io
import time

# 1. SETUP INIZIALE
register_heif_opener()
st.set_page_config(page_title="Art Critic AI", page_icon="🎨")

# --- CONFIGURAZIONE CHIAVE ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine.
Sii sintetico (max 80 parole).
1. Autore/Titolo.
2. Tecnica.
3. Significato.
"""

st.title("🏛️ Art Critic AI")

# --- MEMORIA DI SESSIONE ---
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0
if 'analisi_fatta' not in st.session_state:
    st.session_state['analisi_fatta'] = None
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None

# --- MENU ---
st.info("📸 Se il file è grande (>5MB), il caricamento richiederà qualche secondo. Attendi la barra blu in alto.")
opzione = st.radio("Modalità:", ["Carica Foto (Galleria)", "Webcam"])
img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta ora")
else:
    # Uploader
    img_file = st.file_uploader(
        "Scegli immagine", 
        type=['png', 'jpg', 'jpeg', 'heic', 'webp'], 
        key=f"uploader_{st.session_state['uploader_key']}"
    )

# --- ELABORAZIONE CON STATUS ---
if img_file is not None:
    
    # BOX DI STATO: Questo ti dice cosa sta succedendo!
    with st.status("Elaborazione in corso...", expanded=True) as status:
        
        try:
            # 1. Controllo Dimensione
            size_mb = img_file.size / (1024 * 1024)
            st.write(f"📥 File ricevuto: {size_mb:.1f} MB")
            
            if size_mb > 5:
                st.warning("⚠️ File pesante! Ottimizzazione aggressiva in corso...")
            
            # 2. Apertura e Ridimensionamento
            st.write("🔧 Apertura e conversione...")
            image = Image.open(img_file)
            image = image.convert('RGB')
            
            st.write("📉 Ridimensionamento per risparmio memoria...")
            image.thumbnail((800, 800))
            
            status.update(label="Immagine pronta!", state="complete", expanded=False)
            
            # Mostra immagine
            st.image(image, caption="Opera pronta per l'analisi", use_container_width=True)
            
            # BOTTONE ANALISI
            if st.button("✨ Chiedi al Critico", type="primary"):
                
                with st.spinner('Il critico sta scrivendo...'):
                    # Chiamata AI
                    response = model.generate_content([system_prompt, image])
                    testo = response.text
                    st.session_state['analisi_fatta'] = testo
                    
                    # Audio
                    clean_text = testo.replace("*", "").replace("#", "")
                    if clean_text:
                        tts = gTTS(text=clean_text, lang='it')
                        mp3_fp = io.BytesIO()
                        tts.write_to_fp(mp3_fp)
                        st.session_state['audio_fatto'] = mp3_fp
            
        except Exception as e:
            st.error(f"Errore durante l'elaborazione: {e}")
            status.update(label="Errore!", state="error")

# --- RISULTATI ---
if st.session_state['analisi_fatta']:
    st.divider()
    st.success("Analisi completata")
    
    st.markdown("### 🎙️ L'Esperto dice:")
    st.write(st.session_state['analisi_fatta'])
    
    if st.session_state['audio_fatto']:
        st.audio(st.session_state['audio_fatto'], format='audio/mp3')
    
    # RESET
    def reset_app():
        st.session_state['analisi_fatta'] = None
        st.session_state['audio_fatto'] = None
        st.session_state['uploader_key'] += 1
    
    st.button("🔄 Nuova Analisi", on_click=reset_app)
