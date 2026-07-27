import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 1. Konfiguracja strony
st.set_page_config(page_title="Manufaktura - Degustacja", layout="centered", initial_sidebar_state="collapsed")

# 2. Zaawansowany CSS
st.markdown("""
<style>
    /* Tło - bardzo ciemny, ciepły antracyt idealnie komponujący się z drewnem z banera */
    .stApp {
        background: linear-gradient(135deg, #181818 0%, #222222 100%);
    }
    
    /* Wymuszenie jasnego koloru tekstu dla pełnej czytelności */
    p, label, span, div[data-baseweb="radio"], .st-emotion-cache-1629p8f {
        color: #f1f2f6 !important;
    }
    
    /* Jasne nagłówki */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Ukrycie domyślnego nagłówka Streamlit */
    header {visibility: hidden;}
    
    /* Zaokrąglenie rogów i dodanie cienia do głównego banera (zdjęcia) */
    img[data-testid="stImage"] {
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    
    /* Półprzezroczyste karty dla sekcji (Glassmorphism) */
    .block-container {
        padding-top: 2rem;
    }
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }
    
    /* Animacje Hover dla kart */
    div[data-testid="stVerticalBlock"] > div:hover {
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.15);
    }
    
    /* Przycisk wysyłania (Glow) */
    button[kind="primary"] {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: white !important;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    button[kind="primary"]:hover {
        box-shadow: 0 0 15px rgba(75, 108, 183, 0.6);
        border-color: rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# 3. Konfiguracja połączenia z Arkuszem Google
ID_ARKUSZA = "1Ze654cGGS7qVwYRXhJjM8_Tj3oEBCUaFfDEWnkktdS4"

@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

client = init_connection()

# 4. Pobieranie bazy pytań (Odświeżanie co 60 sekund)
@st.cache_data(ttl=60)
def pobierz_pytania():
    sheet = client.open_by_key(ID_ARKUSZA).worksheet("Baza_Pytan")
    return pd.DataFrame(sheet.get_all_records())

# 5. Interfejs Aplikacji

# Główny baner ze zdjęciem na samej górze
st.image("manu1.png", use_container_width=True)

st.title("🌭 Panel Degustacyjny")
st.markdown("Oceń szczerze, to pomoże nam dopracować recepturę!")

probka = st.radio("Którą próbkę oceniasz?", ("Próbka A", "Próbka B", "Próbka C"), horizontal=True)

try:
    # Wczytujemy strukturę pytań z Arkusza
    pytania_df = pobierz_pytania()
    odpowiedzi_usera = []
    
    st.header("Ocena parametrów")
    
    # Automatyczne generowanie suwaków
    for index, row in pytania_df.iterrows():
        min_val = int(row.get('Min_Wartosc', 1))
        max_val = int(row.get('Max_Wartosc', 5))
        
        wartosc = st.slider(
            label=str(row.get('Tresc_Pytania', 'Pytanie bez nazwy')),
            min_value=min_val,
            max_value=max_val,
            value=min_val + (max_val - min_val) // 2,
            help=str(row.get('Opis_Pomocniczy', ''))
        )
        odpowiedzi_usera.append(wartosc)

    st.header("Podsumowanie")
    komentarz = st.text_area("Co byś zmienił/a? (Opcjonalnie)")

    # 6. Zapisywanie danych
    if st.button("Wyślij ocenę 🚀", type="primary", use_container_width=True):
        with st.spinner("Zapisywanie w chmurze..."):
            nowy_wiersz = [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                probka
            ] + odpowiedzi_usera + [komentarz]

            sheet_odpowiedzi = client.open_by_key(ID_ARKUSZA).worksheet("Odpowiedzi")
            sheet_odpowiedzi.append_row(nowy_wiersz)
            
        st.success("Dane zapisane! Możesz popić wodą i wziąć kolejny kawałek.")

except Exception as e:
    st.error(f"Nie udało się połączyć z arkuszem lub wczytać pytań. Błąd: {e}")
