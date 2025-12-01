import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from pillow_heif import register_heif_opener
import io
import gc # <--- NUOVO: Lo spazzino della memoria RAM

# 1. SETUP
register_heif_opener()
st.set_page_config(page_title="Art Critic AI", page_icon="🎨")

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
1. Autore/Titolo.
2. Tecnica.
3. Significato.
"""

st.title("🏛️ Art Critic AI")

# --- FUNZIONI DI PULIZIA (LO SPAZZINO) ---
def reset_dati():
    """Questa funzione parte APPENA tocchi il caricatore di file"""
    st.session_state['analisi_fatta'] = None
    st.session_state['audio_fatto'] = None
    # Forza la pulizia della RAM del telefono
    gc.collect()

# --- MEMORIA ---
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0
if 'analisi_fatta' not in st.session_state:
    st.session_state['analisi_fatta'] = None
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None

# --- MENU ---
st.caption("📸 Modalità Mobile Ottimizzata")
opzione = st.radio("Scegli:", ["Carica Foto", "Webcam"], horizontal=True, on_change=reset_dati)

img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta", on_change=reset_dati)
else:
    # Uploader con AUTO-RESET
    # on_change=reset_dati significa: "Se cambi file, cancella i vecchi risultati subito"
    img_file = st.file_uploader(
        "Scegli immagine", 
        type=['png', 'jpg', 'jpeg', 'heic', 'webp'], 
        key=f"uploader_{st.session_state['uploader_key']}",
        on_change=reset_dati 
    )

# --- ELABORAZIONE ---
if img_file is not None:
    # Se c'è un file ma NON c'è ancora un'analisi, mostriamo l'anteprima
    if st.session_state['analisi_fatta'] is None:
        
        with st.status("Caricamento...", expanded=True) as status:
            try:
                image = Image.open(img_file)
                image = image.convert('RGB')
                
                # Ridimensionamento aggressivo per non bloccare la seconda foto
                image.thumbnail((800, 800))
                
                st.image(image, caption="Immagine pronta", use_container_width=True)
                status.update(label="Pronto!", state="complete", expanded=False)
                
                # BOTTONE ANALISI
                if st.button("✨ Analizza Ora", type="primary"):
                    with st.spinner('Analisi...'):
                        # Chiamata AI
                        response = model.generate_content([system_prompt, image])
                        testo = response.text
                        st.session_state['analisi_fatta'] = testo
                        
                        # Audio
                        clean = testo.replace("*", "").replace("#", "")
                        if clean:
                            tts = gTTS(text=clean, lang='it')
                            mp3_fp = io.BytesIO()
                            tts.write_to_fp(mp3_fp)
                            st.session_state['audio_fatto'] = mp3_fp
                        
                        # Ricarica la pagina per mostrare i risultati puliti
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Errore file: {e}")
                status.update(label="Errore", state="error")

# --- MOSTRA RISULTATI (SOLO SE C'È ANALISI) ---
else:
    # Se img_file è None (cioè l'utente ha cancellato la foto con la X), puliamo tutto
    if st.session_state['analisi_fatta'] is not None:
        reset_dati()
        st.rerun()

if st.session_state['analisi_fatta']:
    st.success("Fatto!")
    st.write(st.session_state['analisi_fatta'])
    
    if st.session_state['audio_fatto']:
        st.audio(st.session_state['audio_fatto'], format='audio/mp3')
    
    st.divider()
    
    # Tasto per forzare la prossima foto
    def prossima_foto():
        st.session_state['uploader_key'] += 1
        reset_dati()
    
    st.button("🔄 Prossima Foto", on_click=prossima_foto, type="primary")
