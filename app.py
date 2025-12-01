import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from pillow_heif import register_heif_opener
import io

# 1. ABILITIAMO I FORMATI IPHONE (HEIC)
register_heif_opener()

# --- CONFIGURAZIONE ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API Key nei Secrets!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Usiamo il modello 2.0 Flash che hai verificato funzionare
model = genai.GenerativeModel('gemini-2.0-flash')

system_prompt = """
Sei un esperto Storico dell'Arte. Analizza l'immagine.
Sii sintetico (max 80 parole).
1. Autore/Titolo (se noti).
2. Tecnica/Stile.
3. Significato breve.
"""

st.title("🏛️ Art Critic AI")

# --- INIZIALIZZAZIONE MEMORIA ---
# Serve per non perdere i dati se il telefono ricarica la pagina
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0
if 'analisi_fatta' not in st.session_state:
    st.session_state['analisi_fatta'] = None
if 'audio_fatto' not in st.session_state:
    st.session_state['audio_fatto'] = None

# --- MENU DI SCELTA ---
opzione = st.radio("Modalità:", ["Carica Foto (Galleria)", "Webcam"])
img_file = None

if opzione == "Webcam":
    img_file = st.camera_input("Scatta ora")
else:
    # Key dinamica per permettere il reset
    img_file = st.file_uploader(
        "Scegli immagine", 
        type=['png', 'jpg', 'jpeg', 'heic', 'webp'], 
        key=f"uploader_{st.session_state['uploader_key']}"
    )

# --- ELABORAZIONE INTELLIGENTE ---
if img_file is not None:
    try:
        # Se c'è già un'analisi in memoria per questa sessione, non ricalcoliamo
        # (A meno che l'utente non carichi un nuovo file, ma qui semplifichiamo)
        
        # 1. Feedback visivo immediato per file pesanti
        with st.spinner('Ottimizzazione immagine in corso...'):
            image = Image.open(img_file)
            image = image.convert('RGB') # Corregge colori e formati strani
            
            # 2. IL TRUCCO SALVA-MEMORIA: Ridimensioniamo subito!
            # Da 9MB passa a pochi KB. 800px bastano e avanzano per l'AI.
            image.thumbnail((800, 800)) 
            
            st.image(image, caption="Opera acquisita (Ottimizzata)", use_container_width=True)
        
        # Bottone Analisi
        if st.button("✨ Analizza Opera"):
            with st.spinner('Il critico sta osservando...'):
                try:
                    # Chiamata AI
                    response = model.generate_content([system_prompt, image])
                    testo_originale = response.text
                    
                    # Salviamo in memoria
                    st.session_state['analisi_fatta'] = testo_originale
                    
                    # Pulizia testo per Audio (Via gli asterischi)
                    testo_pulito = testo_originale.replace("*", "").replace("#", "")
                    
                    if testo_pulito:
                        tts = gTTS(text=testo_pulito, lang='it')
                        # Salviamo in RAM (BytesIO) invece che su disco
                        mp3_fp = io.BytesIO()
                        tts.write_to_fp(mp3_fp)
                        st.session_state['audio_fatto'] = mp3_fp
                        
                except Exception as e:
                    st.error(f"Errore Gemini: {e}")

    except Exception as e:
        st.error(f"Errore lettura file: {e}")

# --- MOSTRA RISULTATI (Persistenti) ---
if st.session_state['analisi_fatta']:
    st.success("Analisi completata!")
    
    st.markdown("### 🎙️ Risultato:")
    st.write(st.session_state['analisi_fatta'])
    
    if st.session_state['audio_fatto']:
        st.audio(st.session_state['audio_fatto'], format='audio/mp3')
    
    st.divider()
    
    # --- TASTO RESET VERO ---
    def reset_app():
        # Svuota le variabili
        st.session_state['analisi_fatta']
