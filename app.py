import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps # <--- NUOVO: ImageOps per la rotazione sicura
from gtts import gTTS
from pillow_heif import register_heif_opener
import io
import gc

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
# Usiamo il modello Flash (più leggero e veloce)
model = genai.GenerativeModel('gemini-1.5-flash')

system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine.
Sii sintetico (max 80 parole).
1. Autore/Titolo.
2. Tecnica.
3. Significato.
"""

st.title("🏛️ Art Critic AI")

# --- FUNZIONI DI PULIZIA ---
def reset_dati():
    st.session_state['analisi_fatta'] = None
    st.session_state['audio_fatto'] = None
    gc.collect()

# --- MEMORIA ---
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0
if 'analisi_fatta' not in st.session_state:
    st.session_state['analisi_fatta'] = None
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None

# --- MENU ---
st.caption("📸 Carica la foto del quadro (attendi il caricamento completo)")
opzione = st.radio("Scegli:", ["Carica Foto", "Webcam"], horizontal=True, on_change=reset_dati)

img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta", on_change=reset_dati)
else:
    # Uploader
    img_file = st.file_uploader(
        "Scegli immagine", 
        type=['png', 'jpg', 'jpeg', 'heic', 'webp'], 
        key=f"uploader_{st.session_state['uploader_key']}",
        on_change=reset_dati 
    )

# --- ELABORAZIONE SICURA ---
if img_file is not None:
    if st.session_state['analisi_fatta'] is None:
        
        # STATUS BAR PER FEEDBACK VISIVO
        with st.status("Elaborazione immagine pesante...", expanded=True) as status:
            try:
                # 1. Caricamento "Lazy" (apre solo i metadati prima)
                image = Image.open(img_file)
                st.write("📖 Lettura file completata...")
                
                # 2. FIX ROTAZIONE (Cruciale per il Monet orizzontale)
                # Questo evita che la foto venga caricata storta o crashi nel raddrizzarla
                image = ImageOps.exif_transpose(image)
                
                # 3. CONVERSIONE E RIDUZIONE
                image = image.convert('RGB')
                
                # Riduciamo drasticamente prima di mostrarla
                # Max 800px è più che sufficiente per l'AI
                image.thumbnail((800, 800))
                st.write("📉 Ottimizzazione completata.")
                
                status.update(label="Immagine Pronta!", state="complete", expanded=False)
                
                # Mostra immagine
                st.image(image, caption="Opera pronta", use_container_width=True)
                
                # BOTTONE ANALISI
                if st.button("✨ Analizza Ora", type="primary"):
                    with st.spinner('Analisi...'):
                        
                        response = model.generate_content([system_prompt, image])
                        testo = response.text
                        st.session_state['analisi_fatta'] = testo
                        
                        clean = testo.replace("*", "").replace("#", "")
                        if clean:
                            tts = gTTS(text=clean, lang='it')
                            mp3_fp = io.BytesIO()
                            tts.write_to_fp(mp3_fp)
                            st.session_state['audio_fatto'] = mp3_fp
                        
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Errore lettura: {e}")
                st.warning("Prova a fare uno screenshot della foto e caricare quello.")
                status.update(label="Errore", state="error")

else:
    if st.session_state['analisi_fatta'] is not None:
        reset_dati()
        st.rerun()

# --- RISULTATI ---
if st.session_state['analisi_fatta']:
    st.success("Analisi completata!")
    st.write(st.session_state['analisi_fatta'])
    
    if st.session_state['audio_fatto']:
        st.audio(st.session_state['audio_fatto'], format='audio/mp3')
    
    st.divider()
    
    def prossima_foto():
        st.session_state['uploader_key'] += 1
        reset_dati()
    
    st.button("🔄 Prossima Foto", on_click=prossima_foto, type="primary")
