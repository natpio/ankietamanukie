import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.set_page_config(page_title="Manufaktura - Degustacja", layout="centered", initial_sidebar_state="collapsed")

# Zaawansowany CSS - Motyw Grafit/Marmur + Glassmorphism
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d3238 100%);
        color: #f1f2f6;
    }
    header {visibility: hidden;}
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
    div[data-testid="stVerticalBlock"] > div:hover {
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(255, 255, 255, 0.15);
    }
    button[kind="primary"] {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 0 15px rgba(75, 108, 183, 0.6);
        border-color: rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- KONFIGURACJA GOOGLE SHEETS ---
ID_ARKUSZA = "1Ze654cGGS7qVwYRXhJjM8_Tj3oEBCUaFfDEWnkktdS4"

@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Ścieżka do sekretów (musi być skonfigurowana w Streamlit Cloud lub lokalnie w .streamlit/secrets.toml)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

client = init_connection()

@st.cache_data(ttl=60) # Odświeża bazę pytań co 60 sekund
def pobierz_pytania():
    sheet = client.open_by_key(ID_ARKUSZA).worksheet("Baza_Pytan")
    return pd.DataFrame(sheet.get_all_records())

# --- INTERFEJS APLIKACJI ---
st.title("🌭 Panel Degustacyjny")
st.markdown("Oceń szczerze, to pomoże nam dopracować recepturę!")

probka = st.radio("Którą próbkę oceniasz?", ("Próbka A", "Próbka B", "Próbka C"), horizontal=True)

try:
    pytania_df = pobierz_pytania()
    odpowiedzi_usera = []
    
    st.header("Ocena parametrów")
    
    # Automatyczne generowanie suwaków na podstawie danych z Arkusza
    for index, row in pytania_df.iterrows():
        min_val = int(row.get('Min_Wartosc', 1))
        max_val = int(row.get('Max_Wartosc', 5))
        wartosc = st.slider(
            label=str(row.get('Tresc_Pytania', 'Pytanie')),
            min_value=min_val,
            max_value=max_val,
            value=min_val + (max_val - min_val) // 2, # Ustawia domyślnie na środek
            help=str(row.get('Opis_Pomocniczy', ''))
        )
        odpowiedzi_usera.append(wartosc)

    st.header("Podsumowanie")
    komentarz = st.text_area("Co byś zmienił/a? (Opcjonalnie)")

    if st.button("Wyślij ocenę 🚀", type="primary", use_container_width=True):
        # Budujemy wiersz do wysłania
        nowy_wiersz = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            probka
        ] + odpowiedzi_usera + [komentarz]

        # Zapis do Arkusza
        sheet_odpowiedzi = client.open_by_key(ID_ARKUSZA).worksheet("Odpowiedzi")
        sheet_odpowiedzi.append_row(nowy_wiersz)
        
        st.success("Dane zapisane! Możesz popić wodą i wziąć kolejny kawałek.")

except Exception as e:
    st.error(f"Nie udało się połączyć z arkuszem lub wczytać pytań. Błąd: {e}")
